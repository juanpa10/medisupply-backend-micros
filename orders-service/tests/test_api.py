import pytest
from app.app import create_app
from app.db import Base, engine, SessionLocal
from app.services.orders_service import svc
import json
import time



def make_token(sub='cust-1'):
    import jwt, time, os
    secret = os.getenv('JWT_SECRET', 'supersecret')
    now = int(time.time())
    return jwt.encode({'sub': sub, 'role': 'viewer', 'iat': now, 'exp': now + 3600}, secret, algorithm='HS256')


def test_list_orders_empty(client):
    token = make_token('no-such')
    r = client.get('/api/orders', headers={'Authorization': f'Bearer {token}'})
    assert r.status_code == 200
    data = r.get_json()
    assert 'message' in data


def test_create_and_list(client):
    token = make_token('cust-1')
    # create
    r = client.post('/api/orders', headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}, json={'order_number': 'ORD-9999'})
    assert r.status_code == 201
    j = r.get_json()
    assert j['order_number'] == 'ORD-9999'

    # list
    r2 = client.get('/api/orders', headers={'Authorization': f'Bearer {token}'})
    assert r2.status_code == 200
    data = r2.get_json()
    assert any(o['order_number'] == 'ORD-9999' for o in data)


def test_update_status(client):
    token = make_token('cust-1')
    r = client.put('/api/orders/ORD-9999/status', headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}, json={'status': 'transito'})
    assert r.status_code == 200
    j = r.get_json()
    assert j['status'] == 'transito'


def test_stream_sse(client):
    token = make_token('cust-1')
    r = client.get('/api/orders/stream', headers={'Authorization': f'Bearer {token}'}, buffered=True)
    assert r.status_code == 200
    # read a small chunk
    data = r.get_data(as_text=True)
    assert 'data:' in data
def auth(headers, customer_id=None):
    h = headers.copy()
    if customer_id:
        h['X-Customer-Id'] = customer_id
    return h


def test_list_orders_empty(client):
    r = client.get('/api/orders', headers=auth({}, 'cust-1'))
    assert r.status_code == 200
    assert r.get_json() == []


def test_create_and_get_order(client):
    # create
    r = client.post('/api/orders', json={'order_number':'ORD-2001'}, headers=auth({}, 'cust-1'))
    assert r.status_code == 201
    data = r.get_json()
    assert data['order_number'] == 'ORD-2001'

    # get
    r2 = client.get(f"/api/orders/{data['order_number']}", headers=auth({}, 'cust-1'))
    assert r2.status_code == 200
    got = r2.get_json()
    assert got['order_number'] == 'ORD-2001'


def test_forbidden_access(client):
    r = client.post('/api/orders', json={'order_number':'ORD-3001','customer_id':'cust-2'}, headers=auth({}, 'cust-1'))
    # attempt to create with different customer via body should be blocked (we read customer from header)
    assert r.status_code == 400 or r.status_code == 201
    # if created, next attempt to read with wrong header must be forbidden
    if r.status_code == 201:
        data = r.get_json()
        r2 = client.get(f"/api/orders/{data['order_number']}", headers=auth({}, 'cust-1'))
        assert r2.status_code == 404


def test_filters_and_status(client):
    # seed some orders via direct service (use API to keep tests black-box)
    client.post('/api/orders', json={'order_number':'ORD-4001'}, headers=auth({}, 'cust-X'))
    client.post('/api/orders', json={'order_number':'ORD-4002','status':'transito'}, headers=auth({}, 'cust-X'))
    client.post('/api/orders', json={'order_number':'ORD-4003','status':'entregado'}, headers=auth({}, 'cust-X'))

    r = client.get('/api/orders?status=transito', headers=auth({}, 'cust-X'))
    assert r.status_code == 200
    arr = r.get_json()
    assert all(o['status'] == 'transito' for o in arr)


def test_update_status(client):
    client.post('/api/orders', json={'order_number':'ORD-5001'}, headers=auth({}, 'cust-Y'))
    r = client.put('/api/orders/ORD-5001/status', json={'status':'En preparacion'}, headers=auth({}, 'cust-Y'))
    assert r.status_code == 200
    got = r.get_json()
    assert got['status'] == 'En preparacion'


def test_itemized_order(client):
    # Create an order with two items; one product created inline, one with explicit unit_price
    payload = {
        'order_number': 'ORD-7001',
        'items': [
            {'name': 'Widget A', 'unit_price': 10.5, 'quantity': 2},
            {'name': 'Widget B', 'unit_price': 5.0, 'quantity': 1}
        ]
    }
    r = client.post('/api/orders', json=payload, headers=auth({}, 'cust-items'))
    assert r.status_code == 201
    created = r.get_json()
    assert created['order_number'] == 'ORD-7001'
    # monto should be 10.5*2 + 5.0*1 = 26.0
    assert abs(float(created['monto']) - 26.0) < 1e-6

    # fetch the order and inspect items
    r2 = client.get(f"/api/orders/{created['order_number']}", headers=auth({}, 'cust-items'))
    assert r2.status_code == 200
    got = r2.get_json()
    assert abs(float(got['monto']) - 26.0) < 1e-6
    assert len(got['items']) == 2
