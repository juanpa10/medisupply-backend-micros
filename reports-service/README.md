# reports-service

Microservice to generate sales reports by salesperson, product or zone.

Run locally (dev):

1. Create virtualenv and install requirements

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Start Postgres and the app via docker-compose (see folder)

```powershell
docker compose up --build
```

Deterministic seed for 2025-01-01..2025-01-07
-------------------------------------------

For demo and frontend examples we include a small deterministic dataset covering
2025-01-01 through 2025-01-07 so requests that query that window return
meaningful results. The seed inserts three kinds of deterministic sales per day:

- Alice — Paracetamol 500mg (quantity 125) — amount = unit_price (1.20) * 125 = 150.00
- Bob   — Ibuprofeno 400mg (quantity 134) — amount = unit_price (1.50) * 134 = 201.00
- Carlos — on 2025-01-03 only — Paracetamol 500mg (quantity 1000) — amount = 1.20 * 1000 = 1200.00

These rows are inserted idempotently by the seeder. You can ensure they exist
by running the helper script inside the running container (no rebuild):

```powershell
docker compose exec reports-service python scripts/ensure_jan2025.py
```

Verify with this quick SQL check:

```powershell
docker compose exec reports-service python -c 'from app.db import SessionLocal; from sqlalchemy import text; s=SessionLocal(); total=int(s.execute(text("SELECT count(*) FROM sales")).scalar() or 0); rng=float(s.execute(text("SELECT coalesce(sum(amount),0) FROM sales WHERE date >= ''2025-01-01'' AND date <= ''2025-01-07''")).scalar() or 0); print("total_rows=", total); print("sum_2025-01-01..07=", rng)'
```

If the API still returns empty for that range, restart the service to invalidate
its cache:

```powershell
docker compose restart reports-service
```

