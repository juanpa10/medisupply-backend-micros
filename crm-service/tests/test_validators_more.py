import pytest
from app.core.utils.validators import validate_phone, validate_nit, get_secure_filename
from app.core.exceptions import ValidationError


def test_validate_phone_valid():
    assert validate_phone('+12345678901') is True
    assert validate_phone('1234567') is True


def test_validate_phone_invalid():
    with pytest.raises(ValidationError):
        validate_phone('abc123')


def test_validate_nit_valid():
    assert validate_nit('12345-678') is True


def test_validate_nit_invalid():
    with pytest.raises(ValidationError):
        validate_nit('nope!')


def test_get_secure_filename():
    name = get_secure_filename('some file.pdf')
    assert ' ' not in name
