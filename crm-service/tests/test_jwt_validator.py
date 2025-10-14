import jwt
import time
from app.core.auth.jwt_validator import validate_jwt_token
from app import create_app
from app.config.settings import get_config


def test_validate_jwt_token_valid(monkeypatch):
    app = create_app('testing')
    config = get_config('testing')
    payload = {"sub": "user@example.com", "role": "viewer", "iat": int(time.time()), "exp": int(time.time()) + 60}
    token = jwt.encode(payload, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM)

    with app.app_context():
        decoded = validate_jwt_token(token)
        assert decoded['sub'] == 'user@example.com'


def test_validate_jwt_token_expired(monkeypatch):
    app = create_app('testing')
    config = get_config('testing')
    payload = {"sub": "user@example.com", "role": "viewer", "iat": int(time.time()) - 120, "exp": int(time.time()) - 60}
    token = jwt.encode(payload, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM)

    with app.app_context():
        from app.core.exceptions import UnauthorizedError
        try:
            validate_jwt_token(token)
            assert False, "Expected exception for expired token"
        except UnauthorizedError as e:
            # Ensure the correct exception type is raised for expired token
            assert isinstance(e, UnauthorizedError)
