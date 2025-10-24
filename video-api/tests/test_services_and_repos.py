import io, os
from app.services.evidence_service import EvidenceService, PHOTO_MAX
from app.repositories.evidence_repository import EvidenceRepository
from app.app import create_app

def test_service_validation_and_repo(client, tmp_path):
    app = create_app()
    repo = EvidenceRepository(app.session_factory)
    svc = EvidenceService(repo, os.environ["UPLOAD_DIR"], "secret")

    # ok
    res = svc.save_upload(io.BytesIO(b"hi"), "x.png", 2, {
        "content_type":"image/png","client_id":"C1","product_id":"P1","visit_id":"V1","evidence_type":"photo"
    })
    assert res.id > 0 and res.url

    # bad format
    try:
        svc.save_upload(io.BytesIO(b"hi"), "x.gif", 2, {
            "content_type":"image/gif","client_id":"C1","product_id":"P1","visit_id":"V1","evidence_type":"photo"
        })
        assert False, "should fail"
    except ValueError as e:
        assert "Formato" in str(e)
