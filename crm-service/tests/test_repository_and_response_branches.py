import pytest
from flask import Flask
from app.core.utils.response import success_response, error_response
from app.shared.base_repository import BaseRepository


class DummyModel:
    def __init__(self, id):
        self.id = id


class DummySession:
    def __init__(self):
        self.committed = False

    def add(self, obj):
        pass

    def commit(self):
        self.committed = True

    def delete(self, obj):
        pass


def test_base_repository_create_and_delete(monkeypatch):
    from app.config.database import db

    repo = BaseRepository(DummyModel)

    # patch db.session methods used by create
    class Sess:
        def __init__(self):
            self.committed = False
        def add(self, obj):
            self.added = obj
        def commit(self):
            self.committed = True
        def refresh(self, obj):
            self.refreshed = obj

    sess = Sess()
    monkeypatch.setattr(db, 'session', sess)

    # create with a mapping (dict) as expected by BaseRepository.create
    repo.create({'id': 1})
    assert db.session.committed is True

    # patch get_by_id_or_fail to return an object with soft_delete
    class Obj:
        def __init__(self):
            self.soft_deleted = False
        def soft_delete(self, user):
            self.soft_deleted = True

    monkeypatch.setattr(repo, 'get_by_id_or_fail', lambda id: Obj())
    # reset commit flag
    db.session.committed = False
    res = repo.delete(1)
    assert res is True
    assert db.session.committed is True


def test_make_and_error_response_branches():
    app = Flask(__name__)
    with app.test_request_context('/'):
        resp, status = success_response()
        assert status == 200
        e, status2 = error_response('oops', status_code=500)
        assert status2 == 500
        assert e.get_json()['message'] == 'oops'
