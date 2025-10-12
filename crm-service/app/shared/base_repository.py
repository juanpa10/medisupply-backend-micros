"""
Repositorio base con operaciones CRUD genéricas
"""
from typing import Type, TypeVar, Generic, List, Optional
from sqlalchemy.exc import IntegrityError
from app.config.database import db
from app.shared.base_model import BaseModel
from app.core.exceptions import NotFoundError, ConflictError

T = TypeVar('T', bound=BaseModel)


class BaseRepository(Generic[T]):
    """
    Repositorio base con operaciones CRUD
    
    Proporciona métodos genéricos para crear, leer, actualizar y eliminar
    """
    
    def __init__(self, model: Type[T]):
        """
        Inicializa el repositorio
        
        Args:
            model: Clase del modelo SQLAlchemy
        """
        self.model = model
    
    def create(self, data: dict, user: str = None) -> T:
        """
        Crea un nuevo registro
        
        Args:
            data: Datos del registro
            user: Usuario que crea el registro
            
        Returns:
            Instancia del modelo creado
            
        Raises:
            ConflictError: Si hay conflicto (ej. duplicado)
        """
        try:
            instance = self.model(**data)
            if user:
                instance.created_by = user
            
            db.session.add(instance)
            db.session.commit()
            db.session.refresh(instance)
            return instance
        except IntegrityError as e:
            db.session.rollback()
            raise ConflictError('El registro ya existe o viola restricciones de integridad')
    
    def get_by_id(self, id: int, include_deleted: bool = False) -> Optional[T]:
        """
        Obtiene un registro por ID
        
        Args:
            id: ID del registro
            include_deleted: Si incluir registros eliminados
            
        Returns:
            Instancia del modelo o None
        """
        query = db.session.query(self.model).filter(self.model.id == id)
        
        if not include_deleted:
            query = query.filter(self.model.is_deleted == False)
        
        return query.first()
    
    def get_by_id_or_fail(self, id: int, include_deleted: bool = False) -> T:
        """
        Obtiene un registro por ID o lanza excepción
        
        Args:
            id: ID del registro
            include_deleted: Si incluir registros eliminados
            
        Returns:
            Instancia del modelo
            
        Raises:
            NotFoundError: Si no se encuentra el registro
        """
        instance = self.get_by_id(id, include_deleted)
        if not instance:
            raise NotFoundError(f'{self.model.__name__} no encontrado')
        return instance
    
    def get_all(self, include_deleted: bool = False) -> List[T]:
        """
        Obtiene todos los registros
        
        Args:
            include_deleted: Si incluir registros eliminados
            
        Returns:
            Lista de instancias
        """
        query = db.session.query(self.model)
        
        if not include_deleted:
            query = query.filter(self.model.is_deleted == False)
        
        return query.all()
    
    def filter_by(self, include_deleted: bool = False, **filters) -> List[T]:
        """
        Filtra registros por criterios
        
        Args:
            include_deleted: Si incluir registros eliminados
            **filters: Criterios de filtro
            
        Returns:
            Lista de instancias
        """
        query = db.session.query(self.model).filter_by(**filters)
        
        if not include_deleted:
            query = query.filter(self.model.is_deleted == False)
        
        return query.all()
    
    def query(self):
        """
        Obtiene un query base
        
        Returns:
            Query de SQLAlchemy
        """
        return db.session.query(self.model).filter(self.model.is_deleted == False)
    
    def update(self, id: int, data: dict, user: str = None) -> T:
        """
        Actualiza un registro
        
        Args:
            id: ID del registro
            data: Datos a actualizar
            user: Usuario que actualiza
            
        Returns:
            Instancia actualizada
            
        Raises:
            NotFoundError: Si no se encuentra el registro
        """
        instance = self.get_by_id_or_fail(id)
        
        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        
        if user:
            instance.updated_by = user
        
        db.session.commit()
        db.session.refresh(instance)
        return instance
    
    def delete(self, id: int, user: str = None, soft: bool = True) -> bool:
        """
        Elimina un registro
        
        Args:
            id: ID del registro
            user: Usuario que elimina
            soft: Si es eliminación suave (soft delete)
            
        Returns:
            True si se eliminó
            
        Raises:
            NotFoundError: Si no se encuentra el registro
        """
        instance = self.get_by_id_or_fail(id)
        
        if soft:
            instance.soft_delete(user)
            db.session.commit()
        else:
            db.session.delete(instance)
            db.session.commit()
        
        return True
    
    def count(self, include_deleted: bool = False) -> int:
        """
        Cuenta los registros
        
        Args:
            include_deleted: Si incluir eliminados
            
        Returns:
            Número de registros
        """
        query = db.session.query(self.model)
        
        if not include_deleted:
            query = query.filter(self.model.is_deleted == False)
        
        return query.count()
    
    def exists(self, **filters) -> bool:
        """
        Verifica si existe un registro con los filtros dados
        
        Args:
            **filters: Criterios de filtro
            
        Returns:
            True si existe
        """
        return db.session.query(
            db.session.query(self.model)
            .filter_by(**filters)
            .filter(self.model.is_deleted == False)
            .exists()
        ).scalar()
