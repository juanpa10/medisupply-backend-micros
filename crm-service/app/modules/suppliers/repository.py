"""
Repositorio de Suppliers
"""
from app.shared.base_repository import BaseRepository
from app.modules.suppliers.models import Supplier
from app.core.exceptions import ConflictError


class SupplierRepository(BaseRepository[Supplier]):
    """Repositorio para operaciones de base de datos de Suppliers"""
    
    def __init__(self):
        super().__init__(Supplier)
    
    def get_by_nit(self, nit: str, include_deleted: bool = False):
        """
        Obtiene un proveedor por NIT
        
        Args:
            nit: NIT del proveedor
            include_deleted: Si incluir eliminados
            
        Returns:
            Supplier o None
        """
        query = self.query().filter(Supplier.nit == nit)
        
        if include_deleted:
            query = self.model.query.filter(Supplier.nit == nit)
        
        return query.first()
    
    def check_nit_exists(self, nit: str, exclude_id: int = None) -> bool:
        """
        Verifica si existe un NIT
        
        Args:
            nit: NIT a verificar
            exclude_id: ID a excluir de la búsqueda (para updates)
            
        Returns:
            True si existe
        """
        query = self.query().filter(Supplier.nit == nit)
        
        if exclude_id:
            query = query.filter(Supplier.id != exclude_id)
        
        return query.count() > 0
    
    def search_suppliers(self, search_term: str = None, pais: str = None, 
                        status: str = None):
        """
        Busca proveedores con filtros
        
        Args:
            search_term: Término de búsqueda (razón social o NIT)
            pais: Filtro por país
            status: Filtro por estado
            
        Returns:
            Query de SQLAlchemy
        """
        query = self.query()
        
        if search_term:
            search_filter = f'%{search_term}%'
            query = query.filter(
                (Supplier.razon_social.ilike(search_filter)) |
                (Supplier.nit.ilike(search_filter))
            )
        
        if pais:
            query = query.filter(Supplier.pais == pais)
        
        if status:
            query = query.filter(Supplier.status == status)
        
        return query
    
    def get_suppliers_by_country(self, pais: str):
        """
        Obtiene proveedores por país
        
        Args:
            pais: País a filtrar
            
        Returns:
            Lista de suppliers
        """
        return self.query().filter(Supplier.pais == pais).all()
    
    def get_active_suppliers(self):
        """
        Obtiene solo proveedores activos
        
        Returns:
            Lista de suppliers activos
        """
        return self.query().filter(Supplier.status == 'active').all()
