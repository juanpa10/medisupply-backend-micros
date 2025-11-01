from datetime import datetime
from app.repositories.deliveries_repository import DeliveriesRepository
from app.domain.delivery import ALLOWED_STATUSES

class DeliveriesService:
    def __init__(self, repo: DeliveriesRepository):
        self.repo = repo
    def create(self, order_id:int, client_id:int, delivery_date:str, status:str):
        if status not in ALLOWED_STATUSES:
            raise ValueError("invalid_status")
        try:
            dt = datetime.fromisoformat(delivery_date.replace("Z",""))
        except Exception:
            raise ValueError("invalid_date")
        return self.repo.create(order_id, client_id, dt, status)
    def list_all(self, limit:int, cursor:int):
        return self.repo.list_all(limit=limit, cursor=cursor)
    def list_by_client(self, client_id:int, limit:int, cursor:int):
        return self.repo.list_by_client(client_id=client_id, limit=limit, cursor=cursor)
