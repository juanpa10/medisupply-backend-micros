import io, json, time
from app.services.evidence_service import PHOTO_MAX, VIDEO_MAX

def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"

def fake_file(size, byte=b"x"):
    return io.BytesIO(byte * size)

def upload(client, name, content, evidence_type="photo"):
    data = {
        "file": (content, name),
        "client_id": "C1",
        "product_id": "P1",
        "visit_id": "V1",
        "evidence_type": evidence_type,
        "lat": "4.65",
        "lon": "-74.05",
    }
    return client.post("/evidence/upload", data=data, content_type="multipart/form-data")

def test_photo_ok(client):
    r = upload(client, "ok.png", fake_file(1024), "photo")
    assert r.status_code == 201
    body = r.get_json()
    assert "Evidencia cargada correctamente" in body["message"]
    assert "url" in body

def test_video_ok(client):
    r = upload(client, "v.mp4", fake_file(1024*1024), "video")
    assert r.status_code == 201

def test_format_validation(client):
    r = upload(client, "bad.gif", fake_file(100), "photo")
    assert r.status_code == 400
    assert "Formato" in r.get_json()["error"]

def test_size_validation_photo(client):
    r = upload(client, "big.png", fake_file(PHOTO_MAX + 1), "photo")
    assert r.status_code == 400
    assert "grande" in r.get_json()["error"]

def test_size_validation_video(client):
    r = upload(client, "big.mp4", fake_file(VIDEO_MAX + 1), "video")
    assert r.status_code == 400
    assert "grande" in r.get_json()["error"]

def test_get_evidence_and_signed_url(client):
    r = upload(client, "ok.png", fake_file(2048), "photo")
    evid_id = r.get_json()["id"]

    r2 = client.get(f"/evidence/{evid_id}")
    assert r2.status_code == 200
    body = r2.get_json()
    sig_url = body["signed_url"]
    # try to fetch file using signed URL
    r3 = client.get(sig_url)
    assert r3.status_code == 200
    assert r3.data  # has bytes
