import datetime
from dateutil.relativedelta import relativedelta
from functools import wraps
import time

from app.repositories.repo import Repo


def ttl_cache(ttl_seconds=60):
    cache = {}
    def deco(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            key = (args, tuple(sorted(kwargs.items())))
            entry = cache.get(key)
            now = time.time()
            if entry and now - entry[0] < ttl_seconds:
                return entry[1]
            val = f(*args, **kwargs)
            cache[key] = (now, val)
            return val
        return wrapped
    return deco


class ReportsService:
    def __init__(self, repo: Repo|None=None):
        self.repo = repo or Repo()

    @ttl_cache(ttl_seconds=90)
    def generate_report(self, criterion: str, start: datetime.date, end: datetime.date):
        # validate criterion
        if criterion not in ('salesperson', 'product', 'zone'):
            raise ValueError('invalid criterion')

        total = self.repo.total_sales(start, end)

        # previous period
        delta = end - start
        prev_end = start - datetime.timedelta(days=1)
        prev_start = prev_end - delta
        prev_total = self.repo.total_sales(prev_start, prev_end)

        pct_change = None
        if prev_total:
            pct_change = (total - prev_total) / prev_total * 100.0

        top5 = self.repo.group_top_n(start, end, criterion, n=5)

        series = self.repo.grouped_daily_series(start, end, criterion)

        # adapt series into timeseries buckets aggregated across groups for chart
        # produce daily totals (for charting) aggregated
        daily = self.repo.daily_series(start, end)

        return {
            'criterion': criterion,
            'start': start.isoformat(),
            'end': end.isoformat(),
            'total': total,
            'pct_change': pct_change,
            'top5': top5,
            'series': series,
            'daily': daily,
        }
