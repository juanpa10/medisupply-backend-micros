import datetime
from app.services.reports_service import ReportsService
from app.repositories.repo import Repo
from app.db import Base, engine


def setup_function():
    # recreate tables on each test run
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def seed_simple(repo: Repo):
    today = datetime.date.today()
    rows = [
        {'date': today - datetime.timedelta(days=1), 'salesperson': 'Alice', 'product': 'Widget', 'zone': 'North', 'amount': 100},
        {'date': today - datetime.timedelta(days=1), 'salesperson': 'Bob', 'product': 'Gadget', 'zone': 'South', 'amount': 200},
        {'date': today - datetime.timedelta(days=2), 'salesperson': 'Alice', 'product': 'Widget', 'zone': 'North', 'amount': 50},
    ]
    repo.insert_sales_bulk(rows)


def test_generate_report_basic():
    repo = Repo()
    seed_simple(repo)
    svc = ReportsService(repo=repo)
    end = datetime.date.today() - datetime.timedelta(days=1)
    start = end - datetime.timedelta(days=6)
    r = svc.generate_report('salesperson', start, end)
    assert 'total' in r
    assert isinstance(r['top5'], list)
    assert isinstance(r['daily'], list)
