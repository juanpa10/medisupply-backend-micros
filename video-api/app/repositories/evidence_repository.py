from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional, List
from app.domain.evidence import Evidence

class EvidenceRepository:
    def __init__(self, db_session_factory):
        self.db_session_factory = db_session_factory

    def create(self, **kwargs) -> Evidence:
        with self.db_session_factory() as s:  # type: Session
            e = Evidence(**kwargs)
            s.add(e)
            s.commit()
            s.refresh(e)
            return e

    def get(self, evid_id: int) -> Optional[Evidence]:
        with self.db_session_factory() as s:
            return s.get(Evidence, evid_id)

    def list_recent(self, limit: int = 20) -> List[Evidence]:
        with self.db_session_factory() as s:
            stmt = select(Evidence).order_by(Evidence.created_at.desc()).limit(limit)
            return list(s.scalars(stmt))
