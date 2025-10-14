import os
import pytest

from app.modules.suppliers.service import SupplierService
from app.modules.suppliers.repository import SupplierRepository


def test_delete_certificate_nonexistent_logs(monkeypatch, tmp_path):
    svc = SupplierService()

    # simulate supplier with non-existing file
    class Repo:
        def get_by_id_or_fail(self, id):
            return type('S', (), {'certificado_path': str(tmp_path / 'nope.pdf'), 'razon_social': 'R'})()
        def delete(self, id, user, soft=True):
            return True

    svc.repository = Repo()

    # Should not raise even if file doesn't exist
    assert svc.delete_supplier(1, user='u') is True


def test_repo_has_exists_method():
    # Ensure the repository exposes an `exists` method (callable)
    assert hasattr(SupplierRepository, 'exists') and callable(getattr(SupplierRepository, 'exists'))
