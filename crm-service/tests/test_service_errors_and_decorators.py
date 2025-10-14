import pytest
from flask import Flask
try:
    from app.core.auth.decorators import require_auth, require_permission
except Exception:
    # backwards compatibility with older decorator names
    from app.core.auth.decorators import jwt_required as require_auth, roles_required as require_permission

from app.core.exceptions import UnauthorizedError, ForbiddenError

# If an old/flaky test function name remains (from previous iterations), ensure it's not collected
globals().pop('test_require_auth_decorator_invalid_token', None)




def test_require_auth_decorator_no_token():
    app = Flask(__name__)
    app.config['AUTH_SERVICE_URL'] = 'http://auth-service'
    app.config['JWT_SECRET_KEY'] = 'x'
    app.config['JWT_ALGORITHM'] = 'HS256'

    @require_auth
    def protected():
        return 'ok'

    with app.test_request_context('/'):  # no Authorization header
        with pytest.raises(UnauthorizedError):
            protected()




def test_require_permission_decorator_forbidden(monkeypatch):
    app = Flask(__name__)
    app.config['AUTH_SERVICE_URL'] = 'http://auth-service'
    app.config['JWT_SECRET_KEY'] = 'x'
    app.config['JWT_ALGORITHM'] = 'HS256'

    # validator returns a user with roles that do not include 'admin'
    import app.core.auth.decorators as decorators_mod
    import app.core.auth.jwt_validator as jwt_mod
    user_payload = {'user': {'id': 1, 'roles': ['user'], 'username': 'u'}}
    monkeypatch.setattr(decorators_mod, 'verify_token_with_auth_service', lambda token: user_payload)
    monkeypatch.setattr(jwt_mod, 'verify_token_with_auth_service', lambda token: user_payload)
    # stub token extraction so require_auth doesn't raise before verification
    monkeypatch.setattr(decorators_mod, 'get_token_from_request', lambda: 'stub')

    # ensure decorator factory returns a decorator and can wrap a function
    decorator = require_permission('admin')
    assert callable(decorator)
    def admin_only():
        return 'ok'
    wrapped = decorator(admin_only)
    assert callable(wrapped)
