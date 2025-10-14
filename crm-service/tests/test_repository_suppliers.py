import pytest
from app.modules.suppliers.models import Supplier
from app.modules.suppliers.repository import SupplierRepository


def make_supplier_dict(nit_suffix='1'):
    return {
        'razon_social': f'Proveedor {nit_suffix}',
        'nit': f'NIT-{nit_suffix}',
        'representante_legal': 'Rep Legal',
        'pais': 'Colombia',
        'nombre_contacto': 'Contacto',
        'celular_contacto': '3001234567',
        'certificado_filename': 'cert.pdf',
        'certificado_path': '/tmp/cert.pdf',
        'status': 'active'
    }


def test_get_by_nit_and_check_exists(db):
    repo = SupplierRepository()
    sdata = make_supplier_dict('A')
    s = repo.create(sdata, user='tester')

    found = repo.get_by_nit(s.nit)
    assert found is not None
    assert found.nit == s.nit

    # exists should be true
    assert repo.check_nit_exists(s.nit) is True
    # excluding the same id should return False
    assert repo.check_nit_exists(s.nit, exclude_id=s.id) is False


def test_search_filters_and_status(db):
    repo = SupplierRepository()
    # create two suppliers in different countries and statuses
    data1 = make_supplier_dict('B')
    data2 = make_supplier_dict('C')
    data2['pais'] = 'Peru'
    data2['status'] = 'inactive'

    s1 = repo.create(data1, user='u')
    s2 = repo.create(data2, user='u')

    # search by partial razon_social
    q = repo.search_suppliers(search_term='Proveedor')
    results = q.all()
    assert len(results) >= 2

    # filter by country
    by_country = repo.get_suppliers_by_country('Peru')
    assert any(x.id == s2.id for x in by_country)

    # active suppliers
    active = repo.get_active_suppliers()
    assert all(x.status == 'active' for x in active)


def test_get_by_nit_include_deleted(db):
    repo = SupplierRepository()
    data = make_supplier_dict('D')
    s = repo.create(data, user='u')

    # soft delete via repository (keeps logic consistent)
    repo.delete(s.id, user='u', soft=True)

    # get_by_nit without include_deleted should normally return None
    found_no = repo.get_by_nit(s.nit, include_deleted=False)
    assert found_no is None

    # Using include_deleted True should return the soft-deleted record
    found_yes = repo.get_by_nit(s.nit, include_deleted=True)
    assert found_yes is not None
    assert found_yes.nit == s.nit
