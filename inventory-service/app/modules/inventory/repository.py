"""
Repositorio de inventario con búsqueda optimizada
"""
from typing import List, Optional, Tuple
from datetime import date, datetime
from sqlalchemy import or_, and_, func
from app.shared.base_repository import BaseRepository
from app.modules.inventory.models import InventoryItem, InventoryMovement
from app.modules.inventory.product_model import Product
from app.shared.enums import InventoryStatus, MovementType
from app.core.utils.logger import get_logger
from app.config.database import db

logger = get_logger(__name__)


class InventoryItemRepository(BaseRepository[InventoryItem]):
    """
    Repositorio de items de inventario con métodos optimizados
    
    Implementa búsqueda rápida (<1 segundo) por product_id, ubicación y lote
    para cumplir con HU-22: localizar producto en bodega
    """
    
    def __init__(self):
        super().__init__(InventoryItem)
    
    def get_by_product(self, product_id: int) -> Optional[InventoryItem]:
        """
        Obtiene primer item de inventario por product_id
        
        Args:
            product_id: ID del producto en products-service
            
        Returns:
            Item de inventario o None
        """
        return self.query().filter(
            InventoryItem.product_id == product_id
        ).first()
    
    def get_all_by_product(self, product_id: int) -> List[InventoryItem]:
        """
        Obtiene todos los items de inventario de un producto
        (puede haber múltiples ubicaciones para el mismo producto)
        
        Args:
            product_id: ID del producto
            
        Returns:
            Lista de items de inventario
        """
        return self.query().filter(
            InventoryItem.product_id == product_id
        ).order_by(
            InventoryItem.pasillo,
            InventoryItem.estanteria,
            InventoryItem.nivel
        ).all()
    
    def find_product_location(self, product_id: int) -> List[InventoryItem]:
        """
        Localiza un producto en todas las ubicaciones
        Optimizado para < 1 segundo (HU-22)
        
        Args:
            product_id: ID del producto a localizar
            
        Returns:
            Lista de ubicaciones donde se encuentra el producto
        """
        logger.info(f"Localizando producto {product_id} en bodega")
        
        items = self.query().filter(
            InventoryItem.product_id == product_id,
            InventoryItem.cantidad > 0
        ).order_by(
            InventoryItem.pasillo,
            InventoryItem.estanteria,
            InventoryItem.nivel
        ).all()
        
        logger.info(f"Producto {product_id} encontrado en {len(items)} ubicaciones")
        return items
    
    def search_by_product_name_or_code(
        self,
        search_query: str
    ) -> List[Tuple[InventoryItem, Product]]:
        """
        Busca inventario por nombre, código o referencia del producto
        Hace JOIN con la tabla products para permitir búsqueda por campos del producto
        
        Args:
            search_query: Texto a buscar en nombre, código o referencia
            
        Returns:
            Lista de tuplas (InventoryItem, Product) que coinciden con la búsqueda
        """
        logger.info(f"Buscando inventario por query: '{search_query}'")
        
        # Construir query con JOIN
        query = db.session.query(InventoryItem, Product).join(
            Product,
            InventoryItem.product_id == Product.id
        )
        
        # Filtrar por nombre, código o referencia (case-insensitive)
        search_pattern = f"%{search_query.lower()}%"
        query = query.filter(
            or_(
                func.lower(Product.nombre).like(search_pattern),
                func.lower(Product.codigo).like(search_pattern),
                func.lower(Product.referencia).like(search_pattern)
            )
        )
        
        # Solo productos activos y con stock
        query = query.filter(
            Product.status == 'active',
            Product.is_deleted == False,
            InventoryItem.cantidad > 0
        )
        
        # Ordenar por nombre de producto
        query = query.order_by(
            Product.nombre,
            InventoryItem.pasillo
        )
        
        results = query.all()
        logger.info(f"Búsqueda completada: {len(results)} resultados encontrados")
        
        return results
    
    def search_inventory(
        self,
        product_id: Optional[int] = None,
        status: Optional[str] = None,
        pasillo: Optional[str] = None,
        estanteria: Optional[str] = None,
        nivel: Optional[str] = None
    ) -> List[InventoryItem]:
        """
        Busca items de inventario con múltiples filtros
        
        Args:
            product_id: Filtro por producto
            status: Filtro por estado
            pasillo: Filtro por pasillo
            estanteria: Filtro por estantería
            nivel: Filtro por nivel
            
        Returns:
            Lista de items que coinciden
        """
        query = self.query()
        
        if product_id:
            query = query.filter(InventoryItem.product_id == product_id)
        
        if status:
            query = query.filter(InventoryItem.status == status)
        
        if pasillo:
            query = query.filter(InventoryItem.pasillo == pasillo)
        
        if estanteria:
            query = query.filter(InventoryItem.estanteria == estanteria)
        
        if nivel:
            query = query.filter(InventoryItem.nivel == nivel)
        
        return query.order_by(
            InventoryItem.product_id
        ).all()
    
    def get_by_location(
        self,
        pasillo: str,
        estanteria: Optional[str] = None,
        nivel: Optional[str] = None
    ) -> List[InventoryItem]:
        """
        Obtiene items por ubicación en bodega
        
        Args:
            pasillo: Pasillo
            estanteria: Estantería (opcional)
            nivel: Nivel (opcional)
            
        Returns:
            Lista de items en la ubicación
        """
        query = self.query().filter(
            InventoryItem.pasillo == pasillo
        )
        
        if estanteria:
            query = query.filter(InventoryItem.estanteria == estanteria)
        
        if nivel:
            query = query.filter(InventoryItem.nivel == nivel)
        
        return query.order_by(InventoryItem.product_id).all()
    
    def get_items_without_location(self) -> List[InventoryItem]:
        """
        Obtiene items sin ubicación asignada
        
        Returns:
            Lista de items sin ubicación
        """
        query = self.query().filter(
            or_(
                InventoryItem.pasillo.is_(None),
                InventoryItem.estanteria.is_(None),
                InventoryItem.nivel.is_(None)
            )
        )
        
        return query.order_by(InventoryItem.product_id).all()
    
    def get_total_stock_by_product(self, product_id: int) -> float:
        """
        Calcula el stock total de un producto en todas las ubicaciones
        
        Args:
            product_id: ID del producto
            
        Returns:
            Cantidad total
        """
        result = self.query().filter(
            InventoryItem.product_id == product_id
        ).with_entities(
            func.sum(InventoryItem.cantidad)
        ).scalar()
        
        return float(result) if result else 0.0
    
    def get_available_stock_by_product(self, product_id: int) -> float:
        """
        Calcula el stock disponible de un producto
        
        Args:
            product_id: ID del producto
            
        Returns:
            Cantidad disponible total
        """
        result = self.query().filter(
            InventoryItem.product_id == product_id,
            InventoryItem.status == InventoryStatus.AVAILABLE.value
        ).with_entities(
            func.sum(InventoryItem.cantidad)
        ).scalar()
        
        return float(result) if result else 0.0


class InventoryMovementRepository(BaseRepository[InventoryMovement]):
    """
    Repositorio de movimientos de inventario
    """
    
    def __init__(self):
        super().__init__(InventoryMovement)
    
    def get_by_product(
        self,
        product_id: int,
        limit: int = 100
    ) -> List[InventoryMovement]:
        """
        Obtiene movimientos de un producto
        
        Args:
            product_id: ID del producto
            limit: Límite de resultados
            
        Returns:
            Lista de movimientos
        """
        return self.query().filter(
            InventoryMovement.product_id == product_id
        ).order_by(
            InventoryMovement.fecha_movimiento.desc()
        ).limit(limit).all()
    
    def get_by_inventory_item(
        self,
        inventory_item_id: int,
        limit: int = 100
    ) -> List[InventoryMovement]:
        """
        Obtiene movimientos de un item de inventario específico
        
        Args:
            inventory_item_id: ID del item de inventario
            limit: Límite de resultados
            
        Returns:
            Lista de movimientos
        """
        return self.query().filter(
            InventoryMovement.inventory_item_id == inventory_item_id
        ).order_by(
            InventoryMovement.fecha_movimiento.desc()
        ).limit(limit).all()
    
    def search_movements(
        self,
        product_id: Optional[int] = None,
        inventory_item_id: Optional[int] = None,
        tipo: Optional[str] = None,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None
    ) -> List[InventoryMovement]:
        """
        Busca movimientos con filtros
        
        Args:
            product_id: Filtro por producto
            inventory_item_id: Filtro por item de inventario
            tipo: Filtro por tipo de movimiento
            fecha_desde: Fecha inicial
            fecha_hasta: Fecha final
            
        Returns:
            Lista de movimientos
        """
        query = self.query()
        
        if product_id:
            query = query.filter(InventoryMovement.product_id == product_id)
        
        if inventory_item_id:
            query = query.filter(InventoryMovement.inventory_item_id == inventory_item_id)
        
        if tipo:
            query = query.filter(InventoryMovement.tipo == tipo)
        
        if fecha_desde:
            query = query.filter(InventoryMovement.fecha_movimiento >= fecha_desde)
        
        if fecha_hasta:
            # Incluir todo el día de fecha_hasta
            fecha_hasta_end = datetime.combine(fecha_hasta, datetime.max.time())
            query = query.filter(InventoryMovement.fecha_movimiento <= fecha_hasta_end)
        
        return query.order_by(
            InventoryMovement.fecha_movimiento.desc()
        ).all()
    
    def get_recent_movements(
        self,
        limit: int = 50
    ) -> List[InventoryMovement]:
        """
        Obtiene movimientos recientes
        
        Args:
            limit: Número de movimientos
            
        Returns:
            Lista de movimientos recientes
        """
        return self.query().order_by(
            InventoryMovement.fecha_movimiento.desc()
        ).limit(limit).all()
