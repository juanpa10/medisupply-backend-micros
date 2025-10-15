import os
import json
import importlib.util
import sys
from pathlib import Path


def load_auth_module_with_env(env: dict):
    # prepare env for import
    old = {k: os.environ.get(k) for k in env}
    os.environ.update(env)
    try:
        root = Path(__file__).resolve().parents[1]
        module_path = root / "app.py"
        spec = importlib.util.spec_from_file_location("auth_service_app_db", str(module_path))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        return mod
    finally:
        # restore previous env values
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def test_db_backed_login_and_verify():
    # Use sqlite in-memory for tests
    os.environ['USERS_JSON'] = json.dumps([
        {"email": "dbuser", "password": "DbPass#1", "role": "security_admin"}
    ])
    env = {
        'DATABASE_URL': 'sqlite:///:memory:',
        'INIT_DB': 'true'
    }
    mod = load_auth_module_with_env(env)
    app = mod.app
    app.testing = True
    client = app.test_client()

    # login should work (seeded into DB on init)
    r = client.post('/auth/login', json={'email': 'dbuser', 'password': 'DbPass#1'})
    assert r.status_code == 200
    j = r.get_json()
    assert 'access_token' in j
    token = j['access_token']

    # verify via query param
    r2 = client.get(f'/auth/verify?token={token}')
    assert r2.status_code == 200
    v = r2.get_json()
    assert v.get('valid') is True
    assert v.get('role') == 'security_admin'
