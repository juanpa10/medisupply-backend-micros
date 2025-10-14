import pytest

from app.modules.suppliers.service import SupplierService


def test_get_all_suppliers_delegates_to_repository():
    svc = SupplierService()

    class Repo:
        def search_suppliers(self, search, pais, status):
            return ['s1', 's2']

    svc.repository = Repo()
    res = svc.get_all_suppliers(search='term', pais='CO', status='active')
    assert res == ['s1', 's2']


def test_get_supplier_returns_repo_result():
    svc = SupplierService()

    class Repo:
        def get_by_id_or_fail(self, sid):
            return {'id': sid, 'name': 'X'}

    svc.repository = Repo()
    r = svc.get_supplier(5)
    assert r['id'] == 5


def test_get_by_nit_delegates():
    svc = SupplierService()

    class Repo:
        def get_by_nit(self, nit):
            if nit == 'N1':
                return {'nit': nit}
            return None

    svc.repository = Repo()
    assert svc.get_by_nit('N1')['nit'] == 'N1'
    assert svc.get_by_nit('NNO') is None
