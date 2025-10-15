def test_create_manager_and_duplicates(client):
    # create manager
    payload = {
        'full_name': 'Juan Perez',
        'email': 'juan@example.com',
        'phone': '1234567890',
        'identification': 'ID123'
    }
    resp = client.post('/api/v1/managers', json=payload)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data['email'] == 'juan@example.com'

    # duplicate email
    payload2 = {
        'full_name': 'Maria',
        'email': 'juan@example.com',
        'phone': '0987654321',
        'identification': 'ID999'
    }
    resp2 = client.post('/api/v1/managers', json=payload2)
    assert resp2.status_code == 409

    # duplicate identification
    payload3 = {
        'full_name': 'Carlos',
        'email': 'carlos@example.com',
        'phone': '111222333',
        'identification': 'ID123'
    }
    resp3 = client.post('/api/v1/managers', json=payload3)
    assert resp3.status_code == 409


def test_assign_and_reassign_client(client):
    # create two managers and a client
    m1 = {'full_name': 'A', 'email': 'a@example.com', 'phone': '1', 'identification': 'A1'}
    m2 = {'full_name': 'B', 'email': 'b@example.com', 'phone': '2', 'identification': 'B1'}
    client_resp = client.post('/api/v1/managers', json=m1)
    assert client_resp.status_code == 201
    id1 = client_resp.get_json()['id']
    client_resp2 = client.post('/api/v1/managers', json=m2)
    id2 = client_resp2.get_json()['id']
    # create client
    c = client.post('/api/v1/clients', json={'name': 'Cliente1', 'identifier': 'C1'})
    assert c.status_code == 201
    client_id = c.get_json()['id']
    # assign to m1
    assign = client.post(f'/api/v1/managers/{id1}/assign', json={'client_id': client_id})
    assert assign.status_code == 200
    # check manager is m1
    check = client.get(f'/api/v1/clients/{client_id}/manager')
    assert check.status_code == 200
    assert check.get_json()['manager']['id'] == id1
    # reassign to m2
    reassign = client.post(f'/api/v1/managers/{id2}/assign', json={'client_id': client_id})
    assert reassign.status_code == 200
    check2 = client.get(f'/api/v1/clients/{client_id}/manager')
    assert check2.get_json()['manager']['id'] == id2


def test_get_manager_by_email_includes_clients(client):
    # create manager
    payload = {
        'full_name': 'Manager X',
        'email': 'mx@example.com',
        'phone': '555',
        'identification': 'MX1'
    }
    resp = client.post('/api/v1/managers', json=payload)
    assert resp.status_code == 201
    mid = resp.get_json()['id']
    # create two clients
    c1 = client.post('/api/v1/clients', json={'name':'C1','identifier':'C1'})
    c2 = client.post('/api/v1/clients', json={'name':'C2','identifier':'C2'})
    assert c1.status_code == 201 and c2.status_code == 201
    id1 = c1.get_json()['id']; id2 = c2.get_json()['id']
    # assign both to manager
    a1 = client.post(f'/api/v1/managers/{mid}/assign', json={'client_id': id1})
    a2 = client.post(f'/api/v1/managers/{mid}/assign', json={'client_id': id2})
    assert a1.status_code == 200 and a2.status_code == 200
    # fetch by email
    r = client.get(f'/api/v1/managers/by-email/{payload["email"]}')
    assert r.status_code == 200
    j = r.get_json()
    assert j.get('email') == payload['email']
    assert isinstance(j.get('clients'), list) and len(j.get('clients')) >= 2
