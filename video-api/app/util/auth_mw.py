from functools import wraps
from flask import request, jsonify

def require_auth(optional=False):
    def deco(fn):
        @wraps(fn)
        def w(*a, **kw):
            auth = request.headers.get("Authorization", "")
            user = None
            if auth.startswith("Bearer "):
                user = auth.split(" ", 1)[1] or None  # en real, decodificar JWT
            elif not optional:
                return jsonify({"error": "Unauthorized"}), 401
            request.user = user
            return fn(*a, **kw)
        return w
    return deco
