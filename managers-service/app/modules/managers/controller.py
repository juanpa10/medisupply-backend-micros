from flask import request, jsonify, g
import re

from app.modules.managers.service import service
from app.modules.managers.repository import ManagerRepository
from app.config.database import db
from app.core.exceptions import ValidationError, ConflictError, NotFoundError
from app.core.auth.decorators import require_auth, require_permission


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

    # resolve manager_ref to numeric id
    repo = ManagerRepository()
    manager_id = None
    try:
        # try numeric
        manager_id = int(manager_ref)
    except ValueError:
        # lookup by identification field
        mgr = db.session.query(repo.model).filter(repo.model.identification == manager_ref, repo.model.is_deleted == False).first()
        if not mgr:
            return jsonify({'error': 'manager not found'}), 404
        manager_id = mgr.id

    # prefer authenticated operator if present
    if getattr(g, 'current_user', None):
        operator = g.current_user.get('username') or operator

    try:
        client = service.assign_client(int(manager_id), int(client_id), operator=operator, evidence=evidence)
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


def get_client_manager_controller(client_id):
    from app.config.database import db
    from app.modules.managers.models import Client
    client = db.session.query(Client).filter(Client.id == int(client_id)).first()
    if not client:
        return jsonify({'error': 'client not found'}), 404
    if not client.manager:
        return jsonify({'manager': None}), 200
    return jsonify({'manager': client.manager.to_dict()}), 200
