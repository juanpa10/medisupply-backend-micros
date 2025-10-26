"""
Controlador simplificado de inventario - Búsqueda por producto
"""
from flask import request
from app.modules.inventory.service import InventoryService
from app.core.utils.response import success_response, error_response
from app.core.exceptions import BusinessError
from app.core.utils.logger import get_logger

logger = get_logger(__name__)


class InventoryController:
    """
    Controlador de inventario - Solo búsqueda por producto
    """
    
    def __init__(self):
        self.service = InventoryService()
    
    def search_by_product(self):
        """
        GET /api/v1/inventory/search-product?q=<query>
        
        Busca inventario por nombre, código o referencia del producto.
        
        Query params:
        - q: texto a buscar (mínimo 2 caracteres)
        
        Returns:
        - Lista de items de inventario con información del producto incluida
        
        Example Response:
        {
            "success": true,
            "message": "1 producto(s) encontrado(s) en inventario",
            "data": [
                {
                    "id": 1,
                    "product_id": 1,
                    "pasillo": "A",
                    "estanteria": "01",
                    "nivel": "1",
                    "ubicacion": "Pasillo A - Estantería 01 - Nivel 1",
                    "cantidad": 500.0,
                    "status": "available",
                    "created_at": "2025-10-25T22:14:26.624176",
                    "updated_at": null,
                    "product_info": {
                        "nombre": "Paracetamol 500mg",
                        "codigo": "MED-001",
                        "referencia": "REF-PARA-500",
                        "descripcion": "Analgésico y antipirético",
                        "categoria": "Medicamentos",
                        "unidad_medida": "tableta",
                        "proveedor": "Farmacéutica XYZ"
                    }
                }
            ]
        }
        """
        try:
            search_query = request.args.get('q', '').strip()
            
            # Validar que el query no esté vacío
            if not search_query:
                return error_response(
                    message='Debe proporcionar un término de búsqueda (parámetro "q")',
                    status_code=400
                )
            
            # Validar longitud mínima
            if len(search_query) < 2:
                return error_response(
                    message='El término de búsqueda debe tener al menos 2 caracteres',
                    status_code=400
                )
            
            # Ejecutar búsqueda
            results = self.service.search_by_product_query(search_query)
            
            return success_response(
                data=results,
                message=f'{len(results)} producto(s) encontrado(s) en inventario'
            )
            
        except BusinessError as e:
            return error_response(message=str(e), status_code=400)
        except Exception as e:
            logger.error(f"Error en búsqueda por producto: {str(e)}")
            return error_response(
                message='Error al buscar productos en inventario',
                status_code=500
            )
