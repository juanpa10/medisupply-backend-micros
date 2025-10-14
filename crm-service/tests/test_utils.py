from app.core.utils.pagination import paginate_query
from sqlalchemy import select


class DummyQuery:
    def __init__(self, items):
        self._items = items

    def filter(self, *args, **kwargs):
        return self

    def count(self):
        return len(self._items)

    def limit(self, n):
        class L:
            def __init__(self, items, n):
                self._items = items
                self._n = n

            def offset(self, o):
                class O:
                    def __init__(self, items, n, o):
                        self._items = items
                        self._n = n
                        self._o = o

                    def all(self):
                        return self._items[self._o:self._o + self._n]

                return O(self._items, self._n, o)

        return L(self._items, n)

    def offset(self, o):
        # support calling offset() first then limit()
        class Off:
            def __init__(self, items, o):
                self._items = items
                self._o = o

            def limit(self, n):
                class L2:
                    def __init__(self, items, o, n):
                        self._items = items
                        self._o = o
                        self._n = n

                    def all(self):
                        return self._items[self._o:self._o + self._n]

                return L2(self._items, self._o, n)

        return Off(self._items, o)


def test_paginate_query_basic(monkeypatch):
    items = list(range(30))
    dq = DummyQuery(items)
    from app import create_app
    app = create_app('testing')
    with app.test_request_context('/?page=1&per_page=10'):
        res = paginate_query(dq)
    assert 'items' in res
    assert 'total' in res
    assert res['total'] == 30
