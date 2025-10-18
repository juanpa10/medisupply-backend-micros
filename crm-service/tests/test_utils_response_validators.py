import pytest
from flask import Flask
from app.core.utils.response import success_response, error_response
from app.core.utils.validators import validate_email, validate_required_fields
from app.core.exceptions import ValidationError


def test_success_response_basic():
    app = Flask(__name__)
    with app.test_request_context('/'):
        resp, status = success_response(data={'a': 1}, message='ok', status_code=200)
        assert status == 200
        assert resp.get_json().get('data')['a'] == 1
        assert resp.get_json().get('message') == 'ok'


def test_error_response():
    app = Flask(__name__)
    with app.test_request_context('/'):
        resp, status = error_response('bad', status_code=400)
        assert status == 400
        assert resp.get_json().get('message') == 'bad'


def test_validate_email():
    assert validate_email('x@y.com') is True
    with pytest.raises(ValidationError):
        validate_email('notanemail')


def test_validate_required():
    # should not raise
    assert validate_required_fields({'a': 1}, ['a']) is None
    with pytest.raises(ValidationError):
        validate_required_fields({'a': 1}, ['b'])
