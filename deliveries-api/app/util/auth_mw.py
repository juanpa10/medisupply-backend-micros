from functools import wraps
from flask import request, jsonify
def require_auth(optional=True):
    def deco(fn):
        @wraps(fn)
        def w(*a, **kw):
            if not optional and not request.headers.get("Authorization","").startswith("Bearer "):
                return jsonify({"error":"unauthorized"}), 401
            return fn(*a, **kw)
        return w
    return deco
