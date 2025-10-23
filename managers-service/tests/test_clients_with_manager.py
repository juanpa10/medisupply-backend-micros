import pytest


def test_list_clients_with_manager_flow(client):
    # create two managers
    m1 = {'full_name': 'G1', 'email': 'g1@example.com', 'phone': '1', 'identification': 'G1'}
    m2 = {'full_name': 'G2', 'email': 'g2@example.com', 'phone': '2', 'identification': 'G2'}
    r1 = client.post('/api/v1/managers', json=m1)
    r2 = client.post('/api/v1/managers', json=m2)
    assert r1.status_code == 201 and r2.status_code == 201
    id1 = r1.get_json()['id']

    # create two clients
    c1 = client.post('/api/v1/clients', json={'name':'CliA','identifier':'CA1'})
    c2 = client.post('/api/v1/clients', json={'name':'CliB','identifier':'CB1'})
    assert c1.status_code == 201 and c2.status_code == 201
    cid1 = c1.get_json()['id']
    cid2 = c2.get_json()['id']

    # assign only first client to manager id1
    a = client.post(f'/api/v1/managers/{id1}/assign', json={'client_id': cid1})
    assert a.status_code == 200

    # call the new HTTP endpoint
    r = client.get('/api/v1/clients-with-manager')
    assert r.status_code == 200
    arr = r.get_json()
    # find our clients
    found_c1 = next((x for x in arr if x['id'] == cid1), None)
    found_c2 = next((x for x in arr if x['id'] == cid2), None)
    assert found_c1 is not None and found_c2 is not None
    assert isinstance(found_c1['manager'], dict)
    assert found_c1['manager']['full_name'] == 'G1'
    assert found_c2['manager'] is None
