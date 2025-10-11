import os
import json
import pytest
import importlib.util
import sys
from pathlib import Path


def load_auth_app():
    root = Path(__file__).resolve().parents[1]
    module_path = root / "app.py"
    spec = importlib.util.spec_from_file_location("auth_service_app", str(module_path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod.app


@pytest.fixture()
def client():
    os.environ["USERS_JSON"] = json.dumps([
        {"email": "admin", "password": "Admin#123", "role": "security_admin"},
        {"email": "viewer", "password": "Viewer#123", "role": "viewer"}
    ])
    flask_app = load_auth_app()
    flask_app.testing = True
    with flask_app.test_client() as c:
        yield c


def test_login_success_and_verify(client):
    r = client.post("/auth/login", json={"email":"admin","password":"Admin#123"})
    assert r.status_code == 200
    j = r.get_json()
    assert "access_token" in j
    token = j["access_token"]

    r2 = client.get(f"/auth/verify?token={token}")
    assert r2.status_code == 200
    v = r2.get_json()
    assert v.get("valid") is True
    assert v.get("role") == "security_admin"


def test_login_bad_credentials(client):
    r = client.post("/auth/login", json={"email":"admin","password":"wrong"})
    assert r.status_code == 401


def test_login_missing_fields(client):
    r = client.post("/auth/login", json={"email":"admin"})
    assert r.status_code == 400
