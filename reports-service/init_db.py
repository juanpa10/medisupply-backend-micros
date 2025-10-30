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
        # Use the same example medical products as the inventory seeder so
        # reports reference realistic product names used across the project.
        products = [
            'Paracetamol 500mg', 'Ibuprofeno 400mg', 'Amoxicilina 500mg',
            'Omeprazol 20mg', 'Losartán 50mg', 'Metformina 850mg',
            'Simvastatina 20mg', 'Aspirina 100mg', 'Cetirizina 10mg'
        ]
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
        # Add deterministic sample data for 2025-01-01 .. 2025-01-07 so reports
        # queries that target that window (e.g. the example in README) return
        # meaningful results.
        jan_start = date(2025, 1, 1)
        jan_rows = []
        # create a few predictable sales per day with known products
        # Use unit prices from the inventory seeder to compute deterministic
        # amounts as unit_price * quantity so the example data looks realistic.
        product_price = {
            'Paracetamol 500mg': 1.20,
            'Ibuprofeno 400mg': 1.50,
            'Amoxicilina 500mg': 2.00,
            'Omeprazol 20mg': 1.80,
            'Losartán 50mg': 2.20,
            'Metformina 850mg': 1.00,
            'Simvastatina 20mg': 1.90,
            'Aspirina 100mg': 0.80,
            'Cetirizina 10mg': 1.10,
        }
        # chosen quantities to produce round/example amounts similar to old values
        qty_alice = 125    # Paracetamol -> 1.20 * 125 = 150.00
        qty_bob = 134      # Ibuprofeno -> 1.50 * 134 = 201.00 (close to previous 200)
        qty_big = 1000     # large sale on day 3 -> 1.20 * 1000 = 1200.00

        for offset in range(0, 7):
            d = jan_start + timedelta(days=offset)
            amount_a = round(product_price['Paracetamol 500mg'] * qty_alice, 2)
            amount_b = round(product_price['Ibuprofeno 400mg'] * qty_bob, 2)
            jan_rows.append({'date': d, 'salesperson': 'Alice', 'product': 'Paracetamol 500mg', 'zone': 'North', 'amount': amount_a})
            jan_rows.append({'date': d, 'salesperson': 'Bob',   'product': 'Ibuprofeno 400mg',   'zone': 'South', 'amount': amount_b})
            # a larger sale on 2025-01-03 to create a top item
            if offset == 2:
                amount_big = round(product_price['Paracetamol 500mg'] * qty_big, 2)
                jan_rows.append({'date': d, 'salesperson': 'Carlos', 'product': 'Paracetamol 500mg', 'zone': 'North', 'amount': amount_big})

        rows.extend(jan_rows)

        # bulk insert random + jan_rows if DB empty
        from app.repositories.repo import Repo
        Repo().insert_sales_bulk(rows)

        # Ensure deterministic Jan 1-7 2025 data exists even if the DB
        # already had other rows (idempotent check). If there are no sales
        # in that window, insert jan_rows explicitly.
        try:
            jan_start = date(2025, 1, 1)
            jan_end = date(2025, 1, 7)
            jan_count = sess.query(Sale).filter(Sale.date >= jan_start).filter(Sale.date <= jan_end).count()
            if jan_count == 0:
                Repo().insert_sales_bulk(jan_rows)
        except Exception:
            # if anything goes wrong here, we don't want to fail the init
            pass


    if __name__ == '__main__':
        # When invoked as a script (e.g. in the k8s init Job) run the init
        # routine so tables are created and seeded. Keep messages minimal
        # so logs are concise in CI.
        print('Running reports-service init_db...')
        init_db()
