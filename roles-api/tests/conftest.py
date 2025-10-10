import os, pytest, jwt
from app.app import create_app

SECRET = os.getenv("JWT_SECRET", "supersecret")

@pytest.fixture(scope="session")
def app():
    # ensure test DB
    os.environ["DATABASE_URL"] = "sqlite:///roles_simple_test.db"
    os.environ["JWT_SECRET"] = SECRET
    app = create_app()
    app.testing = True
    return app

@pytest.fixture()
def client(app):
    return app.test_client()

def make_token(role="security_admin", sub="admin"):
    return jwt.encode({"sub": sub, "role": role}, SECRET, algorithm="HS256")

@pytest.fixture()
def admin_token():
    return make_token("security_admin")

@pytest.fixture()
def viewer_token():
    return make_token("viewer")
