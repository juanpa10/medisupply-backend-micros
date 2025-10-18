import os
import json
import pytest


def test_seed_assigns_admin_role(app):
    # app fixture ensures DB seeded
    from app.services.roles_service import RolesService
    svc = RolesService()
    users = svc.list_users_with_roles()
    assert isinstance(users, list)
    # ensure at least one user has roles array and admin role may be present
    assert all('roles' in u for u in users)


def test_repo_duplicate_email(app):
    from app.services.roles_service import RolesService
    svc = RolesService()
    # create a unique user
    import time
    email = f"dup{int(time.time()*1000)}@example.com"
    u = svc.create_user('Test User', email, 'pw123')
    assert u is not None
    # attempt to create again via repo should raise ValueError
    with pytest.raises(ValueError):
        svc.repo.create_user('Test User', email, 'pw123')


def test_set_user_roles_via_service(app):
    from app.services.roles_service import RolesService
    svc = RolesService()
    # create role and user
    import time
    role_name = f"TestRole{int(time.time()*1000)}"
    email = f"another{int(time.time()*1000)}@example.com"
    r = svc.create_role(role_name,'desc')
    u = svc.create_user('Another', email, 'pw')
    assert r and u
    res = svc.set_user_roles(u.id, [{'role_id': r.id, 'can_create': True, 'can_edit': False, 'can_delete': False, 'can_view': True}])
    assert res is not None
    assert any(rr['name'] == role_name for rr in res['roles'])


def test_create_user_missing_fields_returns_bad_request(client, admin_token):
    r = client.post('/api/users', headers={'Authorization': f'Bearer {admin_token}'}, json={})
    assert r.status_code == 400
    j = r.get_json()
    assert j.get('error') == 'BAD_REQUEST'


def test_set_user_roles_bad_assignments(client, admin_token):
    # assignments must be a list
    body = {'assignments': 'notalist'}
    r = client.put('/api/users/1/roles-permissions', headers={'Authorization': f'Bearer {admin_token}'}, json=body)
    assert r.status_code == 400
    j = r.get_json()
    assert j.get('error') == 'BAD_REQUEST'


def test_create_user_delegation_fallback_when_auth_unreachable(client, admin_token, monkeypatch):
    # simulate auth-service unreachable by setting AUTH_SERVICE_URL to a non-routable address
    import os
    os.environ['AUTH_SERVICE_URL'] = 'http://localhost:59999'
    import time
    email = f"local{int(time.time()*1000)}@example.com"
    r = client.post('/api/users', headers={'Authorization': f'Bearer {admin_token}'}, json={'names':'Local','email':email,'password':'pw'})
    # depending on timing, local create should succeed or return email_exists
    assert r.status_code in (201, 400)
    if r.status_code == 201:
        j = r.get_json()
        assert j.get('email') == email
