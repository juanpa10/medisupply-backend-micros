import os
import sys
import types

def test_create_app_calls_init_db(monkeypatch):
    # prepare a fake init_db module to verify create_app calls it when INIT_DB=true
    fake = types.SimpleNamespace()
    called = {'ok': False}
    def fake_init_db(url=None):
        called['ok'] = True

    fake.init_db = fake_init_db
    sys.modules['init_db'] = fake

    # set env to trigger init
    monkeypatch.setenv('INIT_DB', 'true')

    # import factory and create app
    from app import create_app
    app = create_app()
    client = app.test_client()
    r = client.get('/health')
    assert r.status_code == 200
    # our fake init_db should have been called
    assert called['ok']
    # remove the fake so subsequent tests import the real module
    if 'init_db' in sys.modules:
        del sys.modules['init_db']


def test_init_db_runs_with_repo_stub(monkeypatch):
    # stub out Repo.insert_sales_bulk to avoid heavy DB work
    from app import create_app
    # ensure DB created
    monkeypatch.setenv('DATABASE_URL', 'sqlite:///reports_test_init.db')
    # stub
    import app.repositories.repo as repo_mod
    monkeypatch.setattr(repo_mod.Repo, 'insert_sales_bulk', lambda self, rows: None)

    import init_db
    # call the real init_db (Repo.insert_sales_bulk is stubbed)
    init_db.init_db()
    # if no exception, we consider it OK
