import os, pytest, tempfile, shutil
from app.app import create_app
from app.db import Base, engine

@pytest.fixture()
def client(tmp_path):
    # temp dir for uploads
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    os.environ["UPLOAD_DIR"] = str(upload_dir)
    os.environ["SECRET_KEY"] = "testing-secret"
    app = create_app()
    app.config.update(TESTING=True)
    with app.test_client() as c:
        yield c
