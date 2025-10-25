import os
import importlib
import pytest
from types import SimpleNamespace
from app import db as db_mod
from app.app import create_app
from sqlalchemy.exc import IntegrityError


def test_db_url_selects_postgres_when_env_set(monkeypatch):
    # simulate env vars for a postgres DB
    monkeypatch.setenv('DATABASE_URL', '')
    monkeypatch.setenv('DB_HOST', 'db.local')
    monkeypatch.setenv('POSTGRES_USER', 'u')
    monkeypatch.setenv('POSTGRES_PASSWORD', 'p')
    monkeypatch.setenv('POSTGRES_DB', 'orders')
    monkeypatch.setenv('DB_PORT', '5433')

    import importlib
    importlib.reload(db_mod)
    url = db_mod.DB_URL
    assert 'postgresql' in url
    assert 'db.local' in url


def test_create_app_handles_inspect_exception(monkeypatch):
    # Ensure the engine uses a local sqlite DB for this test so create_all won't
    # attempt to connect to any external postgres host (the previous test may
    # have configured DB_HOST). Force DATABASE_URL to sqlite for isolation.
    monkeypatch.setenv('DATABASE_URL', 'sqlite:///orders_test.db')
    importlib.reload(db_mod)

    def fake_inspect(e):
        raise Exception('inspect-failed')

    from sqlalchemy import inspect
    monkeypatch.setattr('sqlalchemy.inspect', fake_inspect)

    # reload app to pick up monkeypatched inspect behavior and new engine
    import app.app as app_mod
    importlib.reload(app_mod)
    a = app_mod.create_app({'SEED': False})
    assert a is not None


def test_commit_integrity_error_propagates(monkeypatch):
    # simulate commit raising IntegrityError to ensure repo.create_order propagates
    from app.repositories.repo import Repo
    r = Repo()
    orig_commit = r.session.commit

    def bad_commit():
        raise IntegrityError(statement=None, params=None, orig=Exception('dup'))

    monkeypatch.setattr(r.session, 'commit', bad_commit)
    # first create should raise IntegrityError from commit
    try:
        with pytest.raises(IntegrityError):
            r.create_order('c-err', 'C-1')
    finally:
        # restore
        monkeypatch.setattr(r.session, 'commit', orig_commit)
