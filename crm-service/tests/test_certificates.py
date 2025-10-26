import io
from pathlib import Path
import pytest

from app.modules.suppliers.service import SupplierService
from app.modules.suppliers.controller import SupplierController


def test_normalize_file_path_relative():
    # Test que _normalize_file_path convierte ruta relativa a absoluta
    rel = "uploads/certificates/test.pdf"
    normalized = SupplierService._normalize_file_path(rel)

    # Debe ser ruta absoluta
    assert Path(normalized).is_absolute()
    # Debe contener el directorio del proyecto
    assert "medisupply-backend-micros" in normalized or "crm-service" in normalized
    # Debe contener la ruta relativa
    assert "uploads" in normalized
    assert "certificates" in normalized


def test_get_supplier_certificate_returns_info(tmp_path, monkeypatch):
    # Crear archivo real
    uploads = tmp_path / "uploads" / "certificates"
    uploads.mkdir(parents=True)
    f = uploads / "supplier.pdf"
    f.write_bytes(b"pdf")

    # Mock repository to return a supplier with relative path
    supplier_obj = type("S", (), {
        'certificado_path': str(Path("uploads") / "certificates" / "supplier.pdf"),
        'certificado_filename': 'supplier.pdf',
        'certificado_mime_type': 'application/pdf',
        'certificado_size': f.stat().st_size,
        'razon_social': 'Test'
    })()

    svc = SupplierService()
    svc.repository = type('R', (), {'get_by_id_or_fail': lambda self, i: supplier_obj})()

    # Monkeypatch project root to tmp_path by changing __file__ resolution temporarily
    # We'll monkeypatch SupplierService._normalize_file_path to behave relative to tmp_path
    orig = SupplierService._normalize_file_path

    def fake_normalize(p):
        # If p is absolute return as-is
        pth = Path(p)
        if pth.is_absolute():
            return str(pth.resolve())
        return str((tmp_path / p).resolve())

    monkeypatch.setattr(SupplierService, '_normalize_file_path', staticmethod(fake_normalize))

    info = svc.get_supplier_certificate(1)

    assert info['filename'] == 'supplier.pdf'
    assert info['mime_type'] == 'application/pdf'
    assert Path(info['path']).exists()

    # restore
    monkeypatch.setattr(SupplierService, '_normalize_file_path', orig)


def test_delete_certificate_file_removes(tmp_path, monkeypatch):
    uploads = tmp_path / "uploads" / "certificates"
    uploads.mkdir(parents=True)
    f = uploads / "toremove.pdf"
    f.write_bytes(b"x")

    svc = SupplierService()
    
    # Monkeypatch _normalize_file_path para que resuelva desde tmp_path
    def fake_normalize(p):
        pth = Path(p)
        if pth.is_absolute():
            return str(pth.resolve())
        return str((tmp_path / p).resolve())
    
    monkeypatch.setattr(SupplierService, '_normalize_file_path', staticmethod(fake_normalize))
    
    # call with relative path
    svc._delete_certificate_file(str(Path("uploads") / "certificates" / "toremove.pdf"))

    assert not f.exists()


def test_controller_get_certificate_send_file(client, app, monkeypatch, tmp_path):
    # Crear archivo
    uploads = tmp_path / "uploads" / "certificates"
    uploads.mkdir(parents=True)
    f = uploads / "dl.pdf"
    f.write_bytes(b"pdfdata")

    # Mock service method to return file info
    monkeypatch.setattr('app.modules.suppliers.controller.SupplierService.get_supplier_certificate',
                        lambda self, sid: {
                            'path': str(f.resolve()),
                            'filename': 'dl.pdf',
                            'mime_type': 'application/pdf',
                            'size': f.stat().st_size
                        })

    controller = SupplierController()

    with app.test_request_context('/api/v1/suppliers/1/certificate'):
        resp = controller.get_certificate(1)

    # send_file should return a Flask response
    status = getattr(resp, 'status_code', None)
    assert status == 200
    cd = resp.headers.get('Content-Disposition', '')
    assert 'attachment' in cd
    assert 'dl.pdf' in cd


def test_controller_get_certificate_file_not_found(client, app, monkeypatch):
    # Mock service to raise FileNotFoundError
    def raise_fnf(self, sid):
        raise FileNotFoundError("File not found")
    
    monkeypatch.setattr('app.modules.suppliers.controller.SupplierService.get_supplier_certificate', raise_fnf)

    controller = SupplierController()

    with app.test_request_context('/api/v1/suppliers/1/certificate'):
        resp = controller.get_certificate(1)

    if isinstance(resp, tuple):
        response, status = resp
    else:
        response = resp
        status = getattr(response, 'status_code', None)

    assert status == 404


def test_controller_get_certificate_general_error(client, app, monkeypatch):
    # Mock service to raise generic exception
    def raise_exc(self, sid):
        raise RuntimeError("Something went wrong")
    
    monkeypatch.setattr('app.modules.suppliers.controller.SupplierService.get_supplier_certificate', raise_exc)

    controller = SupplierController()

    with app.test_request_context('/api/v1/suppliers/1/certificate'):
        resp = controller.get_certificate(1)

    if isinstance(resp, tuple):
        response, status = resp
    else:
        response = resp
        status = getattr(response, 'status_code', None)

    assert status == 500

