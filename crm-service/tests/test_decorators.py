import pytest
from app import create_app
from app.core.auth.decorators import require_auth


def test_require_auth_without_token():
    app = create_app('testing')

    @app.route('/protected')
    @require_auth
    def protected():
        return 'ok'

    client = app.test_client()
    r = client.get('/protected')
    assert r.status_code == 401


def test_require_auth_with_malformed_header(monkeypatch):
    app = create_app('testing')

    @app.route('/protected2')
    @require_auth
    def protected2():
        return 'ok'

    client = app.test_client()
    r = client.get('/protected2', headers={'Authorization': 'BadHeader token'})
    assert r.status_code == 401
