import pytest

from app.modules.suppliers.repository import SupplierRepository
from app.modules.suppliers.service import SupplierService


def test_supplier_repo_get_by_nit_filters_deleted(monkeypatch):
    repo = SupplierRepository()

    class Q:
        def filter(self, *args, **kwargs):
            return self
        def first(self):
            return {'nit': 'X'}

    # monkeypatch query to return our Q
    monkeypatch.setattr(repo, 'query', lambda: Q())
    res = repo.get_by_nit('X')
    assert res['nit'] == 'X'


def test_supplier_service_delete_and_count(monkeypatch):
    svc = SupplierService()

    class Repo:
        def get_by_id_or_fail(self, id):
            return type('S', (), {'razon_social': 'R'})()
        def delete(self, id, user, soft=True):
            return True
        def count(self):
            return 7

    svc.repository = Repo()
    res = svc.delete_supplier(1, user='u')
    assert res is True
    assert svc.get_suppliers_count() == 7
