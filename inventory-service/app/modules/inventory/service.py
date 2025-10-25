"""
Servicio de negocio para gestión de inventario
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from app.modules.inventory.models import InventoryItem, InventoryMovement
from app.modules.inventory.repository import InventoryItemRepository, InventoryMovementRepository
from app.shared.enums import InventoryStatus, MovementType
from app.core.exceptions import ValidationError, ResourceNotFoundError, BusinessError
from app.core.utils.logger import get_logger
from app.config.database import db

logger = get_logger(__name__)


class InventoryService:
    """
    Servicio de negocio para gestión de inventario
    
    Maneja:
    - Stock y ubicación en bodega
    - Movimientos de inventario (entradas/salidas)
    - Reservas de stock
    - Alertas de stock bajo/alto
    """
    
    def __init__(self):
        self.repo = InventoryItemRepository()
        self.movement_repo = InventoryMovementRepository()
    
    def create_inventory_item(self, data: Dict[str, Any]) -> InventoryItem:
        """
        Crea un nuevo item de inventario
        
        Args:
            data: Datos del item
            
        Returns:
            Item creado
            
        Raises:
            ValidationError: Si ya existe un item para ese product_id/bodega/lote
        """
        product_id = data['product_id']
        bodega_id = data['bodega_id']
        lote = data.get('lote')
        
        # Verificar que no exista ya un item con los mismos datos
        existing = self.repo.get_by_product_and_bodega(product_id, bodega_id, lote)
        if existing:
            raise ValidationError(
                f"Ya existe un item de inventario para product_id={product_id}, "
                f"bodega_id={bodega_id}, lote={lote}"
            )
        
        # Calcular cantidad disponible
        cantidad = Decimal(str(data['cantidad']))
        cantidad_reservada = Decimal(str(data.get('cantidad_reservada', 0)))
        data['cantidad_disponible'] = cantidad - cantidad_reservada
        
        item = InventoryItem(**data)
        self.repo.create(item)
        
        logger.info(f"Item de inventario creado: product_id={product_id}, bodega={bodega_id}")
        
        # Registrar movimiento de entrada inicial
        if cantidad > 0:
            self._register_movement(
                item=item,
                tipo=MovementType.ENTRADA.value,
                cantidad=cantidad,
                cantidad_anterior=0,
                cantidad_nueva=cantidad,
                motivo="Entrada inicial de inventario",
                usuario_id=data.get('usuario_id'),
                usuario_nombre=data.get('usuario_nombre')
            )
        
        return item
    
    def update_inventory_item(self, item_id: int, data: Dict[str, Any]) -> InventoryItem:
        """
        Actualiza un item de inventario
        
        Args:
            item_id: ID del item
            data: Datos a actualizar
            
        Returns:
            Item actualizado
        """
        item = self.repo.get_by_id(item_id)
        if not item:
            raise ResourceNotFoundError(f"Item de inventario {item_id} no encontrado")
        
        self.repo.update(item, data)
        logger.info(f"Item de inventario {item_id} actualizado")
        
        return item
    
    def delete_inventory_item(self, item_id: int) -> bool:
        """
        Elimina (soft delete) un item de inventario
        
        Args:
            item_id: ID del item
            
        Returns:
            True si se eliminó
        """
        item = self.repo.get_by_id(item_id)
        if not item:
            raise ResourceNotFoundError(f"Item de inventario {item_id} no encontrado")
        
        if item.cantidad_reservada > 0:
            raise BusinessError(
                "No se puede eliminar un item con stock reservado. "
                "Primero libere las reservas."
            )
        
        self.repo.delete(item)
        logger.info(f"Item de inventario {item_id} eliminado")
        
        return True
    
    def find_product_location(self, product_id: int) -> List[InventoryItem]:
        """
        Localiza un producto en todas las bodegas (HU-22: < 1 segundo)
        
        Args:
            product_id: ID del producto a localizar
            
        Returns:
            Lista de ubicaciones donde está el producto
        """
        return self.repo.find_product_location(product_id)
    
    def adjust_stock(
        self,
        item_id: int,
        cantidad: Decimal,
        tipo: str,
        motivo: Optional[str] = None,
        documento_referencia: Optional[str] = None,
        usuario_id: Optional[int] = None,
        usuario_nombre: Optional[str] = None
    ) -> InventoryItem:
        """
        Ajusta el stock de un item (entrada/salida)
        
        Args:
            item_id: ID del item
            cantidad: Cantidad a ajustar
            tipo: Tipo de movimiento (entrada/salida/ajuste)
            motivo: Motivo del ajuste
            documento_referencia: Documento de referencia
            usuario_id: ID del usuario que realiza el ajuste
            usuario_nombre: Nombre del usuario
            
        Returns:
            Item actualizado
            
        Raises:
            BusinessError: Si no hay suficiente stock para salida
        """
        item = self.repo.get_by_id(item_id)
        if not item:
            raise ResourceNotFoundError(f"Item de inventario {item_id} no encontrado")
        
        cantidad_anterior = item.cantidad
        es_entrada = tipo in [
            MovementType.ENTRADA.value,
            MovementType.DEVOLUCION_CLIENTE.value
        ]
        
        if es_entrada:
            item.ajustar_cantidad(cantidad, es_entrada=True)
        else:
            # Validar que hay suficiente stock disponible
            if item.cantidad_disponible < cantidad:
                raise BusinessError(
                    f"Stock insuficiente. Disponible: {item.cantidad_disponible}, "
                    f"Solicitado: {cantidad}"
                )
            item.ajustar_cantidad(cantidad, es_entrada=False)
        
        cantidad_nueva = item.cantidad
        db.session.commit()
        
        logger.info(
            f"Stock ajustado - Item {item_id}: {cantidad_anterior} -> {cantidad_nueva} "
            f"({tipo})"
        )
        
        # Registrar movimiento
        self._register_movement(
            item=item,
            tipo=tipo,
            cantidad=cantidad,
            cantidad_anterior=cantidad_anterior,
            cantidad_nueva=cantidad_nueva,
            motivo=motivo,
            documento_referencia=documento_referencia,
            usuario_id=usuario_id,
            usuario_nombre=usuario_nombre
        )
        
        return item
    
    def reserve_stock(
        self,
        item_id: int,
        cantidad: Decimal,
        motivo: Optional[str] = None,
        documento_referencia: Optional[str] = None
    ) -> InventoryItem:
        """
        Reserva stock para una orden
        
        Args:
            item_id: ID del item
            cantidad: Cantidad a reservar
            motivo: Motivo de la reserva
            documento_referencia: Documento de referencia (ej: número de orden)
            
        Returns:
            Item actualizado
            
        Raises:
            BusinessError: Si no hay suficiente stock disponible
        """
        item = self.repo.get_by_id(item_id)
        if not item:
            raise ResourceNotFoundError(f"Item de inventario {item_id} no encontrado")
        
        if not item.reservar_stock(cantidad):
            raise BusinessError(
                f"Stock insuficiente para reservar. Disponible: {item.cantidad_disponible}, "
                f"Solicitado: {cantidad}"
            )
        
        db.session.commit()
        
        logger.info(
            f"Stock reservado - Item {item_id}: {cantidad} unidades "
            f"(Doc: {documento_referencia})"
        )
        
        return item
    
    def release_stock(
        self,
        item_id: int,
        cantidad: Decimal,
        motivo: Optional[str] = None
    ) -> InventoryItem:
        """
        Libera stock reservado
        
        Args:
            item_id: ID del item
            cantidad: Cantidad a liberar
            motivo: Motivo de la liberación
            
        Returns:
            Item actualizado
        """
        item = self.repo.get_by_id(item_id)
        if not item:
            raise ResourceNotFoundError(f"Item de inventario {item_id} no encontrado")
        
        item.liberar_stock(cantidad)
        db.session.commit()
        
        logger.info(f"Stock liberado - Item {item_id}: {cantidad} unidades")
        
        return item
    
    def update_location(
        self,
        item_id: int,
        pasillo: str,
        estanteria: str,
        nivel: str
    ) -> InventoryItem:
        """
        Actualiza la ubicación de un item en bodega
        
        Args:
            item_id: ID del item
            pasillo: Pasillo
            estanteria: Estantería
            nivel: Nivel
            
        Returns:
            Item actualizado
        """
        item = self.repo.get_by_id(item_id)
        if not item:
            raise ResourceNotFoundError(f"Item de inventario {item_id} no encontrado")
        
        item.actualizar_ubicacion(pasillo, estanteria, nivel)
        db.session.commit()
        
        logger.info(
            f"Ubicación actualizada - Item {item_id}: "
            f"Pasillo {pasillo}, Estantería {estanteria}, Nivel {nivel}"
        )
        
        return item
    
    def search_by_product_query(
        self,
        search_query: str,
        bodega_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Busca inventario por nombre, código o referencia del producto
        
        Args:
            search_query: Texto a buscar (nombre, código o referencia)
            bodega_id: Filtro opcional por bodega
            
        Returns:
            Lista de diccionarios con información de inventario y producto
        """
        if not search_query or len(search_query.strip()) < 2:
            raise ValidationError("La búsqueda debe tener al menos 2 caracteres")
        
        # Buscar con JOIN a tabla products
        results = self.repo.search_by_product_name_or_code(
            search_query=search_query.strip(),
            bodega_id=bodega_id
        )
        
        # Enriquecer respuesta con datos del producto
        enriched_results = []
        for inventory_item, product in results:
            item_dict = inventory_item.to_dict()
            
            # Agregar información del producto
            item_dict['product_info'] = {
                'nombre': product.nombre,
                'codigo': product.codigo,
                'referencia': product.referencia,
                'descripcion': product.descripcion,
                'categoria': product.categoria,
                'unidad_medida': product.unidad_medida,
                'proveedor': product.proveedor
            }
            
            enriched_results.append(item_dict)
        
        logger.info(
            f"Búsqueda de inventario completada: '{search_query}' - "
            f"{len(enriched_results)} resultados"
        )
        
        return enriched_results
    
    def get_low_stock_alerts(self, bodega_id: Optional[int] = None) -> List[InventoryItem]:
        """
        Obtiene items con stock bajo
        
        Args:
            bodega_id: Filtro opcional por bodega
            
        Returns:
            Lista de items con stock bajo
        """
        return self.repo.get_low_stock_items(bodega_id)
    
    def get_expiring_soon(
        self,
        dias: int = 30,
        bodega_id: Optional[int] = None
    ) -> List[InventoryItem]:
        """
        Obtiene items próximos a vencer
        
        Args:
            dias: Días de anticipación
            bodega_id: Filtro opcional por bodega
            
        Returns:
            Lista de items próximos a vencer
        """
        return self.repo.get_expiring_soon(dias, bodega_id)
    
    def get_movements_history(
        self,
        product_id: Optional[int] = None,
        inventory_item_id: Optional[int] = None,
        bodega_id: Optional[int] = None,
        tipo: Optional[str] = None,
        limit: int = 100
    ) -> List[InventoryMovement]:
        """
        Obtiene historial de movimientos
        
        Args:
            product_id: Filtro por producto
            inventory_item_id: Filtro por item específico
            bodega_id: Filtro por bodega
            tipo: Filtro por tipo de movimiento
            limit: Límite de resultados
            
        Returns:
            Lista de movimientos
        """
        if inventory_item_id:
            return self.movement_repo.get_by_inventory_item(inventory_item_id, limit)
        elif product_id:
            return self.movement_repo.get_by_product(product_id, limit)
        elif bodega_id:
            return self.movement_repo.get_recent_movements(bodega_id, limit)
        else:
            return self.movement_repo.get_recent_movements(None, limit)
    
    def _register_movement(
        self,
        item: InventoryItem,
        tipo: str,
        cantidad: Decimal,
        cantidad_anterior: Decimal,
        cantidad_nueva: Decimal,
        motivo: Optional[str] = None,
        documento_referencia: Optional[str] = None,
        usuario_id: Optional[int] = None,
        usuario_nombre: Optional[str] = None
    ) -> InventoryMovement:
        """
        Registra un movimiento de inventario (método interno)
        
        Args:
            item: Item de inventario
            tipo: Tipo de movimiento
            cantidad: Cantidad del movimiento
            cantidad_anterior: Cantidad antes del movimiento
            cantidad_nueva: Cantidad después del movimiento
            motivo: Motivo del movimiento
            documento_referencia: Documento de referencia
            usuario_id: ID del usuario
            usuario_nombre: Nombre del usuario
            
        Returns:
            Movimiento creado
        """
        movement = InventoryMovement(
            inventory_item_id=item.id,
            product_id=item.product_id,
            bodega_id=item.bodega_id,
            tipo=tipo,
            cantidad=cantidad,
            cantidad_anterior=cantidad_anterior,
            cantidad_nueva=cantidad_nueva,
            motivo=motivo,
            documento_referencia=documento_referencia,
            usuario_id=usuario_id,
            usuario_nombre=usuario_nombre,
            lote=item.lote,
            fecha_movimiento=datetime.utcnow()
        )
        
        self.movement_repo.create(movement)
        
        return movement
