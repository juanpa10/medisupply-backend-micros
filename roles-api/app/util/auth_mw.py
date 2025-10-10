from functools import wraps
from flask import request, jsonify, g
import os, jwt

SECRET = os.getenv("JWT_SECRET", "supersecret")
ALG    = os.getenv("JWT_ALGORITHM", "HS256")

def require_auth(fn):
    @wraps(fn)
    def w(*a, **kw):
        auth = request.headers.get("Authorization","")
        if not auth.startswith("Bearer "): return jsonify({"error":"UNAUTHORIZED"}), 401
        token = auth.split(" ",1)[1].strip()
        try:
            g.claims = jwt.decode(token, SECRET, algorithms=[ALG])
        except jwt.PyJWTError:
            return jsonify({"error":"INVALID_TOKEN"}), 401
        return fn(*a, **kw)
    return w

def require_role(*allowed):
    def deco(fn):
        @wraps(fn)
        def w(*a, **kw):
            role = (getattr(g,"claims",{}) or {}).get("role")
            if role not in allowed:
                return jsonify({"error":"FORBIDDEN"}), 403
            return fn(*a, **kw)
        return w
    return deco
