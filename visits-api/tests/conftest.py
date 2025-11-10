import os, pytest
from app.app import create_app
@pytest.fixture()
def client(tmp_path):
    os.environ["DATABASE_URL"] = f"sqlite:///{tmp_path}/test.db"
    app = create_app(); app.config.update(TESTING=True)
    with app.test_client() as c: yield c
