import os
import json
import importlib.util
import sys
from pathlib import Path


def load_auth_module():
    root = Path(__file__).resolve().parents[1]
    module_path = root / "app.py"
    spec = importlib.util.spec_from_file_location("auth_service_app", str(module_path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_load_users_and_token_functions():
    os.environ.pop('DATABASE_URL', None)
    os.environ['USERS_JSON'] = json.dumps([
        {"email": "u1", "password": "pw1", "role": "admin"}
    ])
    mod = load_auth_module()
    users = mod.load_users()
    assert 'u1' in users
    token = mod.create_token('u1', 'admin')
    decoded = mod.decode_token(token)
    assert decoded.get('sub') == 'u1'
    assert decoded.get('role') == 'admin'


def test_verify_endpoint_missing_token():
    mod = load_auth_module()
    app = mod.app
    app.testing = True
    with app.test_client() as c:
        r = c.get('/auth/verify')
        assert r.status_code == 400
        j = r.get_json()
        assert j.get('valid') is False