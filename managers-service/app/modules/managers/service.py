from app.modules.managers.repository import ManagerRepository
from app.core.exceptions import ConflictError, ValidationError
from datetime import datetime
from app.config.database import db

repo = ManagerRepository()


class ManagerService:
    def create_manager(self, data: dict, operator: str = None):
        # validate required fields
        required = ['full_name', 'email', 'phone', 'identification']
        for f in required:
            if not data.get(f):
                raise ValidationError(f'{f} is required')
        # basic validations
        if repo.exists_by_email_or_identification(data['email'], data['identification']):
            raise ConflictError('Manager with same email or identification exists')
        manager = repo.create(data, user=operator)
        return manager

    def assign_client(self, manager_id: int, client_id: int, operator: str = None, evidence: str = None):
        # ensure manager exists
        mgr = repo.get_by_id_or_fail(manager_id)
        # ensure client assignment respects single-active rule is enforced in repository
        client = repo.assign_client(manager_id, client_id, operator=operator, evidence=evidence)
        return client

    def reassign_client(self, new_manager_id: int, client_id: int, operator: str = None, evidence: str = None):
        # ensures new manager exists
        repo.get_by_id_or_fail(new_manager_id)
        return repo.reassign_client(new_manager_id, client_id, operator=operator, evidence=evidence)

    def get_assignments_history(self, client_id: int = None):
        return repo.get_assignments(client_id)

    def list_clients_with_manager(self):
        """Return a list of clients with an extra field 'manager' that contains
        the full_name of the linked AccountManager or the string 'Sin Gerente'
        when no manager is assigned.
        """
        from app.modules.managers.models import Client
        clients = db.session.query(Client).filter(Client.is_deleted == False).all()
        out = []
        for c in clients:
            mgr = getattr(c, 'manager', None)
            if mgr:
                mgr_obj = {'id': mgr.id, 'full_name': mgr.full_name}
            else:
                mgr_obj = None
            cd = c.to_dict()
            cd['manager'] = mgr_obj
            out.append(cd)
        return out

service = ManagerService()
