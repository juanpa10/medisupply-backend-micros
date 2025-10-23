import os
import json
import importlib.util
import sys
import time
from pathlib import Path


def load_auth_module_with_env(env: dict):
    old = {k: os.environ.get(k) for k in env}
    os.environ.update(env)
    try:
        root = Path(__file__).resolve().parents[1]
        module_path = root / "app.py"
        spec = importlib.util.spec_from_file_location("auth_service_app_ex", str(module_path))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        return mod
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def test_login_invalid_json():
    mod = load_auth_module_with_env({'USERS_JSON': json.dumps([])})
    app = mod.app
    app.testing = True
    client = app.test_client()

    # send malformed json body
    r = client.post('/auth/login', data='not-a-json', content_type='application/json')
    assert r.status_code == 400
    j = r.get_json()
    assert j and 'invalid json' in j.get('error', '')


def test_verify_expired_token():
    # import module without DB
    mod = load_auth_module_with_env({'USERS_JSON': json.dumps([{"email":"a","password":"p","role":"r"}])})
    app = mod.app
    app.testing = True
    client = app.test_client()

    # craft an expired token (exp in the past)
    now = int(time.time())
    payload = {"sub": "a", "role": "r", "iat": now - 3600, "exp": now - 10}
    token = mod.jwt.encode(payload, mod.JWT_SECRET, algorithm="HS256")

    r = client.get(f'/auth/verify?token={token}')
    assert r.status_code == 401
    j = r.get_json()
    assert j.get('valid') is False and 'expired' in j.get('error', '')


def test_create_user_no_writable_columns():
    # create module with DB enabled but without init so users table may be absent
    mod = load_auth_module_with_env({'DATABASE_URL': 'sqlite:///:memory:'})
    app = mod.app
    app.testing = True
    client = app.test_client()

    # ensure users table does not exist
    with app.app_context():
        try:
            mod.db.session.execute(mod.text('DROP TABLE IF EXISTS users'))
            mod.db.session.commit()
        except Exception:
            try:
                mod.db.session.rollback()
            except Exception:
                pass

    r = client.post('/auth/users', json={'email': 'x@x.com', 'password': 'P#1'})
    assert r.status_code == 500
    j = r.get_json()
    assert j.get('error') == 'no writable columns available'


def test_db_backed_login_user_not_found():
    # DB enabled but seeded with no users
    env = {'DATABASE_URL': 'sqlite:///:memory:', 'INIT_DB': 'true', 'USERS_JSON': json.dumps([])}
    mod = load_auth_module_with_env(env)
    app = mod.app
    app.testing = True
    client = app.test_client()

    r = client.post('/auth/login', json={'email': 'doesnotexist', 'password': 'nopass'})
    assert r.status_code == 401


def test_login_uses_auth_user_roles():
    # Create a minimal users table (no role column) and an auth_user_roles mapping
    env = {'DATABASE_URL': 'sqlite:///:memory:', 'INIT_DB': 'true', 'USERS_JSON': json.dumps([])}
    mod = load_auth_module_with_env(env)
    app = mod.app
    app.testing = True
    client = app.test_client()

    with app.app_context():
        # drop and recreate minimal users table
        mod.db.session.execute(mod.text('DROP TABLE IF EXISTS users'))
        mod.db.session.execute(mod.text('CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE, password TEXT)'))
        mod.db.session.commit()
        # insert user
        mod.db.session.execute(mod.text("INSERT INTO users (email, password) VALUES ('legacylogin@example.com', 'Plain#9')"))
        mod.db.session.commit()
        # fetch id
        row = mod.db.session.execute(mod.text("SELECT id FROM users WHERE email='legacylogin@example.com' LIMIT 1")).fetchone()
        uid = row[0]
        # ensure auth_user_roles table exists (init_db should have created it)
        try:
            mod.db.session.execute(mod.text("INSERT INTO auth_user_roles (user_id, role) VALUES (:uid, :role)"), {'uid': uid, 'role': 'security_admin'})
            mod.db.session.commit()
        except Exception:
            try:
                mod.db.session.rollback()
            except Exception:
                pass

    # Now login using plaintext password fallback; role should be resolved from auth_user_roles
    r = client.post('/auth/login', json={'email': 'legacylogin@example.com', 'password': 'Plain#9'})
    assert r.status_code == 200
    j = r.get_json()
    assert j.get('role') == 'security_admin'


def test_verify_header_token():
    mod = load_auth_module_with_env({'USERS_JSON': json.dumps([{"email":"h","password":"p","role":"r"}])})
    app = mod.app
    app.testing = True
    client = app.test_client()

    token = mod.create_token('h', 'r')
    headers = {'Authorization': f'Bearer {token}'}
    r = client.get('/auth/verify', headers=headers)
    assert r.status_code == 200
    j = r.get_json()
    assert j.get('valid') is True and j.get('role') == 'r'


def test_create_user_db_error_returns_500(monkeypatch):
    # simulate DB error during user creation to hit exception path
    mod = load_auth_module_with_env({'DATABASE_URL': 'sqlite:///:memory:'})
    app = mod.app
    app.testing = True
    client = app.test_client()

    # create a minimal users table so the create_user_api path proceeds to execute
    with app.app_context():
        try:
            mod.db.session.execute(mod.text('DROP TABLE IF EXISTS users'))
            # include email and pwd_hash so insert_data will be populated
            mod.db.session.execute(mod.text('CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE, pwd_hash TEXT, names TEXT, password TEXT, role TEXT)'))
            mod.db.session.commit()
        except Exception:
            try:
                mod.db.session.rollback()
            except Exception:
                pass

    def raise_exec(*a, **k):
        raise Exception('boom')

    # monkeypatch the session.execute to raise when called
    monkeypatch.setattr(mod.db.session, 'execute', raise_exec)

    r = client.post('/auth/users', json={'email': 'err@example.com', 'password': 'P#1'})
    assert r.status_code == 500
    j = r.get_json()
    assert j.get('error') == 'could_not_create_user'


def test_get_user_from_db_no_columns():
    env = {'DATABASE_URL': 'sqlite:///:memory:'}
    mod = load_auth_module_with_env(env)
    # drop users table so inspector returns no columns
    app = mod.app
    app.testing = True
    with app.app_context():
        try:
            mod.db.session.execute(mod.text('DROP TABLE IF EXISTS users'))
            mod.db.session.commit()
        except Exception:
            try:
                mod.db.session.rollback()
            except Exception:
                pass

    # get_user_from_db should return None when no selectable columns
    res = mod.get_user_from_db('noone')
    assert res is None


def test_init_seeds_legacy_password_schema(tmp_path):
    # Create a file-backed sqlite DB with a legacy users table (password column)
    db_file = tmp_path / 'legacy.db'
    db_url = f'sqlite:///{db_file}'

    # create the database file and a users table without role/pwd_hash column
    import sqlite3
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute('CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE, password TEXT, names TEXT)')
    conn.commit()
    conn.close()

    users_json = json.dumps([
        {"email": "legacyseed@example.com", "password": "L#1", "role": "security_admin"}
    ])

    # Now import module with INIT_DB true pointing to our file DB so init_db will run against existing schema
    mod = load_auth_module_with_env({'DATABASE_URL': db_url, 'INIT_DB': 'true', 'USERS_JSON': users_json})

    # After init, the legacy user should exist and an auth_user_roles entry should have been created
    app = mod.app
    with app.app_context():
        row = mod.db.session.execute(mod.text("SELECT id FROM users WHERE email='legacyseed@example.com' LIMIT 1")).fetchone()
        assert row is not None
        uid = row[0]
        aur = mod.db.session.execute(mod.text("SELECT role FROM auth_user_roles WHERE user_id=:uid LIMIT 1"), {'uid': uid}).fetchone()
        assert aur and aur[0] == 'security_admin'
