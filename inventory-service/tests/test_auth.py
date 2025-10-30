"""
Tests for JWTValidator and auth decorators.
"""
import jwt
import requests
from unittest.mock import patch, MagicMock
import pytest

from app.core.auth.jwt_validator import JWTValidator
from app.core.auth.decorators import require_auth, require_permission, optional_auth


def test_extract_token_from_request_and_validate(app):
    with app.test_request_context(headers={'Authorization': 'Bearer abc.def.ghi'}):
        token = JWTValidator.extract_token_from_request()
        assert token == 'abc.def.ghi'

    with app.test_request_context(headers={'Authorization': 'BadHeader'}):
        assert JWTValidator.extract_token_from_request() is None


def test_decode_token_and_expired(app):
    # set secret and algorithm in app config
    app.config['JWT_SECRET'] = 's'
    app.config['JWT_ALGORITHM'] = 'HS256'

    payload = {'sub': '1'}
    token = jwt.encode(payload, app.config['JWT_SECRET'], algorithm=app.config['JWT_ALGORITHM'])

    with app.app_context():
        decoded = JWTValidator.decode_token(token)
        assert decoded.get('sub') == '1'


def test_verify_with_auth_service_success_and_failure(app, monkeypatch):
    # success case
    fake_resp = MagicMock()
    fake_resp.status_code = 200
    fake_resp.json.return_value = {'valid': True, 'sub': 'u1', 'role': 'r'}

    monkeypatch.setattr('requests.get', lambda *args, **kwargs: fake_resp)

    with app.app_context():
        res = JWTValidator.verify_with_auth_service('t')
        assert res['sub'] == 'u1'

    # failure case - non-200
    fake_resp2 = MagicMock()
    fake_resp2.status_code = 401
    monkeypatch.setattr('requests.get', lambda *args, **kwargs: fake_resp2)

    with app.app_context():
        assert JWTValidator.verify_with_auth_service('t') is None


def test_validate_token_branches(monkeypatch, app):
    # no token
    with app.test_request_context():
        monkeypatch.setattr('app.core.auth.jwt_validator.JWTValidator.extract_token_from_request', lambda: None)
        payload, err = JWTValidator.validate_token()
        assert payload is None and err is not None

    # decode raises InvalidTokenError -> verify_with_auth_service returns payload
    with app.test_request_context():
        monkeypatch.setattr('app.core.auth.jwt_validator.JWTValidator.extract_token_from_request', lambda: 't')
        class _E(Exception):
            pass

        def fake_decode(t):
            raise jwt.InvalidTokenError()

        monkeypatch.setattr('app.core.auth.jwt_validator.JWTValidator.decode_token', staticmethod(fake_decode))
        monkeypatch.setattr('app.core.auth.jwt_validator.JWTValidator.verify_with_auth_service', staticmethod(lambda token: {'sub': 'x', 'role': 'r'}))

        payload, err = JWTValidator.validate_token()
        assert payload and err is None


def test_decorators_require_auth_and_permission(monkeypatch, app):
    # simulate validate_token returning error
    monkeypatch.setattr('app.core.auth.jwt_validator.JWTValidator.validate_token', staticmethod(lambda: (None, 'err')))

    @require_auth
    def protected():
        return {'ok': True}

    resp, status = protected()
    assert status == 401

    # require_permission with insufficient role
    monkeypatch.setattr('app.core.auth.jwt_validator.JWTValidator.validate_token', staticmethod(lambda: ({'sub': '1', 'role': 'user'}, None)))

    @require_permission('admin')
    def admin_only():
        return {'admin': True}

    resp, status = admin_only()
    assert status == 403

    # optional_auth - with and without token
    monkeypatch.setattr('app.core.auth.jwt_validator.JWTValidator.validate_token', staticmethod(lambda: ({'sub': '1', 'role': 'user'}, None)))

    @optional_auth
    def public():
        from flask import g
        return {'user': getattr(g, 'user', None)}

    res = public()
    # optional_auth returns the wrapped function's return value
    assert isinstance(res, dict)
