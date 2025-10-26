"""
Rutas simplificadas de inventario - Solo búsqueda por producto
"""
from flask import Blueprint
from app.modules.inventory.controller import InventoryController
from app.core.auth import require_auth

# Crear blueprint
inventory_bp = Blueprint('inventory', __name__, url_prefix='/api/v1/inventory')

# Inicializar controlador
controller = InventoryController()

# Ruta única: Búsqueda por producto
@inventory_bp.route('/search-product', methods=['GET'])
@require_auth
def search_by_product():
    """
    Buscar inventario por nombre, código o referencia del producto.
    
    Query params:
    - q: término de búsqueda (mínimo 2 caracteres)
    
    Ejemplo: GET /api/v1/inventory/search-product?q=paracetamol
    """
    return controller.search_by_product()
