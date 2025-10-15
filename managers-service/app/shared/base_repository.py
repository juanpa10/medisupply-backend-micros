from typing import TypeVar, Generic, Type, List, Optional
from app.config.database import db
from app.shared.base_model import BaseModel
from sqlalchemy.exc import IntegrityError
from app.core.exceptions import NotFoundError, ConflictError

T = TypeVar('T', bound=BaseModel)


class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model

    def create(self, data: dict, user: str = None) -> T:
        try:
            # Filter data to only include valid model column keys to avoid passing
            # unexpected kwargs (e.g. 'operator') into SQLAlchemy model constructor.
            valid_keys = {c.name for c in self.model.__table__.columns}
            filtered = {k: v for k, v in data.items() if k in valid_keys}
            instance = self.model(**filtered)
            if user:
                instance.created_by = user
            db.session.add(instance)
            db.session.commit()
            db.session.refresh(instance)
            return instance
        except IntegrityError:
            db.session.rollback()
            raise ConflictError('El registro ya existe o viola restricciones de integridad')

    def get_by_id(self, id: int, include_deleted: bool = False) -> Optional[T]:
        query = db.session.query(self.model).filter(self.model.id == id)
        if not include_deleted:
            query = query.filter(self.model.is_deleted == False)
        return query.first()

    def get_by_id_or_fail(self, id: int, include_deleted: bool = False) -> T:
        instance = self.get_by_id(id, include_deleted)
        if not instance:
            raise NotFoundError(f'{self.model.__name__} not found')
        return instance

    def get_all(self, include_deleted: bool = False) -> List[T]:
        query = db.session.query(self.model)
        if not include_deleted:
            query = query.filter(self.model.is_deleted == False)
        return query.all()

    def filter_by(self, include_deleted: bool = False, **filters) -> List[T]:
        query = db.session.query(self.model).filter_by(**filters)
        if not include_deleted:
            query = query.filter(self.model.is_deleted == False)
        return query.all()

    def query(self):
        return db.session.query(self.model).filter(self.model.is_deleted == False)

    def count(self, include_deleted: bool = False) -> int:
        query = db.session.query(self.model)
        if not include_deleted:
            query = query.filter(self.model.is_deleted == False)
        return query.count()

    def update(self, id: int, data: dict, user: str = None) -> T:
        instance = self.get_by_id_or_fail(id)
        for k, v in data.items():
            if hasattr(instance, k):
                setattr(instance, k, v)
        if user:
            instance.updated_by = user
        db.session.commit()
        db.session.refresh(instance)
        return instance

    def delete(self, id: int, user: str = None, soft: bool = True) -> bool:
        instance = self.get_by_id_or_fail(id)
        if soft:
            instance.soft_delete(user)
            db.session.commit()
        else:
            db.session.delete(instance)
            db.session.commit()
        return True

    def exists(self, **filters) -> bool:
        query = db.session.query(self.model).filter_by(**filters).filter(self.model.is_deleted == False)
        return db.session.query(query.exists()).scalar()
