import random
from datetime import date, timedelta
from sqlalchemy import text
from app.db import engine, Base
from app.domain.models import Sale


def init_db(database_url=None):
    # create tables
    Base.metadata.create_all(bind=engine)

    # create a materialized view (optional) - Postgres only
    try:
        with engine.connect() as conn:
            conn.execute(text('''
            CREATE MATERIALIZED VIEW IF NOT EXISTS mv_daily_totals AS
            SELECT date::date as d, salesperson, product, zone, sum(amount) as total
            FROM sales
            GROUP BY date::date, salesperson, product, zone;
            '''))
            conn.commit()
    except Exception:
        # likely sqlite - ignore
        pass

    # seed example data if empty
    from app.db import SessionLocal
    sess = SessionLocal()
    cnt = sess.query(Sale).count()
    if cnt == 0:
        salespeople = ['Alice', 'Bob', 'Carlos', 'Diana']
        products = ['Widget', 'Gadget', 'Doohickey']
        zones = ['North', 'South', 'East', 'West']
        rows = []
        today = date.today()
        for d in range(120):
            day = today - timedelta(days=d)
            # random number of sales per day
            for _ in range(random.randint(5, 15)):
                rows.append({
                    'date': day,
                    'salesperson': random.choice(salespeople),
                    'product': random.choice(products),
                    'zone': random.choice(zones),
                    'amount': round(random.uniform(10, 1000),2),
                })
        # bulk insert
        from app.repositories.repo import Repo
        Repo().insert_sales_bulk(rows)
