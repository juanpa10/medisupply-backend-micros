from app.repositories.repo import Repo
from typing import List


class OrdersService:
    def __init__(self, repo: Repo | None = None):
        self.repo = repo or Repo()

    def seed(self):
        # seed a couple orders for local testing if none exist
        s = self.repo.session
        try:
            existing = s.execute("SELECT COUNT(1) FROM orders").scalar()
        except Exception:
            existing = None
        try:
            if existing == 0 or existing is None:
                # Use allowed status strings
                self.repo.create_order('cust-1', 'ORD-1001', 'En preparacion')
                self.repo.create_order('cust-1', 'ORD-1002', 'pendiente')
        except Exception:
            # rollback session to avoid leaving it in a bad state for tests
            try:
                s.rollback()
            except Exception:
                pass

    def list_orders(self, customer_id: str, state: str | None = None, start_date=None, end_date=None) -> List:
        return self.repo.list_orders_for_customer(customer_id, state, start_date, end_date)

    def get_order(self, order_number: str):
        return self.repo.get_order_by_number(order_number)

    def update_status(self, order_number: str, new_status: str, note: str | None = None):
        return self.repo.update_order_status(order_number, new_status, note)


svc = OrdersService()
