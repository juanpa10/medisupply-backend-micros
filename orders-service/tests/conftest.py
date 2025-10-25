import sys
import os
import pytest

# Ensure tests can import the `app` package under orders-service
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.app import create_app
from app.db import Base, engine
import werkzeug

# Compatibility shim: newer Werkzeug versions may not expose __version__ which
# older Flask test helpers expect. Define it if missing so tests using
# app.test_client() don't fail.
if not hasattr(werkzeug, '__version__'):
    try:
        # Try to get version from importlib metadata as a fallback
        import importlib.metadata as _md
        werkzeug.__version__ = _md.version('werkzeug')
    except Exception:
        werkzeug.__version__ = '3.0.0'


@pytest.fixture
def app():
    cfg = {}
    # ensure fresh sqlite file-based DB used by default
    # drop and recreate to ensure schema matches models (handles previous runs)
    # Remove sqlite file if present to avoid leftover data between runs
    try:
        db_path = engine.url.database
        if db_path:
            if not os.path.isabs(db_path):
                db_path = os.path.join(ROOT, db_path)
            if os.path.exists(db_path):
                os.remove(db_path)
    except Exception:
        pass
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    a = create_app(cfg)
    yield a


@pytest.fixture
def client(app):
    return app.test_client()
