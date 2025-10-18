import pytest
from app.modules.suppliers.service import SupplierService
from app.core.exceptions import ConflictError


class DummySupplier:
    def __init__(self, id=1, razon_social='X', nit='NIT1'):
        self.id = id
        self.razon_social = razon_social
        self.nit = nit
        self.certificado_path = '/tmp/cert'


class DummyRepo:
    def __init__(self):
        self.created = None

    def check_nit_exists(self, nit):
        return nit == 'EXISTS'

    def create(self, data, user):
        s = DummySupplier(id=10, razon_social=data.get('razon_social', 'X'), nit=data.get('nit'))
        self.created = s
        return s

    def get_by_id_or_fail(self, supplier_id):
        if supplier_id == 999:
            raise Exception('not found')
        return DummySupplier(id=supplier_id, razon_social='Found', nit='NITX')

    def update(self, supplier_id, data, user):
        return DummySupplier(id=supplier_id, razon_social=data.get('razon_social', 'Updated'))

    def delete(self, supplier_id, user, soft=True):
        return True

    def count(self):
        return 42

    def get_by_nit(self, nit):
        if nit == 'NFOUND':
            return None
        return DummySupplier(id=5, nit=nit)

    def search_suppliers(self, search, pais, status):
        return ['a', 'b']


def test_create_supplier_conflict(monkeypatch):
    svc = SupplierService()
    svc.repository = DummyRepo()
    data = {'nit': 'EXISTS', 'razon_social': 'C'}
    with pytest.raises(ConflictError):
        svc.create_supplier(data, certificado=None, user='u')


def test_create_supplier_success(monkeypatch):
    svc = SupplierService()
    svc.repository = DummyRepo()

    # avoid file processing
    monkeypatch.setattr(svc, '_process_certificate_file', lambda f: {
        'filename': 'cert.pdf', 'path': '/tmp/cert.pdf', 'mime_type': 'application/pdf', 'size': 123
    })

    data = {'nit': 'NEW', 'razon_social': 'New Co'}
    supplier = svc.create_supplier(data, certificado=object(), user='u')
    assert supplier.id == 10
    assert supplier.nit == 'NEW'


def test_update_and_delete_and_counts(monkeypatch):
    svc = SupplierService()
    svc.repository = DummyRepo()

    # update
    updated = svc.update_supplier(1, {'razon_social': 'R'}, certificado=None, user='u')
    assert updated.razon_social == 'R'

    # delete
    res = svc.delete_supplier(1, user='u')
    assert res is True

    # counts and get_by_nit
    assert svc.get_suppliers_count() == 42
    assert svc.get_by_nit('ABC').nit == 'ABC'
    assert svc.get_by_nit('NFOUND') is None
