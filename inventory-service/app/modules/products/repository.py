"""
Repositorio para gestión de productos

Maneja el acceso a datos para productos, categorías, unidades de medida,
proveedores y archivos de productos.
"""
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy import and_, or_, func, desc, asc
from sqlalchemy.orm import joinedload
from app.config.database import db
from app.shared.base_repository import BaseRepository
from app.modules.products.models import Product, ProductFile, Categoria, UnidadMedida, Proveedor
from app.core.exceptions import ResourceNotFoundError


class ProductRepository(BaseRepository):
    """Repositorio para productos"""
    
    def __init__(self):
        super().__init__(Product)
    
    def create_product(self, product_data: Dict[str, Any]) -> Product:
        """
        Crea un nuevo producto
        """
        product = Product(**product_data)
        db.session.add(product)
        db.session.commit()
        db.session.refresh(product)
        return product
    
    def get_product_by_id(self, product_id: int, include_relations: bool = True) -> Product:
        """
        Obtiene un producto por ID con relaciones opcionales
        """
        query = db.session.query(Product).filter(Product.id == product_id, Product.is_deleted == False)
        
        if include_relations:
            query = query.options(
                joinedload(Product.categoria),
                joinedload(Product.unidad_medida),
                joinedload(Product.proveedor),
                joinedload(Product.files)
            )
        
        product = query.first()
        if not product:
            raise ResourceNotFoundError(f"Producto con ID {product_id} no encontrado")
        
        return product
    
    def get_product_by_codigo(self, codigo: str) -> Optional[Product]:
        """
        Obtiene un producto por código
        """
        return db.session.query(Product).filter(
            Product.codigo == codigo,
            Product.is_deleted == False
        ).first()
    
    def update_product(self, product_id: int, update_data: Dict[str, Any]) -> Product:
        """
        Actualiza un producto
        """
        product = self.get_product_by_id(product_id, include_relations=False)
        
        for key, value in update_data.items():
            setattr(product, key, value)
        
        db.session.commit()
        db.session.refresh(product)
        return product
    
    def search_products(
        self,
        search_term: Optional[str] = None,
        categoria_id: Optional[int] = None,
        proveedor_id: Optional[int] = None,
        status: Optional[str] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Tuple[List[Product], int]:
        """
        Busca productos con filtros y paginación
        
        Returns:
            Tuple[List[Product], int]: Lista de productos y total de resultados
        """
        query = db.session.query(Product).filter(Product.is_deleted == False)
        
        # Aplicar filtros
        if search_term:
            search_filter = or_(
                Product.nombre.ilike(f'%{search_term}%'),
                Product.codigo.ilike(f'%{search_term}%'),
                Product.referencia.ilike(f'%{search_term}%'),
                Product.descripcion.ilike(f'%{search_term}%')
            )
            query = query.filter(search_filter)
        
        if categoria_id:
            query = query.filter(Product.categoria_id == categoria_id)
        
        if proveedor_id:
            query = query.filter(Product.proveedor_id == proveedor_id)
        
        if status and status != 'all':
            query = query.filter(Product.status == status)
        
        # Contar total antes de paginación
        total = query.count()
        
        # Aplicar paginación y ordenamiento
        products = query.order_by(Product.nombre).offset((page - 1) * per_page).limit(per_page).all()
        
        return products, total
    
    def get_products_by_categoria(self, categoria_id: int) -> List[Product]:
        """
        Obtiene todos los productos de una categoría
        """
        return db.session.query(Product).filter(
            Product.categoria_id == categoria_id,
            Product.is_deleted == False
        ).all()
    
    def get_products_by_proveedor(self, proveedor_id: int) -> List[Product]:
        """
        Obtiene todos los productos de un proveedor
        """
        return db.session.query(Product).filter(
            Product.proveedor_id == proveedor_id,
            Product.is_deleted == False
        ).all()
    
    def get_products_without_required_documents(self) -> List[Product]:
        """
        Obtiene productos que no tienen todos los documentos requeridos
        """
        products = db.session.query(Product).options(joinedload(Product.files)).filter(
            Product.is_deleted == False,
            Product.status == 'active'
        ).all()
        
        incomplete_products = []
        for product in products:
            if not product.has_required_documents():
                incomplete_products.append(product)
        
        return incomplete_products


class ProductFileRepository(BaseRepository):
    """Repositorio para archivos de productos"""
    
    def __init__(self):
        super().__init__(ProductFile)
    
    def create_file(self, file_data: Dict[str, Any]) -> ProductFile:
        """
        Crea un nuevo archivo de producto
        """
        product_file = ProductFile(**file_data)
        db.session.add(product_file)
        db.session.commit()
        db.session.refresh(product_file)
        return product_file
    
    def get_files_by_product(self, product_id: int, file_category: Optional[str] = None) -> List[ProductFile]:
        """
        Obtiene archivos de un producto por categoría opcional
        """
        query = db.session.query(ProductFile).filter(
            ProductFile.product_id == product_id,
            ProductFile.status == 'active'
        )
        
        if file_category:
            query = query.filter(ProductFile.file_category == file_category)
        
        return query.order_by(ProductFile.created_at.desc()).all()
    
    def get_file_by_id(self, file_id: int) -> ProductFile:
        """
        Obtiene un archivo por ID
        """
        file = db.session.query(ProductFile).filter(
            ProductFile.id == file_id,
            ProductFile.status == 'active'
        ).first()
        
        if not file:
            raise ResourceNotFoundError(f"Archivo con ID {file_id} no encontrado")
        
        return file
    
    def delete_file(self, file_id: int) -> bool:
        """
        Elimina un archivo (soft delete)
        """
        file = self.get_file_by_id(file_id)
        file.status = 'deleted'
        db.session.commit()
        return True
    
    def get_file_by_stored_filename(self, stored_filename: str) -> Optional[ProductFile]:
        """
        Obtiene un archivo por nombre almacenado
        """
        return db.session.query(ProductFile).filter(
            ProductFile.stored_filename == stored_filename,
            ProductFile.status == 'active'
        ).first()


class CategoriaRepository(BaseRepository):
    """Repositorio para categorías"""
    
    def __init__(self):
        super().__init__(Categoria)
    
    def create_categoria(self, categoria_data: Dict[str, Any]) -> Categoria:
        """
        Crea una nueva categoría
        """
        categoria = Categoria(**categoria_data)
        db.session.add(categoria)
        db.session.commit()
        db.session.refresh(categoria)
        return categoria
    
    def get_all_categorias(self, include_inactive: bool = False) -> List[Categoria]:
        """
        Obtiene todas las categorías
        """
        query = db.session.query(Categoria).filter(Categoria.is_deleted == False)
        
        if not include_inactive:
            query = query.filter(Categoria.status == 'active')
        
        return query.order_by(Categoria.nombre).all()
    
    def get_categoria_by_nombre(self, nombre: str) -> Optional[Categoria]:
        """
        Obtiene una categoría por nombre
        """
        return db.session.query(Categoria).filter(
            Categoria.nombre == nombre,
            Categoria.is_deleted == False
        ).first()


class UnidadMedidaRepository(BaseRepository):
    """Repositorio para unidades de medida"""
    
    def __init__(self):
        super().__init__(UnidadMedida)
    
    def create_unidad_medida(self, unidad_data: Dict[str, Any]) -> UnidadMedida:
        """
        Crea una nueva unidad de medida
        """
        unidad = UnidadMedida(**unidad_data)
        db.session.add(unidad)
        db.session.commit()
        db.session.refresh(unidad)
        return unidad
    
    def get_all_unidades_medida(self, include_inactive: bool = False) -> List[UnidadMedida]:
        """
        Obtiene todas las unidades de medida
        """
        query = db.session.query(UnidadMedida).filter(UnidadMedida.is_deleted == False)
        
        if not include_inactive:
            query = query.filter(UnidadMedida.status == 'active')
        
        return query.order_by(UnidadMedida.nombre).all()
    
    def get_unidad_by_nombre(self, nombre: str) -> Optional[UnidadMedida]:
        """
        Obtiene una unidad de medida por nombre
        """
        return db.session.query(UnidadMedida).filter(
            UnidadMedida.nombre == nombre,
            UnidadMedida.is_deleted == False
        ).first()
    
    def get_unidad_by_abreviatura(self, abreviatura: str) -> Optional[UnidadMedida]:
        """
        Obtiene una unidad de medida por abreviatura
        """
        return db.session.query(UnidadMedida).filter(
            UnidadMedida.abreviatura == abreviatura,
            UnidadMedida.is_deleted == False
        ).first()


class ProveedorRepository(BaseRepository):
    """Repositorio para proveedores"""
    
    def __init__(self):
        super().__init__(Proveedor)
    
    def create_proveedor(self, proveedor_data: Dict[str, Any]) -> Proveedor:
        """
        Crea un nuevo proveedor
        """
        proveedor = Proveedor(**proveedor_data)
        db.session.add(proveedor)
        db.session.commit()
        db.session.refresh(proveedor)
        return proveedor
    
    def get_all_proveedores(self, include_inactive: bool = False) -> List[Proveedor]:
        """
        Obtiene todos los proveedores
        """
        query = db.session.query(Proveedor).filter(Proveedor.is_deleted == False)
        
        if not include_inactive:
            query = query.filter(Proveedor.status == 'active')
        
        return query.order_by(Proveedor.nombre).all()
    
    def get_proveedor_by_nombre(self, nombre: str) -> Optional[Proveedor]:
        """
        Obtiene un proveedor por nombre
        """
        return db.session.query(Proveedor).filter(
            Proveedor.nombre == nombre,
            Proveedor.is_deleted == False
        ).first()
    
    def get_proveedor_by_nit(self, nit: str) -> Optional[Proveedor]:
        """
        Obtiene un proveedor por NIT
        """
        return db.session.query(Proveedor).filter(
            Proveedor.nit == nit,
            Proveedor.is_deleted == False
        ).first()
    
    def search_proveedores(self, search_term: str) -> List[Proveedor]:
        """
        Busca proveedores por nombre o NIT
        """
        return db.session.query(Proveedor).filter(
            and_(
                Proveedor.is_deleted == False,
                or_(
                    Proveedor.nombre.ilike(f'%{search_term}%'),
                    Proveedor.nit.ilike(f'%{search_term}%')
                )
            )
        ).order_by(Proveedor.nombre).all()