from datetime import datetime
from app.config.database import db


class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created_by = db.Column(db.String(100), nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)
    updated_by = db.Column(db.String(100), nullable=True)
    deleted_at = db.Column(db.DateTime, nullable=True)
    deleted_by = db.Column(db.String(100), nullable=True)
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)

    def soft_delete(self, user=None):
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        self.deleted_by = user

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None

    def to_dict(self):
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                result[column.name] = value.isoformat()
            else:
                result[column.name] = value
        return result

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.id}>'
