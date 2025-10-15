import pytest
import jwt
import requests
from datetime import datetime, timedelta
from app import create_app
from app.config.database import db
from app.core.exceptions import UnauthorizedError
from app.core.auth.jwt_validator import validate_jwt_token, verify_token_with_auth_service
from app.core.exceptions import NotFoundError
from app.modules.managers.repository import ManagerRepository
from app.core.auth.decorators import require_permission


def make_token(secret, algorithm='HS256', exp_delta_seconds=60, payload_extra=None):
    payload = {'sub': 'u1', 'exp': datetime.utcnow() + timedelta(seconds=exp_delta_seconds)}
    if payload_extra:
        payload.update(payload_extra)
    return jwt.encode(payload, secret, algorithm=algorithm)


def test_validate_jwt_token_invalid_and_expired(app):
    app.config['JWT_SECRET'] = 'shh'
    app.config['JWT_ALGORITHM'] = 'HS256'
    # invalid signature
    token = make_token('othersecret')
    with app.app_context():
        with pytest.raises(UnauthorizedError):
            validate_jwt_token(token)

    # expired token
    exp_token = make_token('shh', exp_delta_seconds=-10)
    with app.app_context():
        with pytest.raises(UnauthorizedError):
            validate_jwt_token(exp_token)


def test_verify_token_with_auth_service_fallback(monkeypatch, app):
    # simulate requests.get raising to force fallback to local validate
    def raise_req(*args, **kwargs):
        raise requests.RequestException()

    monkeypatch.setattr('requests.get', raise_req)
    app.config['JWT_SECRET'] = 'shh'
    token = make_token('shh')
    with app.app_context():
        # should return payload dict when fallback works
        payload = verify_token_with_auth_service(token)
        assert payload.get('sub') == 'u1'


def test_require_permission_forbidden(app):
    # TESTING mode will set g.current_user role to 'tester'
    app.config['TESTING'] = True

    @app.route('/_perm')
    @require_permission('admin')
    def _perm():
        return {'ok': True}, 200

    client = app.test_client()
    r = client.get('/_perm')
    assert r.status_code == 403
    j = r.get_json()
    assert 'Role required' in j['message']


def test_error_handler_app_exception(app):
    from app.core.exceptions import NotFoundError

    @app.route('/_raise')
    def _raise():
        raise NotFoundError('boom')

    client = app.test_client()
    r = client.get('/_raise')
    assert r.status_code == 404
    j = r.get_json()
    assert j['message'] == 'boom'


def test_base_repository_crud_with_manager(app):
    # use ManagerRepository against real model inside testing DB
    repo = ManagerRepository()
    # create
    data = {'full_name': 'M1', 'email': 'm1@example.com', 'phone': '123', 'identification': 'ID1'}
    mgr = repo.create(data)
    assert mgr.id is not None
    # exists
    assert repo.exists(email='m1@example.com')
    # update
    repo.update(mgr.id, {'full_name': 'M1-updated'})
    m2 = repo.get_by_id(mgr.id)
    assert m2.full_name == 'M1-updated'
    # count
    assert repo.count() >= 1
    # delete soft
    repo.delete(mgr.id, soft=True)
    # after soft delete, get_by_id should return None
    assert repo.get_by_id(mgr.id) is None


def test_create_client_duplicate_returns_400(client):
    # create client
    r1 = client.post('/api/v1/clients', json={'name': 'C1', 'identifier': 'DUP1'})
    assert r1.status_code == 201
    # duplicate
    r2 = client.post('/api/v1/clients', json={'name': 'C1b', 'identifier': 'DUP1'})
    assert r2.status_code == 400
    j = r2.get_json()
    assert 'un cliente con este identificador' in j['error']


def test_get_client_manager_not_found(client):
    r = client.get('/api/v1/clients/99999/manager')
    assert r.status_code == 404
