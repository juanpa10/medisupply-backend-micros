"""
Rutas de inventario
"""
from flask import Blueprint
from app.modules.inventory.controller import InventoryController
from app.core.auth import require_auth

# Crear blueprint
inventory_bp = Blueprint('inventory', __name__, url_prefix='/api/v1/inventory')

# Inicializar controlador
controller = InventoryController()

# Rutas CRUD básicas
@inventory_bp.route('', methods=['POST'])
@require_auth
def create_item():
    """Crear nuevo item de inventario"""
    return controller.create_item()

@inventory_bp.route('/<int:item_id>', methods=['GET'])
@require_auth
def get_item(item_id):
    """Obtener item por ID"""
    return controller.get_item(item_id)

@inventory_bp.route('/<int:item_id>', methods=['PUT'])
@require_auth
def update_item(item_id):
    """Actualizar item"""
    return controller.update_item(item_id)

@inventory_bp.route('/<int:item_id>', methods=['DELETE'])
@require_auth
def delete_item(item_id):
    """Eliminar item"""
    return controller.delete_item(item_id)

# Búsqueda
@inventory_bp.route('/search', methods=['GET'])
@require_auth
def search_inventory():
    """Buscar items de inventario"""
    return controller.search_inventory()

@inventory_bp.route('/search-product', methods=['GET'])
# @require_auth
def search_by_product():
    """
    Buscar inventario por nombre, código o referencia del producto.
    
    Query params:
    - q: término de búsqueda (mínimo 2 caracteres)
    - bodega_id: filtrar por bodega específica (opcional)
    
    Ejemplo: GET /api/v1/inventory/search-product?q=paracetamol&bodega_id=1
    """
    return controller.search_by_product()

# Localización de productos (HU-22)
@inventory_bp.route('/product/<int:product_id>/location', methods=['GET'])
@require_auth
def find_product_location(product_id):
    """Localizar producto en bodegas (<1 segundo)"""
    return controller.find_product_location(product_id)

# Operaciones de stock
@inventory_bp.route('/<int:item_id>/adjust', methods=['POST'])
@require_auth
def adjust_stock(item_id):
    """Ajustar stock (entrada/salida)"""
    return controller.adjust_stock(item_id)

@inventory_bp.route('/<int:item_id>/reserve', methods=['POST'])
@require_auth
def reserve_stock(item_id):
    """Reservar stock"""
    return controller.reserve_stock(item_id)

@inventory_bp.route('/<int:item_id>/release', methods=['POST'])
@require_auth
def release_stock(item_id):
    """Liberar stock reservado"""
    return controller.release_stock(item_id)

# Actualización de ubicación
@inventory_bp.route('/<int:item_id>/location', methods=['PUT'])
@require_auth
def update_location(item_id):
    """Actualizar ubicación física"""
    return controller.update_location(item_id)

# Alertas
@inventory_bp.route('/alerts/low-stock', methods=['GET'])
@require_auth
def get_low_stock_alerts():
    """Obtener items con stock bajo"""
    return controller.get_low_stock_alerts()

@inventory_bp.route('/alerts/expiring', methods=['GET'])
@require_auth
def get_expiring_soon():
    """Obtener items próximos a vencer"""
    return controller.get_expiring_soon()

# Movimientos
@inventory_bp.route('/movements', methods=['GET'])
@require_auth
def get_movements():
    """Obtener historial de movimientos"""
    return controller.get_movements()
