import datetime
from app.repositories.repo import Repo
from app.db import Base, engine
from app.services.reports_service import ReportsService

def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def seed(repo: Repo):
    today = datetime.date.today()
    rows = []
    for d in range(30):
        day = today - datetime.timedelta(days=d)
        for i in range(20):
            rows.append({'date': day, 'salesperson': f'S{i%5}', 'product': f'P{i%3}', 'zone': f'Z{i%4}', 'amount': 100})
    repo.insert_sales_bulk(rows)

def test_report_perf(benchmark):
    repo = Repo()
    seed(repo)
    svc = ReportsService(repo=repo)
    end = datetime.date.today()
    start = end - datetime.timedelta(days=6)
    def run():
        svc.generate_report('product', start, end)
    benchmark(run)
