from typing import List, Optional, Tuple
from sqlalchemy import select
from app.domain.delivery import Delivery

class DeliveriesRepository:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def create(self, order_id:int, client_id:int, delivery_date, status:str) -> Delivery:
        with self.session_factory() as s:
            d = Delivery(order_id=order_id, client_id=client_id, delivery_date=delivery_date, status=status)
            s.add(d); s.commit(); s.refresh(d); return d

    def list_all(self, limit:int=50, cursor:Optional[int]=None) -> Tuple[List[Delivery], Optional[int]]:
        with self.session_factory() as s:
            stmt = select(Delivery).order_by(Delivery.id.asc()).limit(limit+1)
            if cursor: stmt = stmt.where(Delivery.id > cursor)
            rows = list(s.scalars(stmt))
            next_cursor = None
            if len(rows) > limit:
                next_cursor = rows[-1].id
                rows = rows[:limit]
            return rows, next_cursor

    def list_by_client(self, client_id:int, limit:int=50, cursor:Optional[int]=None) -> Tuple[List[Delivery], Optional[int]]:
        with self.session_factory() as s:
            stmt = select(Delivery).where(Delivery.client_id==client_id).order_by(Delivery.id.asc()).limit(limit+1)
            if cursor: stmt = stmt.where(Delivery.id > cursor)
            rows = list(s.scalars(stmt))
            next_cursor = None
            if len(rows) > limit:
                next_cursor = rows[-1].id
                rows = rows[:limit]
            return rows, next_cursor
