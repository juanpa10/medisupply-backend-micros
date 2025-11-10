def make_visit(client, vid=1001, cid=7, date="2025-10-25T09:00:00", clients=[10,20,30]):
    return client.post("/visits", json={
        "visit_id": vid, "commercial_id": cid, "date": date, "client_ids": clients
    })

def test_health(client):
    r = client.get("/health"); assert r.status_code==200 and r.get_json()["status"]=="ok"

def test_create_and_list(client):
    r = make_visit(client, vid=2001); assert r.status_code==201
    d = r.get_json(); assert d["id"]==2001 and len(d["stops"])==3 and d["stops"][0]["position"]==1
    # Segunda visita para probar paginación
    r2 = make_visit(client, vid=2002, clients=[40,50]); assert r2.status_code==201
    l = client.get("/visits?limit=1"); assert l.status_code==200
    payload = l.get_json(); assert "next_cursor" in payload
    if payload["next_cursor"]:
        l2 = client.get(f"/visits?limit=1&cursor={payload['next_cursor']}"); assert l2.status_code==200

def test_by_dates_and_errors(client):
    make_visit(client, vid=3001, date="2025-10-21T10:00:00")
    ok = client.get("/visits/by-dates?from=2025-10-20T00:00:00&to=2025-10-30T23:59:59")
    assert ok.status_code==200 and len(ok.get_json()["items"])>=1
    # fechas inválidas
    bad = client.get("/visits/by-dates?from=x&to=y"); assert bad.status_code==400
    # missing dates
    bad2 = client.get("/visits/by-dates?from=2025-10-20T00:00:00"); assert bad2.status_code==400

def test_by_commercial(client):
    make_visit(client, vid=4001, cid=8)
    make_visit(client, vid=4002, cid=8)
    r = client.get("/visits/by-commercial/8?limit=2"); assert r.status_code==200
    items = r.get_json()["items"]; assert all(v["commercial_id"]==8 for v in items)

#def test_missing_and_invalid_inputs(client):
#    r = client.post("/visits", json={"visit_id":1}); assert r.status_code==400
#    r2 = client.post("/visits", json={"visit_id":2,"commercial_id":3,"date":"X","client_ids":[1]})
#    assert r2.status_code==400 and r2.get_json()["error"]=="invalid_date"
#    r3 = client.post("/visits", json={"visit_id":3,"commercial_id":3,"date":"2025-10-21T00:00:00","client_ids":[]})
#    assert r3.status_code==400 and r3.get_json()["error"]=="invalid_clients"
