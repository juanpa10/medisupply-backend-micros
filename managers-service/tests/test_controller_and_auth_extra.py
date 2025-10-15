import pytest
import requests
from app.core.auth.jwt_validator import verify_token_with_auth_service, get_token_from_request


def test_verify_token_with_auth_service_success(monkeypatch, app):
    class FakeResp:
        status_code = 200
        def json(self):
            return {'user': {'id': 1, 'username': 'u', 'role': 'tester'}}

    def fake_get(url, headers=None, timeout=None):
        return FakeResp()

    monkeypatch.setattr('requests.get', fake_get)
    app.config['AUTH_SERVICE_URL'] = 'http://auth-service:9001'
    with app.app_context():
        token = 'dummy'
        res = verify_token_with_auth_service(token)
        assert isinstance(res, dict) and 'user' in res


def test_get_token_from_request_invalid_scheme(client):
    # create endpoint that calls get_token_from_request
    from flask import current_app
    @current_app.route('/_token2')
    def _token2():
        t = get_token_from_request()
        return {'t': t}, 200

    # send with Basic scheme -> should return 401
    r = client.get('/_token2', headers={'Authorization': 'Basic abc'})
    assert r.status_code == 401
    j = r.get_json()
    assert 'Invalid auth scheme' in j['message']


def test_require_permission_allowed(app):
    app.config['TESTING'] = True

    from app.core.auth.decorators import require_permission

    @app.route('/_okperm')
    @require_permission('tester')
    def _okperm():
        return {'ok': True}, 200

    client = app.test_client()
    r = client.get('/_okperm')
    assert r.status_code == 200


def test_value_error_handler(app):
    @app.route('/_val')
    def _val():
        raise ValueError('bad')

    client = app.test_client()
    r = client.get('/_val')
    assert r.status_code == 400
    j = r.get_json()
    assert j['message'] == 'bad'


def test_create_manager_validation_errors(client):
    # missing fields
    r = client.post('/api/v1/managers', json={'email': 'a@b.com'})
    assert r.status_code == 400
    j = r.get_json()
    assert 'full_name is required' in j['error'] or 'phone is required' in j['error']

    # invalid email
    r2 = client.post('/api/v1/managers', json={'full_name':'X','email':'bad','phone':'123','identification':'id1'})
    assert r2.status_code == 400
    j2 = r2.get_json()
    assert 'invalid email format' in j2['error']
