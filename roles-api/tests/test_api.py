import jwt, json

def auth(h, t): 
    h = dict(h or {})
    h["Authorization"] = f"Bearer {t}"
    return h

def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200

def test_requires_auth(client):
    r = client.get("/api/users")
    assert r.status_code == 401

def test_list_roles_and_users(client, admin_token):
    r1 = client.get("/api/roles", headers=auth({}, admin_token))
    assert r1.status_code == 200
    assert isinstance(r1.get_json(), list)
    r2 = client.get("/api/users", headers=auth({}, admin_token))
    assert r2.status_code == 200
    assert isinstance(r2.get_json(), list)

def test_users_with_roles_initial(client, admin_token):
    r = client.get("/api/users-with-roles", headers=auth({}, admin_token))
    assert r.status_code == 200
    data = r.get_json()
    assert isinstance(data, list)
    # users seeded exist; roles arrays should exist
    assert all("roles" in u for u in data)

def test_set_user_roles_requires_admin(client, viewer_token):
    # viewer no puede modificar
    body = {"assignments":[{"role_id":1,"can_create":True,"can_edit":False,"can_delete":False,"can_view":True}]}
    r = client.put("/api/users/1/roles-permissions", headers=auth({}, viewer_token), json=body)
    assert r.status_code == 403

def test_set_user_roles_happy_path(client, admin_token):
    # asigna 2 roles con flags distintos
    body = {"assignments":[
        {"role_id":1,"can_create":True,"can_edit":False,"can_delete":False,"can_view":True},
        {"role_id":2,"can_create":False,"can_edit":True,"can_delete":False,"can_view":True}
    ]}
    r = client.put("/api/users/1/roles-permissions", headers=auth({}, admin_token), json=body)
    assert r.status_code == 200
    data = r.get_json()
    assert "roles" in data and len(data["roles"]) >= 1

    # verifica que se refleje en /users-with-roles
    r2 = client.get("/api/users-with-roles", headers=auth({}, admin_token))
    assert r2.status_code == 200
    users = r2.get_json()
    u1 = next(u for u in users if u["id"] == 1)
    names = {r["name"] for r in u1["roles"]}
    assert len(names) >= 1

# Nuevo test para verificar control de acceso
def test_access_control_requires_auth(client):
    # Sin token debe rechazar
    body = {"email": "juan@example.com", "rol": "Admin", "action": "create"}
    r = client.post("/api/access-control", json=body)
    assert r.status_code == 401

def test_access_control(client, admin_token):
    # Falta 'action'
    body = {"email": "seed@demo.com", "rol": "admin"}
    r = client.post("/api/access-control", headers=auth({}, admin_token), json=body)
    assert r.status_code == 400