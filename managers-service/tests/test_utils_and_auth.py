import pytest
from flask import Flask, g
from app.core.utils.response import success_response, error_response
from app.core.auth.jwt_validator import get_token_from_request, validate_jwt_token
from app.core.auth.decorators import require_auth, optional_auth
from app.core.exceptions import UnauthorizedError, NotFoundError
from app.shared.base_repository import BaseRepository


def test_success_and_error_response_return_json(app):
    with app.app_context():
        resp, code = success_response({'a': 1}, message='ok', status_code=201)
        assert code == 201
        j = resp.get_json()
        assert j['success'] is True and j['message'] == 'ok' and j['data']['a'] == 1

        resp_e, code_e = error_response('bad', status_code=400, errors={'x': 'y'})
        assert code_e == 400
        je = resp_e.get_json()
        assert je['success'] is False and je['message'] == 'bad' and je['errors']['x'] == 'y'


def test_get_token_from_request_raises_when_missing(app):
    client = app.test_client()
    # make a small endpoint to call get_token_from_request
    @app.route('/_tok')
    def _tok():
        # should raise UnauthorizedError because header missing
        with pytest.raises(UnauthorizedError):
            get_token_from_request()
        return '', 204

    r = client.get('/_tok')
    assert r.status_code == 204


def test_require_auth_sets_dummy_user_in_testing(app):
    # create a small endpoint decorated with require_auth
    @app.route('/_auth')
    @require_auth
    def _auth():
        return {'user': g.current_user}, 200

    client = app.test_client()
    r = client.get('/_auth')
    j = r.get_json()
    assert j['user']['username'] == 'test'


def test_optional_auth_allows_missing_token(app):
    @app.route('/_opt')
    @optional_auth
    def _opt():
        return {'ok': True, 'user': g.current_user}, 200

    client = app.test_client()
    r = client.get('/_opt')
    j = r.get_json()
    assert j['ok'] is True and j['user'] is None


def test_base_repository_get_by_id_or_fail_raises_notfound(app):
    # Create a dummy repository that overrides get_by_id to simulate missing record
    class DummyRepo(BaseRepository):
        def __init__(self):
            super().__init__(object)

        def get_by_id(self, id, include_deleted: bool = False):
            return None

    repo = DummyRepo()
    with pytest.raises(NotFoundError):
        repo.get_by_id_or_fail(9999)
