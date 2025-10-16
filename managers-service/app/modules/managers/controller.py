from flask import request, jsonify, g
import re

from app.modules.managers.service import service
from app.modules.managers.repository import ManagerRepository
from app.config.database import db
from app.core.exceptions import ValidationError, ConflictError, NotFoundError
from app.core.auth.decorators import require_auth, require_permission
from app.modules.managers.models import Client


_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_PHONE_RE = re.compile(r"^[0-9+\-\s]+$")


def _validate_manager_payload(payload: dict):
    required = ['full_name', 'email', 'phone', 'identification']
    for f in required:
        if not payload.get(f):
            raise ValidationError(f'{f} is required')

    email = payload.get('email')
    if not _EMAIL_RE.match(email):
        raise ValidationError('invalid email format')

    phone = payload.get('phone')
    if not _PHONE_RE.match(phone):
        raise ValidationError('invalid phone format')


def create_manager_controller():
    payload = request.get_json() or {}
    operator = payload.get('operator')
    try:
        _validate_manager_payload(payload)
        # Prefer operator from authenticated user if present
        if getattr(g, 'current_user', None):
            operator = g.current_user.get('username') or operator
        mgr = service.create_manager(payload, operator=operator)
        return jsonify(mgr.to_dict()), 201
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except ConflictError as e:
        return jsonify({'error': str(e)}), 409


@require_auth
def list_managers_controller():
    repo = ManagerRepository()
    records = [m.to_dict() for m in repo.get_all()]
    return jsonify(records), 200


def assign_client_controller(manager_ref):
    """
    manager_ref: either numeric id or identification string (e.g. 'ID12345')
    """
    payload = request.get_json() or {}
    client_id = payload.get('client_id')
    operator = payload.get('operator')
    evidence = payload.get('evidence')
    if client_id is None:
        return jsonify({'error': 'client_id required'}), 400

    # resolve manager_ref to numeric id; support numeric identification values
    repo = ManagerRepository()
    manager_id = None
    mgr = None
    # If the ref looks numeric, try to resolve as primary key first.
    try:
        maybe_id = int(manager_ref)
        mgr = repo.get_by_id(maybe_id)
        if mgr:
            manager_id = mgr.id
        else:
            # fallback: maybe the identification is numeric (e.g. '234561')
            mgr = db.session.query(repo.model).filter(repo.model.identification == str(manager_ref), repo.model.is_deleted == False).first()
            if not mgr:
                return jsonify({'error': 'manager not found'}), 404
            manager_id = mgr.id
    except ValueError:
        # not numeric -> lookup by identification field
        mgr = db.session.query(repo.model).filter(repo.model.identification == manager_ref, repo.model.is_deleted == False).first()
        if not mgr:
            return jsonify({'error': 'manager not found'}), 404
        manager_id = mgr.id

    # resolve client_id: accept either numeric PK or identifier string
    from app.modules.managers.models import Client
    client_obj = None
    try:
        # try numeric id first
        maybe_cid = int(client_id)
        client_obj = db.session.query(Client).filter(Client.id == maybe_cid).first()
        if not client_obj:
            # fallback: maybe the identifier is numeric string
            client_obj = db.session.query(Client).filter(Client.identifier == str(client_id), Client.is_deleted == False).first()
    except (ValueError, TypeError):
        # not numeric -> lookup by identifier
        client_obj = db.session.query(Client).filter(Client.identifier == str(client_id), Client.is_deleted == False).first()

    if not client_obj:
        return jsonify({'error': 'client not found'}), 404

    # resolved numeric client PK to use in service call
    resolved_client_id = int(client_obj.id)

    # prefer authenticated operator if present
    if getattr(g, 'current_user', None):
        operator = g.current_user.get('username') or operator

    try:
        client = service.assign_client(int(manager_id), int(resolved_client_id), operator=operator, evidence=evidence)
        return jsonify(client.to_dict()), 200
    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except ConflictError as e:
        return jsonify({'error': str(e)}), 409


def create_client_controller():
    payload = request.get_json() or {}
    name = payload.get('name')
    identifier = payload.get('identifier')
    if not name or not identifier:
        return jsonify({'error': 'name and identifier required'}), 400
    from app.config.database import db
    from app.modules.managers.models import Client
    # check duplicate identifier first to return a friendly 400 instead of 500
    existing = db.session.query(Client).filter(Client.identifier == identifier, Client.is_deleted == False).first()
    if existing:
        return jsonify({'error': 'un cliente con este identificador ya existe'}), 400
    try:
        c = Client(name=name, identifier=identifier)
        # set created_by from authenticated user when available
        if getattr(g, 'current_user', None):
            c.created_by = g.current_user.get('username')
        db.session.add(c)
        db.session.commit()
        db.session.refresh(c)
        return jsonify(c.to_dict()), 201
    except Exception:
        # fallback: if an integrity error still occurs, return 400 with a helpful message
        db.session.rollback()
        return jsonify({'error': 'unable to create client, identifier may already exist'}), 400


@require_auth
def list_clients_controller():
    """Return all non-deleted clients."""
    from app.config.database import db
    records = db.session.query(Client).filter(Client.is_deleted == False).all()
    return jsonify([c.to_dict() for c in records]), 200


def get_client_manager_controller(client_id):
    from app.config.database import db
    from app.modules.managers.models import Client
    client = db.session.query(Client).filter(Client.id == int(client_id)).first()
    if not client:
        return jsonify({'error': 'client not found'}), 404
    if not client.manager:
        return jsonify({'manager': None}), 200
    return jsonify({'manager': client.manager.to_dict()}), 200


def get_manager_by_email_controller(email):
    """Return a manager by email along with an array of linked clients."""
    repo = ManagerRepository()
    mgr = repo.get_by_email(email)
    if not mgr:
        return jsonify({'error': 'manager not found'}), 404
    # serialize manager and include clients
    mgr_data = mgr.to_dict()
    # eager load clients
    clients = [c.to_dict() for c in mgr.clients] if getattr(mgr, 'clients', None) else []
    mgr_data['clients'] = clients
    return jsonify(mgr_data), 200
