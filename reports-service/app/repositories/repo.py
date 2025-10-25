from sqlalchemy import select, func, cast, Date
from app.db import SessionLocal
from app.domain.models import Sale

class Repo:
    def __init__(self, session=None):
        self.session = session or SessionLocal()

    def insert_sales_bulk(self, rows):
        self.session.bulk_save_objects([Sale(**r) for r in rows])
        self.session.commit()

    def total_sales(self, start, end):
        stmt = select(func.coalesce(func.sum(Sale.amount),0)).where(Sale.date >= start).where(Sale.date <= end)
        return float(self.session.execute(stmt).scalar() or 0)

    def group_top_n(self, start, end, group_by, n=5):
        col = getattr(Sale, group_by)
        stmt = select(col, func.sum(Sale.amount).label('total')).where(Sale.date >= start).where(Sale.date <= end).group_by(col).order_by(func.sum(Sale.amount).desc()).limit(n)
        return [{group_by: r[0], 'total': float(r[1])} for r in self.session.execute(stmt).all()]

    def daily_series(self, start, end):
        # avoid casting which can trigger DB-specific processors; use the column directly
        stmt = select(Sale.date.label('d'), func.sum(Sale.amount).label('total')).where(Sale.date >= start).where(Sale.date <= end).group_by(Sale.date).order_by(Sale.date)
        rows = self.session.execute(stmt).all()
        result = []
        for r in rows:
            d = r[0]
            if hasattr(d, 'isoformat'):
                ds = d.isoformat()
            else:
                ds = str(d)
            result.append({'date': ds, 'total': float(r[1])})
        return result

    def grouped_daily_series(self, start, end, group_by):
        col = getattr(Sale, group_by)
        stmt = select(Sale.date.label('d'), col, func.sum(Sale.amount).label('total')).where(Sale.date >= start).where(Sale.date <= end).group_by(Sale.date, col).order_by(Sale.date)
        rows = self.session.execute(stmt).all()
        result = []
        for r in rows:
            d = r[0]
            if hasattr(d, 'isoformat'):
                ds = d.isoformat()
            else:
                ds = str(d)
            result.append({'date': ds, group_by: r[1], 'total': float(r[2])})
        return result
