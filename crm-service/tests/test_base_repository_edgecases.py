import pytest

from app.shared.base_repository import BaseRepository
from app.shared.base_model import BaseModel
from app.core.exceptions import NotFoundError


class DummyModel(BaseModel):
    def __init__(self, id=1, is_deleted=False, **kwargs):
        self.id = id
        self.is_deleted = is_deleted
        for k, v in kwargs.items():
            setattr(self, k, v)


def test_get_by_id_or_fail_raises_when_missing(monkeypatch):
    repo = BaseRepository(DummyModel)

    # Monkeypatch get_by_id to return None
    monkeypatch.setattr(repo, 'get_by_id', lambda _id, include_deleted=False: None)

    with pytest.raises(NotFoundError):
        repo.get_by_id_or_fail(5)


def test_update_sets_attributes_and_user(monkeypatch):
    repo = BaseRepository(DummyModel)

    instance = DummyModel(id=2, name='old')

    # monkeypatch get_by_id_or_fail to return our instance
    monkeypatch.setattr(repo, 'get_by_id_or_fail', lambda _id: instance)

    # monkeypatch db commit/refresh
    monkeypatch.setattr('app.config.database.db.session.commit', lambda: None)
    monkeypatch.setattr('app.config.database.db.session.refresh', lambda x: None)

    updated = repo.update(2, {'name': 'new', 'missing': 'x'}, user='u')
    assert updated.name == 'new'
    assert hasattr(updated, 'updated_by') and updated.updated_by == 'u'

import pytest

from app.shared.base_repository import BaseRepository
from app.core.exceptions import NotFoundError


class M:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.is_deleted = False


def test_get_by_id_or_fail_raises(monkeypatch):
    repo = BaseRepository(M)
    # monkeypatch get_by_id to return None
    monkeypatch.setattr(repo, 'get_by_id', lambda id, include_deleted=False: None)
    with pytest.raises(NotFoundError):
        repo.get_by_id_or_fail(1)


def test_update_copies_attributes(monkeypatch, app):
    repo = BaseRepository(M)

    # provide instance via get_by_id_or_fail
    instance = M(id=1, name='old')
    monkeypatch.setattr(repo, 'get_by_id_or_fail', lambda id: instance)

    # monkeypatch the db used by BaseRepository to avoid needing Flask app context
    class S:
        def __init__(self):
            self.committed = False
        def commit(self):
            self.committed = True
        def refresh(self, obj):
            pass

    import app.shared.base_repository as br
    # replace the db object in the base_repository module with a dummy
    import app.shared.base_repository as br
    class DummySession:
        def commit(self):
            return None
        def refresh(self, obj):
            return None

    dummy_db = type('DB', (), {'session': DummySession()})()
    monkeypatch.setattr(br, 'db', dummy_db, raising=True)
    # avoid calling real commit during unit test
    monkeypatch.setattr(br, '_commit_session', lambda: None, raising=True)

    out = repo.update(1, {'name': 'new', 'ignored': 'x'}, user='u')
    assert out.name == 'new'
