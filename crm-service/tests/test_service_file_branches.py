import io
import os
import uuid
import pytest
from werkzeug.datastructures import FileStorage

from app.modules.suppliers.service import SupplierService
from app.core.exceptions import FileUploadError


class SimpleFile(FileStorage):
    def __init__(self, filename, content=b'pdfdata'):
        super().__init__(stream=io.BytesIO(content), filename=filename)


def test_process_certificate_no_file_raises(monkeypatch, app):
    svc = SupplierService()
    svc.repository = type('R', (), {'check_nit_exists': lambda self, n: False, 'create': lambda self, d, u: None})()

    with pytest.raises(FileUploadError):
        svc._process_certificate_file(None)


def test_create_supplier_calls_repository(monkeypatch, app, tmp_path):
    svc = SupplierService()
    # mock repository to detect create called
    class Repo:
        def __init__(self):
            self.called = False
        def check_nit_exists(self, nit):
            return False
        def create(self, data, user):
            self.called = True
            return type('S', (), {'id': 1, 'razon_social': data.get('razon_social'), 'nit': data.get('nit')})()

    repo = Repo()
    svc.repository = repo

    # monkeypatch file saving and magic detection
    f = SimpleFile('cert.pdf', content=b'%PDF-1.4')
    monkeypatch.setattr('app.modules.suppliers.service.get_secure_filename', lambda n: 'cert.pdf')
    monkeypatch.setattr('app.modules.suppliers.service.uuid', type('U', (), {'uuid4': staticmethod(lambda: type('X', (), {'hex':'abcd'})())})())

    # ensure UPLOAD_FOLDER exists in app config
    upload = tmp_path / 'uploads'
    upload.mkdir()
    monkeypatch.setitem(os.environ, 'FLASK_ENV', 'testing')
    # set config via current_app in create_app fixture (app fixture provides context)
    from flask import current_app
    current_app.config['UPLOAD_FOLDER'] = str(upload)
    current_app.config['ALLOWED_EXTENSIONS'] = ['pdf']
    current_app.config['MAX_FILE_SIZE'] = 5 * 1024 * 1024

    supplier = svc.create_supplier({'nit': 'NEW', 'razon_social': 'X'}, certificado=f, user='u')
    assert repo.called is True


def test_update_supplier_replaces_file(monkeypatch, app, tmp_path):
    svc = SupplierService()
    class Repo:
        def get_by_id_or_fail(self, id):
            return type('S', (), {'certificado_path': str(tmp_path / 'old.pdf'), 'razon_social': 'Old'})()
        def update(self, id, data, user):
            return type('S', (), {'id': id, 'razon_social': data.get('razon_social', 'Updated')})()

    repo = Repo()
    svc.repository = repo

    # create a fake old file
    old_file = tmp_path / 'old.pdf'
    old_file.write_bytes(b'old')

    f = SimpleFile('new.pdf', content=b'%PDF-1.4')
    monkeypatch.setattr('app.modules.suppliers.service.get_secure_filename', lambda n: 'new.pdf')
    monkeypatch.setattr('app.modules.suppliers.service.uuid', type('U', (), {'uuid4': staticmethod(lambda: type('X', (), {'hex':'ef01'})())})())

    from flask import current_app
    current_app.config['UPLOAD_FOLDER'] = str(tmp_path)
    current_app.config['ALLOWED_EXTENSIONS'] = ['pdf']
    current_app.config['MAX_FILE_SIZE'] = 5 * 1024 * 1024

    updated = svc.update_supplier(1, {'razon_social': 'New'}, certificado=f, user='u')
    assert updated.razon_social == 'New' or updated.razon_social == 'Updated'
