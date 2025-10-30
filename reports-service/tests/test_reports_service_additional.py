import datetime
import types
from app.services.reports_service import ReportsService


class StubRepo:
    def __init__(self, total=0, prev_total=0, top5=None, series=None, daily=None):
        self._total = total
        self._prev_total = prev_total
        self._top5 = top5 or []
        self._series = series or []
        self._daily = daily or []
        self.calls = {'total_sales': 0}

    def total_sales(self, start, end):
        # alternate behavior: first call returns _total, second call (for prev) returns _prev_total
        self.calls['total_sales'] += 1
        # if called once, return current total, if called twice, return prev_total
        if self.calls['total_sales'] == 1:
            return float(self._total)
        return float(self._prev_total)

    def group_top_n(self, start, end, group_by, n=5):
        return self._top5

    def grouped_daily_series(self, start, end, group_by):
        return self._series

    def daily_series(self, start, end):
        return self._daily


def test_invalid_criterion_raises():
    svc = ReportsService(repo=StubRepo())
    start = datetime.date(2025, 1, 1)
    end = datetime.date(2025, 1, 7)
    try:
        svc.generate_report('invalid', start, end)
        assert False, 'expected ValueError for invalid criterion'
    except ValueError:
        pass


def test_pct_change_none_when_prev_zero():
    # prev_total = 0 should make pct_change None
    repo = StubRepo(total=100.0, prev_total=0.0, top5=[{'product': 'X', 'total': 100.0}], daily=[{'date': '2025-01-01', 'total': 50.0}])
    svc = ReportsService(repo=repo)
    start = datetime.date(2025, 1, 1)
    end = datetime.date(2025, 1, 7)
    r = svc.generate_report('product', start, end)
    assert r['total'] == 100.0
    assert r['pct_change'] is None
    assert r['top5'] == [{'product': 'X', 'total': 100.0}]
    assert r['daily'] == [{'date': '2025-01-01', 'total': 50.0}]


def test_pct_change_computed_and_cache_prevents_duplicate_repo_calls(monkeypatch):
    # prev_total non-zero -> pct_change computed; also exercise TTL cache
    repo = StubRepo(total=300.0, prev_total=100.0, top5=[{'product': 'A', 'total': 300.0}], daily=[{'date': '2025-01-02', 'total': 150.0}])
    svc = ReportsService(repo=repo)
    start = datetime.date(2025, 1, 1)
    end = datetime.date(2025, 1, 7)

    # call once
    r1 = svc.generate_report('product', start, end)
    assert abs(r1['pct_change'] - 200.0) < 1e-6

    # subsequent call with same args should be served from cache (ttl_cache default 90s)
    # to make this deterministic, monkeypatch time.time so it hasn't advanced
    import time as _time
    base = _time.time()
    monkeypatch.setattr('time.time', lambda: base)

    r2 = svc.generate_report('product', start, end)
    assert r2 == r1

    # ensure repo.total_sales was called only twice total (one for total, one for prev) during first generate
    # subsequent cached call should not invoke repo.total_sales again
    assert repo.calls['total_sales'] == 2
