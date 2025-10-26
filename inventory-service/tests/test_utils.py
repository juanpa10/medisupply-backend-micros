"""
Tests for small utility modules: constants, pagination and response helpers, and error handlers.
"""
from app.core.constants import Roles, ProductStatus, MeasurementUnit, SearchConfig
from app.core.utils.response import success_response, error_response, paginated_response
from app.core.utils.pagination import get_pagination_params, paginate_query
from app.core.middleware.error_handler import register_error_handlers
from flask import Flask


def test_constants_values():
    assert Roles.ADMIN in Roles.ALL_ROLES
    assert ProductStatus.ACTIVE in ProductStatus.ALL_STATUSES
    assert MeasurementUnit.KG in MeasurementUnit.ALL_UNITS
    assert SearchConfig.MIN_SEARCH_LENGTH >= 1


def test_response_helpers(app):
    # success_response and error_response return (response, status_code)
    resp, status = success_response({'a': 1}, message='ok', status_code=201)
    assert status == 201
    json_data = resp.get_json()
    assert json_data['success'] is True

    resp2, status2 = error_response('fail', status_code=400)
    assert status2 == 400
    json_data2 = resp2.get_json()
    assert json_data2['success'] is False

    # paginated_response basic
    pr, st = paginated_response([1, 2], page=1, per_page=2, total=10)
    assert st == 200
    j = pr.get_json()
    assert 'pagination' in j


def test_pagination_params_and_paginate_query(app):
    # set default config
    app.config['DEFAULT_PAGE_SIZE'] = 10
    app.config['MAX_RESULTS_PER_PAGE'] = 50

    with app.test_request_context('/?page=2&per_page=5'):
        p, pp = get_pagination_params()
        assert p == 2 and pp == 5

    # paginate_query with a fake query object
    class FakeQuery:
        def __init__(self, items):
            self._items = items

        def count(self):
            return len(self._items)

        def offset(self, n):
            self._offset = n
            return self

        def limit(self, n):
            self._limit = n
            return self

        def all(self):
            return self._items[self._offset:self._offset + self._limit]

    q = FakeQuery(list(range(30)))
    res = paginate_query(q, page=2, per_page=10)
    assert res['page'] == 2
    assert res['per_page'] == 10
    assert res['total'] == 30

    # edge cases: page < 1 and per_page outside bounds
    with app.test_request_context('/?page=0&per_page=999'):
        p2, pp2 = get_pagination_params()
        assert p2 == 1
        # per_page should be capped to MAX_RESULTS_PER_PAGE
        assert pp2 == app.config['MAX_RESULTS_PER_PAGE']

    with app.test_request_context('/?page=1&per_page=0'):
        p3, pp3 = get_pagination_params()
        assert pp3 == app.config['DEFAULT_PAGE_SIZE']


def test_register_error_handlers_routes():
    app = Flask(__name__)
    register_error_handlers(app)

    @app.route('/raise_app')
    def raise_app():
        from app.core.exceptions import AppException
        raise AppException('bad', status_code=418)

    @app.route('/raise_value')
    def raise_value():
        raise ValueError('oops')

    @app.route('/post_only', methods=['POST'])
    def post_only():
        return 'ok'

    client = app.test_client()
    r = client.get('/raise_app')
    assert r.status_code == 418

    r2 = client.get('/raise_value')
    assert r2.status_code == 400

    r3 = client.get('/post_only')
    assert r3.status_code in (404, 405)


def test_response_errors_contains_errors(app):
    # Ensure error_response includes errors field when provided
    resp, status = error_response('bad', status_code=422, errors={'field': 'err'})
    assert status == 422
    j = resp.get_json()
    assert 'errors' in j and j['errors']['field'] == 'err'
