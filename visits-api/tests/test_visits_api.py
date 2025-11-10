def make_visit(client):
    return client.post("/visits", json={
        "visit_id":1001, "commercial_id":7, "date":"2025-10-25T09:00:00", "client_ids":[10,20,30]
    })

def test_health(client):
    r = client.get("/health"); assert r.status_code==200 and r.get_json()["status"]=="ok"

def test_create_and_list(client):
    r = make_visit(client); assert r.status_code==201
    d = r.get_json(); assert d["id"]==1001 and len(d["stops"])==3 and d["stops"][0]["position"]==1
    l = client.get("/visits?limit=10"); assert l.status_code==200 and len(l.get_json()["items"])>=1

def test_by_dates_and_errors(client):
    make_visit(client)
    ok = client.get("/visits/by-dates?from=2025-10-20T00:00:00&to=2025-10-30T23:59:59")
    assert ok.status_code==200 and len(ok.get_json()["items"])>=1
    bad = client.get("/visits/by-dates?from=x&to=y"); assert bad.status_code==400

def test_by_commercial(client):
    make_visit(client)
    r = client.get("/visits/by-commercial/7"); assert r.status_code==200
    items = r.get_json()["items"]; assert all(v["commercial_id"]==7 for v in items)

def test_missing_fields(client):
    r = client.post("/visits", json={"visit_id":1}); assert r.status_code==400
