import os, pytest, jwt, importlib.util, sys
from pathlib import Path

SECRET = os.getenv("JWT_SECRET", "supersecret")


def load_roles_app():
    root = Path(__file__).resolve().parents[1]
    # ensure the roles-api folder is on sys.path so `import app` works
    sys.path.insert(0, str(root))
    import importlib
    # Remove any previously loaded 'app' to avoid conflicts with other services
    if 'app' in sys.modules:
        del sys.modules['app']
    if 'app.app' in sys.modules:
        del sys.modules['app.app']
    mod = importlib.import_module('app.app')
    return mod.create_app


@pytest.fixture(scope="session")
def app():
    # ensure test DB file lives inside the roles-api folder (not repo root)
    root = Path(__file__).resolve().parents[1]
    db_file = root / "roles_simple_test.db"
    # convert to a file URL (sqlite:///C:/path/to/db)
    db_url = f"sqlite:///{db_file.resolve().as_posix()}"
    os.environ["DATABASE_URL"] = db_url
    os.environ["JWT_SECRET"] = SECRET
    create_app = load_roles_app()
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
