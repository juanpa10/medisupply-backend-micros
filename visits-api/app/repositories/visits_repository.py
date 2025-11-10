from typing import List, Optional
from sqlalchemy import select, and_
from datetime import datetime
from app.domain.visit import Visit, VisitStop

class VisitsRepository:
    def __init__(self, session_factory): self.session_factory = session_factory
    def create_visit(self, visit_id:int, commercial_id:int, date:datetime, client_ids:List[int]) -> Visit:
        with self.session_factory() as s:
            v = Visit(id=visit_id, commercial_id=commercial_id, date=date)
            v.stops = [VisitStop(client_id=c, position=i+1) for i,c in enumerate(client_ids)]
            s.add(v); s.commit(); s.refresh(v); _=len(v.stops); return v
    def list_all(self, limit:int=50, cursor:Optional[int]=None):
        with self.session_factory() as s:
            q = select(Visit).order_by(Visit.id.asc()).limit(limit+1)
            if cursor: q = q.where(Visit.id > cursor)
            rows = list(s.scalars(q)); nxt=None
            if len(rows)>limit: nxt=rows[-1].id; rows=rows[:limit]
            for v in rows: _=len(v.stops)
            return rows, nxt
    def list_by_dates(self, d1:datetime, d2:datetime, limit:int=50, cursor:Optional[int]=None):
        with self.session_factory() as s:
            q = select(Visit).where(and_(Visit.date>=d1, Visit.date<=d2)).order_by(Visit.id.asc()).limit(limit+1)
            if cursor: q = q.where(Visit.id > cursor)
            rows = list(s.scalars(q)); nxt=None
            if len(rows)>limit: nxt=rows[-1].id; rows=rows[:limit]
            for v in rows: _=len(v.stops)
            return rows, nxt
    def list_by_commercial(self, commercial_id:int, limit:int=50, cursor:Optional[int]=None):
        with self.session_factory() as s:
            q = select(Visit).where(Visit.commercial_id==commercial_id).order_by(Visit.id.asc()).limit(limit+1)
            if cursor: q = q.where(Visit.id > cursor)
            rows = list(s.scalars(q)); nxt=None
            if len(rows)>limit: nxt=rows[-1].id; rows=rows[:limit]
            for v in rows: _=len(v.stops)
            return rows, nxt
