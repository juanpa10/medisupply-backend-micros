from datetime import datetime, UTC
from app.shared.base_model import BaseModel
from app.modules.suppliers.models import Supplier


def test_soft_delete_and_restore(db):
    # create a supplier via model directly
    s = Supplier(
        razon_social='X', nit='NIT-X', representante_legal='R', pais='Col',
        nombre_contacto='C', celular_contacto='300', certificado_filename='f', certificado_path='/tmp/f'
    )
    db.session.add(s)
    db.session.commit()

    assert not s.is_deleted

    s.soft_delete(user='tester')
    assert s.is_deleted is True
    assert s.deleted_by == 'tester'
    assert s.deleted_at is not None

    s.restore()
    assert s.is_deleted is False
    assert s.deleted_at is None
    assert s.deleted_by is None


def test_to_dict_and_repr(db):
    s = Supplier(
        razon_social='Y', nit='NIT-Y', representante_legal='R', pais='Col',
        nombre_contacto='C', celular_contacto='300', certificado_filename='f', certificado_path='/tmp/f'
    )
    db.session.add(s)
    db.session.commit()

    d = s.to_dict()
    assert 'id' in d
    assert 'razon_social' in d
    assert isinstance(str(s), str)


def test_to_dict_with_datetime_values(db):
    """Test to_dict convierte datetime a ISO format correctamente"""
    s = Supplier(
        razon_social='Z', nit='NIT-Z', representante_legal='R', pais='Col',
        nombre_contacto='C', celular_contacto='300', certificado_filename='f', certificado_path='/tmp/f'
    )
    db.session.add(s)
    db.session.commit()

    # Forzar un datetime en created_at
    s.created_at = datetime.now(UTC)
    db.session.commit()

    d = s.to_dict()
    
    # Verificar que created_at fue convertido a string ISO
    assert 'created_at' in d
    assert isinstance(d['created_at'], str)
    assert 'T' in d['created_at']  # Formato ISO incluye T


def test_to_dict_with_all_field_types(db):
    """Test to_dict con diferentes tipos de valores"""
    s = Supplier(
        razon_social='Test Dict', nit='NIT-DICT', representante_legal='Rep', 
        pais='Colombia',
        nombre_contacto='Contact', celular_contacto='123456', 
        certificado_filename='cert.pdf', certificado_path='/path/cert.pdf',
        email='test@test.com',  # String
        telefono='555-1234',  # String
        sitio_web='http://test.com'  # String
    )
    db.session.add(s)
    db.session.commit()

    d = s.to_dict()
    
    # Verificar campos string
    assert d['email'] == 'test@test.com'
    assert d['telefono'] == '555-1234'
    assert d['sitio_web'] == 'http://test.com'
    
    # Verificar campos integer
    assert isinstance(d['id'], int)
    
    # Verificar que to_dict funciona sin errores
    assert 'razon_social' in d
    assert 'nit' in d


def test_repr_with_id(db):
    """Test __repr__ incluye información del supplier"""
    s = Supplier(
        razon_social='Repr Test', nit='NIT-REPR', representante_legal='R', 
        pais='Col',
        nombre_contacto='C', celular_contacto='300', 
        certificado_filename='f', certificado_path='/tmp/f'
    )
    db.session.add(s)
    db.session.commit()

    repr_str = repr(s)
    
    # El repr de Supplier es '<Supplier razon_social - nit>'
    assert 'Supplier' in repr_str
    assert 'Repr Test' in repr_str or 'NIT-REPR' in repr_str
    assert '<' in repr_str
    assert '>' in repr_str
