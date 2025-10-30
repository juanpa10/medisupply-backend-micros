#!/usr/bin/env python3
"""
Idempotent helper to ensure deterministic sales exist for 2025-01-01..2025-01-07.
Run inside the `reports-service` container:

  docker compose exec reports-service python reports-service/scripts/ensure_jan2025.py

The script will check for the presence of specific rows (date, salesperson,
product, zone, amount) and insert any that are missing. Safe to run multiple
times.
"""
from datetime import date, timedelta
from app.db import SessionLocal
from app.domain.models import Sale
# Ensure DB tables exist in case init_db didn't run or failed in another
# process. This is idempotent and cheap for the small schema.
from app.db import engine, Base


def ensure_tables():
    try:
        Base.metadata.create_all(bind=engine)
    except Exception:
        # if creation fails, we still attempt the idempotent checks below
        pass


def make_jan_rows():
    jan_start = date(2025, 1, 1)
    rows = []
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
    qty_alice = 125
    qty_bob = 134
    qty_big = 1000

    for offset in range(0, 7):
        d = jan_start + timedelta(days=offset)
        amount_a = round(product_price['Paracetamol 500mg'] * qty_alice, 2)
        amount_b = round(product_price['Ibuprofeno 400mg'] * qty_bob, 2)
        rows.append({'date': d, 'salesperson': 'Alice', 'product': 'Paracetamol 500mg', 'zone': 'North', 'amount': amount_a})
        rows.append({'date': d, 'salesperson': 'Bob',   'product': 'Ibuprofeno 400mg',   'zone': 'South', 'amount': amount_b})
        if offset == 2:
            amount_big = round(product_price['Paracetamol 500mg'] * qty_big, 2)
            rows.append({'date': d, 'salesperson': 'Carlos', 'product': 'Paracetamol 500mg', 'zone': 'North', 'amount': amount_big})
    return rows


def ensure_rows():
    # Make sure the tables exist (safe to call multiple times)
    ensure_tables()
    sess = SessionLocal()
    rows = make_jan_rows()
    inserted = 0
    for r in rows:
        # check existence of an identical row
        q = sess.query(Sale).filter(Sale.date == r['date'])
        q = q.filter(Sale.salesperson == r['salesperson'])
        q = q.filter(Sale.product == r['product'])
        q = q.filter(Sale.zone == r['zone'])
        q = q.filter(Sale.amount == r['amount'])
        exists = sess.query(q.exists()).scalar()
        if not exists:
            s = Sale(**r)
            sess.add(s)
            inserted += 1

    if inserted > 0:
        sess.commit()
    sess.close()
    return inserted


if __name__ == '__main__':
    print('Checking deterministic Jan 2025 sales...')
    n = ensure_rows()
    if n == 0:
        print('All deterministic rows already present.')
    else:
        print(f'Inserted {n} missing deterministic rows.')