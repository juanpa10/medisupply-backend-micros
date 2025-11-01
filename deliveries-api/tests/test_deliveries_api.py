def test_health(client):
    r = client.get("/health"); assert r.status_code == 200 and r.get_json()["status"]=="ok"

def test_create_and_list_and_filter(client):
    # create
    body = {"order_id":11,"client_id":99,"delivery_date":"2025-10-25T10:00:00","status":"alistamiento"}
    r = client.post("/deliveries", json=body); assert r.status_code == 201
    created = r.get_json(); assert created["client_id"]==99

    # list all
    l = client.get("/deliveries?limit=10"); assert l.status_code == 200
    assert any(it["id"]==created["id"] for it in l.get_json()["items"])

    # filter by client
    lc = client.get("/deliveries/client/99"); assert lc.status_code == 200
    assert all(it["client_id"]==99 for it in lc.get_json()["items"])

def test_errors(client):
    # missing
    r = client.post("/deliveries", json={"order_id":1}); assert r.status_code == 400
    # invalid status
    r2 = client.post("/deliveries", json={"order_id":1,"client_id":2,"delivery_date":"2025-10-25T10:00:00","status":"otro"})
    assert r2.status_code == 400 and r2.get_json()["error"]=="invalid_status"
    # invalid date
    r3 = client.post("/deliveries", json={"order_id":1,"client_id":2,"delivery_date":"BAD","status":"entregado"})
    assert r3.status_code == 400 and r3.get_json()["error"]=="invalid_date"
