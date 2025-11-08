"""
Repositorio de inventario con búsqueda optimizada
"""
from typing import List, Optional, Tuple
from datetime import date, datetime
from sqlalchemy import or_, and_, func
from app.shared.base_repository import BaseRepository
from app.modules.inventory.models import InventoryItem, InventoryMovement
# Import the new Product model from products module instead of the old read-only one
from app.modules.products.models import Product
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

    def search_inventory(self, product_id: Optional[int] = None) -> List[InventoryItem]:
        """
        Búsqueda simple de inventario por product_id (ayuda en pruebas y casos sencillos).

        Args:
            product_id: ID del producto a buscar (opcional)

        Returns:
            Lista de InventoryItem que cumplen el filtro
        """
        q = self.query()
        if product_id is not None:
            q = q.filter(InventoryItem.product_id == product_id)

        return q.order_by(InventoryItem.pasillo).all()

    def get_by_location(self, pasillo: str) -> List[InventoryItem]:
        """
        Obtiene items por pasillo/ubicación principal
        """
        return self.query().filter(InventoryItem.pasillo == pasillo).all()

    def get_items_without_location(self) -> List[InventoryItem]:
        """
        Obtiene items que no tienen pasillo/estanteria/nivel definidos
        """
        return self.query().filter(
            (InventoryItem.pasillo == None) | (InventoryItem.estanteria == None) | (InventoryItem.nivel == None)
        ).all()
    
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

        search_pattern = f"%{search_query}%"

        try:
            from sqlalchemy import inspect, text
            inspector = inspect(db.engine)
            product_columns = [c['name'] for c in inspector.get_columns(Product.__tablename__)]
            logger.info(f"Detected product table columns: {sorted(product_columns)}")
        except Exception:
            logger.exception('Failed to inspect DB columns for products; aborting search')
            return []

        # Candidate name/code/reference column names to try (English then Spanish)
        candidates = []
        for col in ('name', 'nombre', 'code', 'codigo', 'reference', 'referencia'):
            if col in product_columns:
                candidates.append(col)

        if not candidates:
            logger.warning('No searchable product columns found in products table')
            return []

        # Use LOWER(... ) LIKE LOWER(:search) for cross-DB compatibility
        where_clauses = [f"LOWER({Product.__tablename__}.{col}) LIKE LOWER(:search)" for col in candidates]
        where_sql = ' OR '.join(where_clauses)

        # Build optional status/is_deleted clauses only if the DB exposes them
        extra_clauses = []
        params = {'search': search_pattern}
        if 'status' in product_columns:
            extra_clauses.append('status = :status')
            params['status'] = 'active'
        if 'is_deleted' in product_columns:
            extra_clauses.append('is_deleted = false')

        extra_sql = ''
        if extra_clauses:
            extra_sql = ' AND ' + ' AND '.join(extra_clauses)

        # Select product id and only the actual DB columns (to avoid ORM mapping issues)
        selected_cols = ', '.join(sorted(product_columns))
        sql = f"SELECT id, {selected_cols} FROM {Product.__tablename__} WHERE ({where_sql}){extra_sql}"

        try:
            rows = db.session.execute(text(sql), params).mappings().all()
        except Exception:
            logger.exception('Failed to execute raw product search SQL')
            return []

        if not rows:
            logger.info('No products matched search')
            return []

        product_ids = [r['id'] for r in rows]

        # Fetch inventory items for matched products (ORM) and attach product data
        items = db.session.query(InventoryItem).filter(
            InventoryItem.product_id.in_(product_ids),
            InventoryItem.cantidad > 0
        ).order_by(InventoryItem.pasillo).all()

        # Return product info as a simple object with attribute access to satisfy callers/tests
        from types import SimpleNamespace

        product_map = {r['id']: SimpleNamespace(**dict(r)) for r in rows}
        results = [(item, product_map.get(item.product_id)) for item in items]

        logger.info(f"Búsqueda completada: {len(results)} resultados encontrados")

        return results

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

    def get_total_stock_by_product(self, product_id: int) -> float:
        """
        Calcula el stock total (independiente del estado) de un producto

        Args:
            product_id: ID del producto

        Returns:
            Cantidad total en inventario
        """
        result = self.query().filter(
            InventoryItem.product_id == product_id
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
