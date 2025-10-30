from app import create_app
import json


def test_reports_endpoint_validation():
    app = create_app()
    client = app.test_client()
    # invalid criterion
    resp = client.post('/api/v1/reports', json={'criterion': 'invalid', 'start': '2025-01-01', 'end': '2025-01-07'})
    assert resp.status_code == 400


def test_reports_endpoint_success(monkeypatch):
    app = create_app()
    client = app.test_client()

    # stub ReportsService.generate_report to avoid DB dependency
    sample = {'criterion': 'product', 'start': '2025-01-01', 'end': '2025-01-07', 'total': 123.0, 'pct_change': 10.0, 'top5': [], 'daily': []}
    import app.controllers.api as api_mod
    monkeypatch.setattr(api_mod.ReportsService, 'generate_report', lambda self, c, s, e: sample)

    resp = client.post('/api/v1/reports', json={'criterion': 'product', 'start': '2025-01-01', 'end': '2025-01-07'})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['total'] == 123.0
