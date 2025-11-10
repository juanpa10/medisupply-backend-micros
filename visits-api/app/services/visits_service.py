from typing import List, Optional
from datetime import datetime
from app.repositories.visits_repository import VisitsRepository

class VisitsService:
    def __init__(self, repo: VisitsRepository): self.repo = repo
    def create_visit(self, visit_id:int, commercial_id:int, date_str:str, client_ids:List[int]):
        if not client_ids or not isinstance(client_ids, list): raise ValueError("invalid_clients")
        try: date = datetime.fromisoformat(date_str.replace("Z",""))
        except Exception: raise ValueError("invalid_date")
        return self.repo.create_visit(visit_id, commercial_id, date, client_ids)
    def list_all(self, limit:int, cursor:Optional[int]): return self.repo.list_all(limit, cursor)
    def list_by_dates(self, df:str, dt:str, limit:int, cursor:Optional[int]):
        try:
            d1 = datetime.fromisoformat(df.replace("Z","")); d2 = datetime.fromisoformat(dt.replace("Z",""))
        except Exception: raise ValueError("invalid_date")
        return self.repo.list_by_dates(d1,d2,limit,cursor)
    def list_by_commercial(self, commercial_id:int, limit:int, cursor:Optional[int]):
        return self.repo.list_by_commercial(commercial_id, limit, cursor)
