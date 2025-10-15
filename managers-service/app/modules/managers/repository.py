from app.shared.base_repository import BaseRepository
from app.modules.managers.models import AccountManager, Client, AssignmentHistory
from app.config.database import db
from app.core.exceptions import ConflictError, NotFoundError
from datetime import datetime


class ManagerRepository(BaseRepository[AccountManager]):
    def __init__(self):
        super().__init__(AccountManager)

    def exists_by_email_or_identification(self, email: str, identification: str, exclude_id: int = None) -> bool:
        query = db.session.query(self.model).filter(
            (AccountManager.email == email) | (AccountManager.identification == identification)
        )
        if exclude_id:
            query = query.filter(AccountManager.id != exclude_id)
        query = query.filter(AccountManager.is_deleted == False)
        return db.session.query(query.exists()).scalar()

    def assign_client(self, manager_id: int, client_id: int, operator: str = None, evidence: str = None):
        # get client
        client = db.session.query(Client).filter(Client.id == client_id).first()
        if not client:
            # Client absence should be reported as NotFound (404), not Conflict (409)
            raise NotFoundError('Client not found')
        prev_manager_id = client.manager_id
        if prev_manager_id == manager_id:
            # already assigned
            return client
        # create history entry for assignment
        now = datetime.utcnow()
        history = AssignmentHistory(manager_id=manager_id, client_id=client_id, assigned_at=now, operator=operator, evidence=evidence)
        db.session.add(history)
        # mark unassigned_at for previous assignment history if exists
        if prev_manager_id:
            prev_hist = db.session.query(AssignmentHistory).filter(AssignmentHistory.client_id == client_id, AssignmentHistory.unassigned_at == None).order_by(AssignmentHistory.assigned_at.desc()).first()
            if prev_hist:
                prev_hist.unassigned_at = now
        # assign manager
        client.manager_id = manager_id
        db.session.commit()
        db.session.refresh(client)
        return client

    def reassign_client(self, new_manager_id: int, client_id: int, operator: str = None, evidence: str = None):
        # simply call assign_client (history logic handles unassign)
        return self.assign_client(new_manager_id, client_id, operator=operator, evidence=evidence)

    def get_assignments(self, client_id: int = None):
        query = db.session.query(AssignmentHistory)
        if client_id:
            query = query.filter(AssignmentHistory.client_id == client_id)
        return query.order_by(AssignmentHistory.assigned_at.desc()).all()

    def get_by_email(self, email: str):
        return db.session.query(self.model).filter(self.model.email == email, self.model.is_deleted == False).first()
