from flask import Flask
from app.core.utils.response import paginated_response
from app.core.auth.decorators import optional_auth


def test_paginated_response_basic():
    app = Flask(__name__)
    with app.test_request_context('/'):
        resp, status = paginated_response(['a', 'b'], page=1, per_page=2, total=5)
        assert status == 200
        body = resp.get_json()
        assert body['pagination']['total_pages'] == 3


def test_optional_auth_no_token():
    app = Flask(__name__)

    @optional_auth
    def pub():
        return 'ok'

    with app.test_request_context('/'):
        assert pub() == 'ok'
