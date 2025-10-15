"""Auth service Flask app (single, clean implementation).

This file must contain a single definition of `app` and the DB helpers
so that `init_db.py` can import `DB_ENABLED`, `init_db` and `app`.
"""

import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from passlib.context import CryptContext
import time
import jwt

pwd_ctx = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
PORT = int(os.environ.get("PORT", "9001"))
USERS_JSON = os.environ.get(
    "USERS_JSON",
    '[{"email":"admin@medisupply.com","password":"Admin#123","role":"security_admin"},'
    '{"email":"viewer@medisupply.com","password":"Viewer#123","role":"viewer"}]',
)

DATABASE_URL = os.environ.get("DATABASE_URL")
DB_ENABLED = bool(DATABASE_URL)

# token expiry (minutes)
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
JWT_SECRET = os.environ.get("JWT_SECRET", "supersecret")

USERS = None
db = None

if not DB_ENABLED:
    data = json.loads(USERS_JSON)
    USERS = {u["email"]: {"pwd_hash": pwd_ctx.hash(u["password"]), "role": u["role"]} for u in data}
else:
    # SQLAlchemy is only imported/used when DB is enabled
    from flask_sqlalchemy import SQLAlchemy
    from sqlalchemy import inspect, text
    db = SQLAlchemy()

    # define User model at module scope so runtime code can use it
    class User(db.Model):
        __tablename__ = "users"
        id = db.Column(db.Integer, primary_key=True)
        email = db.Column(db.String(255), unique=True, nullable=False, index=True)
        pwd_hash = db.Column(db.String(255), nullable=True)
        role = db.Column(db.String(100), nullable=True)

    globals()["User"] = User

    def init_db(app):
        """Initialize DB, ensure users table, and seed default users if empty.

        Important: do not call db.init_app(app) here because the Flask process
        that imports this module already initializes the SQLAlchemy instance.
        This function should be safe to call from the entrypoint after import.
        """
        with app.app_context():
            try:
                inspector = inspect(db.engine)
                has_users = "users" in inspector.get_table_names()
            except Exception:
                has_users = False

            if has_users:
                try:
                    cols = [c["name"] for c in inspector.get_columns("users")]
                    required = {"email", "pwd_hash", "role"}
                    if not required.issubset(set(cols)):
                        print("[init_db] incompatible users schema detected, dropping users table")
                        db.session.execute(text("DROP TABLE IF EXISTS users CASCADE"))
                        db.session.commit()
                except Exception:
                    try:
                        db.session.rollback()
                    except Exception:
                        pass

            db.create_all()

            try:
                count = db.session.query(User).count()
            except Exception:
                try:
                    db.session.rollback()
                except Exception:
                    pass
                count = 0

            if count == 0:
                data = json.loads(USERS_JSON)
                for u in data:
                    user = User(email=u["email"], pwd_hash=pwd_ctx.hash(u["password"]), role=u.get("role", "viewer"))
                    db.session.add(user)
                db.session.commit()

    def get_user_from_db(email: str):
        try:
            # ensure an app context is active for DB operations
            with app.app_context():
                return db.session.query(User).filter_by(email=email).first()
        except Exception:
            try:
                db.session.rollback()
            except Exception:
                pass
            return None


app = Flask(__name__)
CORS(app)

# If DB is enabled, ensure the Flask app is configured and SQLAlchemy is initialized
if DB_ENABLED:
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    # initialize the SQLAlchemy extension for this app process
    db.init_app(app)


@app.get('/health')
def health():
    return {'ok': True}


@app.post('/auth/login')
def login():
    # Use explicit parsing and a helpful debug path if anything's wrong.
    try:
        body = request.get_json(force=True, silent=False) or {}
    except Exception as e:
        return jsonify({'error': f'invalid json: {e}'}), 400

    email = body.get('email')
    password = body.get('password')
    if not email or not password:
        return jsonify({'error': 'email and password are required'}), 400

    if not DB_ENABLED:
        user = USERS.get(email)
        if not user or not pwd_ctx.verify(password, user['pwd_hash']):
            return jsonify({'error': 'invalid credentials'}), 401
        # create JWT
        now = int(time.time())
        payload = {"sub": email, "role": user["role"], "iat": now, "exp": now + ACCESS_TOKEN_EXPIRE_MINUTES * 60}
        token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
        return jsonify({
            'access_token': token,
            'token_type': 'Bearer',
            'expires_in': ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            'role': user['role']
        })

    # DB-backed
    u = get_user_from_db(email)
    if not u or not pwd_ctx.verify(password, u.pwd_hash):
        return jsonify({'error': 'invalid credentials'}), 401
    now = int(time.time())
    payload = {"sub": email, "role": u.role, "iat": now, "exp": now + ACCESS_TOKEN_EXPIRE_MINUTES * 60}
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return jsonify({
        'access_token': token,
        'token_type': 'Bearer',
        'expires_in': ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        'role': u.role
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)

