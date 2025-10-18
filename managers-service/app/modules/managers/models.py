from app.config.database import db
from app.shared.base_model import BaseModel

# Cliente tiene referencia al gerente activo (si aplica)
class Client(BaseModel):
    __tablename__ = 'clients'

    name = db.Column(db.String(255), nullable=False)
    identifier = db.Column(db.String(100), nullable=False, unique=True, index=True)
    manager_id = db.Column(db.Integer, db.ForeignKey('account_managers.id'), nullable=True)

    manager = db.relationship('AccountManager', back_populates='clients')

    def to_dict(self):
        data = super().to_dict()
        data.update({'name': self.name, 'identifier': self.identifier, 'manager_id': self.manager_id})
        return data


class AccountManager(BaseModel):
    __tablename__ = 'account_managers'

    full_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    phone = db.Column(db.String(50), nullable=False)
    identification = db.Column(db.String(100), nullable=False, unique=True, index=True)
    status = db.Column(db.String(20), nullable=False, default='active')

    clients = db.relationship('Client', back_populates='manager')

    def to_dict(self):
        data = super().to_dict()
        data.update({'full_name': self.full_name, 'email': self.email, 'phone': self.phone, 'identification': self.identification, 'status': self.status})
        return data


class AssignmentHistory(BaseModel):
    __tablename__ = 'assignment_history'

    manager_id = db.Column(db.Integer, db.ForeignKey('account_managers.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    assigned_at = db.Column(db.DateTime, nullable=False)
    unassigned_at = db.Column(db.DateTime, nullable=True)
    operator = db.Column(db.String(100), nullable=True)
    evidence = db.Column(db.Text, nullable=True)

    def to_dict(self):
        data = super().to_dict()
        data.update({'manager_id': self.manager_id, 'client_id': self.client_id, 'assigned_at': self.assigned_at.isoformat() if self.assigned_at else None, 'unassigned_at': self.unassigned_at.isoformat() if self.unassigned_at else None, 'operator': self.operator})
        return data
