"""
Controlador de inventario - Maneja HTTP requests
"""
from flask import request, g
from marshmallow import ValidationError as MarshmallowValidationError
from app.modules.inventory.service import InventoryService
from app.modules.inventory.schemas import (
    InventoryItemCreateSchema,
    InventoryItemUpdateSchema,
    InventorySearchSchema,
    InventoryLocationUpdateSchema,
    InventoryAdjustmentSchema,
    InventoryReservationSchema,
    MovementSearchSchema
)
from app.core.utils.response import success_response, error_response, paginated_response
from app.core.utils.pagination import get_pagination_params, paginate_query
from app.core.exceptions import ValidationError, ResourceNotFoundError, BusinessError
from app.core.utils.logger import get_logger
from decimal import Decimal

logger = get_logger(__name__)


class InventoryController:
    """
    Controlador de inventario
    
    Maneja validación de requests y formateo de responses
    para operaciones de inventario
    """
    
    def __init__(self):
        self.service = InventoryService()
        self.create_schema = InventoryItemCreateSchema()
        self.update_schema = InventoryItemUpdateSchema()
        self.search_schema = InventorySearchSchema()
        self.location_schema = InventoryLocationUpdateSchema()
        self.adjustment_schema = InventoryAdjustmentSchema()
        self.reservation_schema = InventoryReservationSchema()
        self.movement_search_schema = MovementSearchSchema()
    
    def create_item(self):
        """
        POST /api/v1/inventory
        
        Crea un nuevo item de inventario
        """
        try:
            data = self.create_schema.load(request.json)
            
            # Obtener usuario del contexto
            user = getattr(g, 'user', {})
            data['usuario_id'] = user.get('id')
            data['usuario_nombre'] = user.get('username')
            
            item = self.service.create_inventory_item(data)
            
            logger.info(f"Item de inventario creado: {item.id}")
            
            return success_response(
                data=item.to_dict(),
                message='Item de inventario creado exitosamente',
                status_code=201
            )
            
        except MarshmallowValidationError as e:
            logger.warning(f"Validación fallida: {e.messages}")
            return error_response(
                message='Datos de entrada inválidos',
                errors=e.messages,
                status_code=400
            )
        except ValidationError as e:
            logger.warning(f"Error de validación: {str(e)}")
            return error_response(message=str(e), status_code=400)
        except Exception as e:
            logger.error(f"Error al crear item: {str(e)}")
            return error_response(
                message='Error al crear item de inventario',
                status_code=500
            )
    
    def get_item(self, item_id: int):
        """
        GET /api/v1/inventory/<id>
        
        Obtiene un item de inventario por ID
        """
        try:
            item = self.service.repo.get_by_id(item_id)
            if not item:
                raise ResourceNotFoundError(f"Item {item_id} no encontrado")
            
            return success_response(data=item.to_dict())
            
        except ResourceNotFoundError as e:
            return error_response(message=str(e), status_code=404)
        except Exception as e:
            logger.error(f"Error al obtener item: {str(e)}")
            return error_response(
                message='Error al obtener item',
                status_code=500
            )
    
    def update_item(self, item_id: int):
        """
        PUT /api/v1/inventory/<id>
        
        Actualiza un item de inventario
        """
        try:
            data = self.update_schema.load(request.json)
            item = self.service.update_inventory_item(item_id, data)
            
            logger.info(f"Item actualizado: {item_id}")
            
            return success_response(
                data=item.to_dict(),
                message='Item actualizado exitosamente'
            )
            
        except MarshmallowValidationError as e:
            return error_response(
                message='Datos inválidos',
                errors=e.messages,
                status_code=400
            )
        except ResourceNotFoundError as e:
            return error_response(message=str(e), status_code=404)
        except Exception as e:
            logger.error(f"Error al actualizar item: {str(e)}")
            return error_response(
                message='Error al actualizar item',
                status_code=500
            )
    
    def delete_item(self, item_id: int):
        """
        DELETE /api/v1/inventory/<id>
        
        Elimina un item de inventario
        """
        try:
            self.service.delete_inventory_item(item_id)
            
            return success_response(
                message='Item eliminado exitosamente',
                status_code=200
            )
            
        except ResourceNotFoundError as e:
            return error_response(message=str(e), status_code=404)
        except BusinessError as e:
            return error_response(message=str(e), status_code=400)
        except Exception as e:
            logger.error(f"Error al eliminar item: {str(e)}")
            return error_response(
                message='Error al eliminar item',
                status_code=500
            )
    
    def search_inventory(self):
        """
        GET /api/v1/inventory/search
        
        Busca items de inventario con filtros
        """
        try:
            params = self.search_schema.load(request.args)
            
            items = self.service.repo.search_inventory(
                product_id=params.get('product_id'),
                bodega_id=params.get('bodega_id'),
                lote=params.get('lote'),
                status=params.get('status'),
                pasillo=params.get('pasillo'),
                estanteria=params.get('estanteria'),
                nivel=params.get('nivel'),
                stock_bajo=params.get('stock_bajo', False)
            )
            
            # Paginar resultados
            page = params.get('page', 1)
            per_page = params.get('per_page', 20)
            
            paginated = paginate_query(items, page, per_page)
            
            return paginated_response(
                items=[item.to_dict() for item in paginated['items']],
                total=paginated['total'],
                page=paginated['page'],
                per_page=paginated['per_page']
            )
            
        except MarshmallowValidationError as e:
            return error_response(
                message='Parámetros inválidos',
                errors=e.messages,
                status_code=400
            )
        except Exception as e:
            logger.error(f"Error en búsqueda: {str(e)}")
            return error_response(
                message='Error en búsqueda de inventario',
                status_code=500
            )
    
    def find_product_location(self, product_id: int):
        """
        GET /api/v1/inventory/product/<product_id>/location
        
        Localiza un producto en todas las bodegas (HU-22)
        Optimizado para < 1 segundo
        """
        try:
            items = self.service.find_product_location(product_id)
            
            if not items:
                return success_response(
                    data=[],
                    message=f'Producto {product_id} no encontrado en inventario'
                )
            
            return success_response(
                data=[item.to_dict() for item in items],
                message=f'Producto encontrado en {len(items)} ubicación(es)'
            )
            
        except Exception as e:
            logger.error(f"Error al localizar producto: {str(e)}")
            return error_response(
                message='Error al localizar producto',
                status_code=500
            )
    
    def adjust_stock(self, item_id: int):
        """
        POST /api/v1/inventory/<id>/adjust
        
        Ajusta el stock de un item (entrada/salida)
        """
        try:
            data = self.adjustment_schema.load(request.json)
            
            user = getattr(g, 'user', {})
            
            item = self.service.adjust_stock(
                item_id=item_id,
                cantidad=Decimal(str(data['cantidad'])),
                tipo=data['tipo'],
                motivo=data.get('motivo'),
                documento_referencia=data.get('documento_referencia'),
                usuario_id=user.get('id'),
                usuario_nombre=user.get('username')
            )
            
            return success_response(
                data=item.to_dict(),
                message='Stock ajustado exitosamente'
            )
            
        except MarshmallowValidationError as e:
            return error_response(
                message='Datos inválidos',
                errors=e.messages,
                status_code=400
            )
        except ResourceNotFoundError as e:
            return error_response(message=str(e), status_code=404)
        except BusinessError as e:
            return error_response(message=str(e), status_code=400)
        except Exception as e:
            logger.error(f"Error al ajustar stock: {str(e)}")
            return error_response(
                message='Error al ajustar stock',
                status_code=500
            )
    
    def reserve_stock(self, item_id: int):
        """
        POST /api/v1/inventory/<id>/reserve
        
        Reserva stock para una orden
        """
        try:
            data = self.reservation_schema.load(request.json)
            
            item = self.service.reserve_stock(
                item_id=item_id,
                cantidad=Decimal(str(data['cantidad'])),
                motivo=data.get('motivo'),
                documento_referencia=data.get('documento_referencia')
            )
            
            return success_response(
                data=item.to_dict(),
                message='Stock reservado exitosamente'
            )
            
        except MarshmallowValidationError as e:
            return error_response(
                message='Datos inválidos',
                errors=e.messages,
                status_code=400
            )
        except ResourceNotFoundError as e:
            return error_response(message=str(e), status_code=404)
        except BusinessError as e:
            return error_response(message=str(e), status_code=400)
        except Exception as e:
            logger.error(f"Error al reservar stock: {str(e)}")
            return error_response(
                message='Error al reservar stock',
                status_code=500
            )
    
    def release_stock(self, item_id: int):
        """
        POST /api/v1/inventory/<id>/release
        
        Libera stock reservado
        """
        try:
            data = request.json or {}
            cantidad = Decimal(str(data.get('cantidad', 0)))
            
            item = self.service.release_stock(
                item_id=item_id,
                cantidad=cantidad,
                motivo=data.get('motivo')
            )
            
            return success_response(
                data=item.to_dict(),
                message='Stock liberado exitosamente'
            )
            
        except ResourceNotFoundError as e:
            return error_response(message=str(e), status_code=404)
        except Exception as e:
            logger.error(f"Error al liberar stock: {str(e)}")
            return error_response(
                message='Error al liberar stock',
                status_code=500
            )
    
    def update_location(self, item_id: int):
        """
        PUT /api/v1/inventory/<id>/location
        
        Actualiza la ubicación de un item
        """
        try:
            data = self.location_schema.load(request.json)
            
            item = self.service.update_location(
                item_id=item_id,
                pasillo=data['pasillo'],
                estanteria=data['estanteria'],
                nivel=data['nivel']
            )
            
            return success_response(
                data=item.to_dict(),
                message='Ubicación actualizada exitosamente'
            )
            
        except MarshmallowValidationError as e:
            return error_response(
                message='Datos inválidos',
                errors=e.messages,
                status_code=400
            )
        except ResourceNotFoundError as e:
            return error_response(message=str(e), status_code=404)
        except Exception as e:
            logger.error(f"Error al actualizar ubicación: {str(e)}")
            return error_response(
                message='Error al actualizar ubicación',
                status_code=500
            )
    
    def get_low_stock_alerts(self):
        """
        GET /api/v1/inventory/alerts/low-stock
        
        Obtiene items con stock bajo
        """
        try:
            bodega_id = request.args.get('bodega_id', type=int)
            items = self.service.get_low_stock_alerts(bodega_id)
            
            return success_response(
                data=[item.to_dict() for item in items],
                message=f'Se encontraron {len(items)} items con stock bajo'
            )
            
        except Exception as e:
            logger.error(f"Error al obtener alertas: {str(e)}")
            return error_response(
                message='Error al obtener alertas de stock',
                status_code=500
            )
    
    def get_expiring_soon(self):
        """
        GET /api/v1/inventory/alerts/expiring
        
        Obtiene items próximos a vencer
        """
        try:
            dias = request.args.get('dias', default=30, type=int)
            bodega_id = request.args.get('bodega_id', type=int)
            
            items = self.service.get_expiring_soon(dias, bodega_id)
            
            return success_response(
                data=[item.to_dict() for item in items],
                message=f'Se encontraron {len(items)} items próximos a vencer'
            )
            
        except Exception as e:
            logger.error(f"Error al obtener items por vencer: {str(e)}")
            return error_response(
                message='Error al obtener items por vencer',
                status_code=500
            )
    
    def get_movements(self):
        """
        GET /api/v1/inventory/movements
        
        Obtiene historial de movimientos
        """
        try:
            params = self.movement_search_schema.load(request.args)
            
            movements = self.service.movement_repo.search_movements(
                product_id=params.get('product_id'),
                bodega_id=params.get('bodega_id'),
                inventory_item_id=params.get('inventory_item_id'),
                tipo=params.get('tipo'),
                fecha_desde=params.get('fecha_desde'),
                fecha_hasta=params.get('fecha_hasta')
            )
            
            # Paginar
            page = params.get('page', 1)
            per_page = params.get('per_page', 20)
            
            paginated = paginate_query(movements, page, per_page)
            
            return paginated_response(
                items=[m.to_dict() for m in paginated['items']],
                total=paginated['total'],
                page=paginated['page'],
                per_page=paginated['per_page']
            )
            
        except MarshmallowValidationError as e:
            return error_response(
                message='Parámetros inválidos',
                errors=e.messages,
                status_code=400
            )
        except Exception as e:
            logger.error(f"Error al obtener movimientos: {str(e)}")
            return error_response(
                message='Error al obtener movimientos',
                status_code=500
            )
    
    def search_by_product(self):
        """
        GET /api/v1/inventory/search-product?q=<query>&bodega_id=<id>
        
        Busca inventario por nombre, código o referencia del producto.
        Utiliza JOIN con la tabla products para buscar por campos de producto.
        
        Query params:
        - q: texto a buscar (mínimo 2 caracteres)
        - bodega_id: filtrar por bodega específica (opcional)
        
        Returns:
        - Lista de items de inventario con información del producto incluida
        """
        try:
            search_query = request.args.get('q', '').strip()
            bodega_id = request.args.get('bodega_id', type=int)
            
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
            results = self.service.search_by_product_query(search_query, bodega_id)
            
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
