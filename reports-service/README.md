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
