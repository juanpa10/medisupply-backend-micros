"""
Rutas (Blueprint) para el módulo de Suppliers
"""
from flask import Blueprint
from app.modules.suppliers.controller import SupplierController
from app.core.auth.decorators import require_auth

# Crear blueprint
suppliers_bp = Blueprint('suppliers', __name__)

# Instanciar controlador
controller = SupplierController()


# Rutas
@suppliers_bp.route('', methods=['POST'])
@require_auth
def create_supplier():
    """Crear un nuevo proveedor"""
    return controller.create()


@suppliers_bp.route('', methods=['GET'])
@require_auth
def get_suppliers():
    """Obtener todos los proveedores"""
    return controller.get_all()


@suppliers_bp.route('/stats', methods=['GET'])
@require_auth
def get_suppliers_stats():
    """Obtener estadísticas de proveedores"""
    return controller.get_stats()


@suppliers_bp.route('/<int:supplier_id>', methods=['GET'])
@require_auth
def get_supplier(supplier_id):
    """Obtener un proveedor por ID"""
    return controller.get_one(supplier_id)


@suppliers_bp.route('/<int:supplier_id>', methods=['PUT'])
@require_auth
def update_supplier(supplier_id):
    """Actualizar un proveedor"""
    return controller.update(supplier_id)


@suppliers_bp.route('/<int:supplier_id>', methods=['DELETE'])
@require_auth
def delete_supplier(supplier_id):
    """Eliminar un proveedor"""
    return controller.delete(supplier_id)
