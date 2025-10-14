from datetime import datetime
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
