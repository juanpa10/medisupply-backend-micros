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
    
    def load_users():
        """Return in-memory USERS dict (helpers for tests)."""
        data = json.loads(USERS_JSON)
        return {u["email"]: {"pwd_hash": pwd_ctx.hash(u["password"]), "role": u["role"]} for u in data}

else:
    # SQLAlchemy is only imported/used when DB is enabled
    from flask_sqlalchemy import SQLAlchemy
    from sqlalchemy import inspect, text
    db = SQLAlchemy()

    # define User model at module scope so runtime code can use it
    class User(db.Model):
        __tablename__ = "users"
        id = db.Column(db.Integer, primary_key=True)
        # Support multiple schemas: roles-api uses `names` and `password` columns,
        # while auth-service originally used `email`, `pwd_hash`, `role`.
        names = db.Column(db.String(255), nullable=True)
        email = db.Column(db.String(255), unique=True, nullable=False, index=True)
        pwd_hash = db.Column(db.String(255), nullable=True)
        # legacy/plain password column present in roles-api schema
        password = db.Column(db.String(255), nullable=True)
        # role string if present; otherwise we may resolve it via user_roles -> roles
        role = db.Column(db.String(100), nullable=True)

    class AuthUserRole(db.Model):
        __tablename__ = 'auth_user_roles'
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, nullable=False, index=True)
        role = db.Column(db.String(100), nullable=False)

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

            # Do NOT drop existing users table. Accept multiple schemas used by other
            # services (roles-api). Create missing tables if possible, and seed only
            # using the available columns so inserts don't fail.
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
                # Inspect current columns and insert only into those present
                try:
                    cols = [c["name"] for c in inspector.get_columns("users")]
                except Exception:
                    cols = []

                for u in data:
                    insert_data = {}
                    if "email" in cols:
                        insert_data["email"] = u["email"]
                    if "pwd_hash" in cols:
                        insert_data["pwd_hash"] = pwd_ctx.hash(u["password"])
                    elif "password" in cols:
                        # roles-api uses plaintext password column; seed plaintext there
                        insert_data["password"] = u["password"]
                    if "role" in cols:
                        insert_data["role"] = u.get("role", "viewer")
                    if "names" in cols and not insert_data.get("names"):
                        insert_data["names"] = u.get("names") or u["email"]

                    if insert_data:
                        # Use a table insert that only writes existing columns
                        db.session.execute(User.__table__.insert().values(**insert_data))
                        # If the users table doesn't support a native `role` column but
                        # the seed provided a role, persist it into `auth_user_roles`.
                        if 'role' not in cols and u.get('role'):
                            # Try to find the inserted user's id and persist role
                            try:
                                db.session.flush()
                                row = db.session.execute(text("SELECT id FROM users WHERE email=:email LIMIT 1"), {'email': u['email']}).fetchone()
                                if row:
                                    uid = row[0]
                                    db.session.execute(AuthUserRole.__table__.insert().values(user_id=uid, role=u.get('role')))
                            except Exception:
                                try:
                                    db.session.rollback()
                                except Exception:
                                    pass
                db.session.commit()

    def get_user_from_db(email: str):
        # Use a resilient raw-SQL approach: detect which columns exist and select only them.
        try:
            with app.app_context():
                try:
                    inspector = inspect(db.engine)
                    cols = {c['name'] for c in inspector.get_columns('users')}
                except Exception:
                    cols = set()

                wanted = ['id', 'email', 'names', 'pwd_hash', 'password', 'role']
                sel_cols = [c for c in wanted if c in cols]
                if not sel_cols:
                    return None

                q = text(f"SELECT {', '.join(sel_cols)} FROM users WHERE email=:email LIMIT 1")
                row = db.session.execute(q, {'email': email}).fetchone()
                if not row:
                    return None

                # Build a simple object with expected attributes
                from types import SimpleNamespace
                obj = SimpleNamespace()
                for idx, col in enumerate(sel_cols):
                    setattr(obj, col, row[idx])

                # Ensure attributes exist even if column missing
                for col in wanted:
                    if not hasattr(obj, col):
                        setattr(obj, col, None)

                # If role missing, try to resolve via user_roles -> roles
                if not getattr(obj, 'role', None):
                    if 'user_roles' in inspect(db.engine).get_table_names():
                        try:
                            r = db.session.execute(
                                text(
                                    "SELECT r.name FROM roles r JOIN user_roles ur ON ur.role_id=r.id WHERE ur.user_id=:uid LIMIT 1"
                                ),
                                {"uid": obj.id},
                            ).fetchone()
                            if r:
                                obj.role = r[0]
                        except Exception:
                            try:
                                db.session.rollback()
                            except Exception:
                                pass
                # If still missing, check our auth_user_roles fallback table
                if not getattr(obj, 'role', None) and 'auth_user_roles' in inspect(db.engine).get_table_names():
                    try:
                        r2 = db.session.execute(text("SELECT role FROM auth_user_roles WHERE user_id=:uid LIMIT 1"), {"uid": obj.id}).fetchone()
                        if r2:
                            obj.role = r2[0]
                    except Exception:
                        try:
                            db.session.rollback()
                        except Exception:
                            pass

                return obj
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
    # If INIT_DB is set at import time (tests use this), run init_db to create/seed tables
    if os.environ.get('INIT_DB', '').lower() in ('1', 'true'):
        try:
            # run idempotent init
            init_db(app)
        except Exception:
            # swallow failures during import-time init to keep behavior permissive in tests
            pass


def create_token(sub: str, role: str):
    now = int(time.time())
    payload = {"sub": sub, "role": role, "iat": now, "exp": now + ACCESS_TOKEN_EXPIRE_MINUTES * 60}
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def decode_token(token: str):
    return jwt.decode(token, JWT_SECRET, algorithms=["HS256"]) 


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
    if not u:
        print(f"[auth-debug] login: user not found for email={email}")
        return jsonify({'error': 'invalid credentials'}), 401

    # Accept either a stored password hash (`pwd_hash`) or a legacy/plain `password` column.
    valid = False
    print(f"[auth-debug] login: found user email={getattr(u,'email',None)} pwd_hash_present={bool(getattr(u,'pwd_hash',None))} password_field={getattr(u,'password',None)!r}")
    if getattr(u, 'pwd_hash', None):
        try:
            valid = pwd_ctx.verify(password, u.pwd_hash)
        except Exception:
            valid = False
    if not valid and getattr(u, 'password', None):
        # fallback: compare plaintext (insecure, but compatible with roles-api)
        valid = (password == u.password)

    print(f"[auth-debug] login: password check result={valid}")

    if not valid:
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



@app.get('/auth/verify')
def verify():
    # Accept token via query param `token` or Authorization header `Bearer <token>`
    token = request.args.get('token')
    if not token:
        auth = request.headers.get('Authorization', '')
        if auth.startswith('Bearer '):
            token = auth.split(None, 1)[1].strip()

    if not token:
        return jsonify({'valid': False}), 400

    try:
        payload = decode_token(token)
        return jsonify({'valid': True, 'role': payload.get('role'), 'sub': payload.get('sub')}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'valid': False, 'error': 'token expired'}), 401
    except Exception:
        return jsonify({'valid': False, 'error': 'invalid token'}), 401



@app.post('/auth/users')
def create_user_api():
    """Create a user in the auth DB. Expects JSON with email, password, optional names and role.

    This endpoint is intended for other services (like roles-api) to delegate
    user creation so a single service is the source of truth for credentials.
    """
    try:
        body = request.get_json(force=True, silent=False) or {}
    except Exception as e:
        return jsonify({'error': f'invalid json: {e}'}), 400

    email = body.get('email')
    password = body.get('password')
    names = body.get('names')
    role = body.get('role')
    if not email or not password:
        return jsonify({'error': 'email and password are required'}), 400

    if not DB_ENABLED:
        # In-memory mode: create in USERS dict
        USERS[email] = {'pwd_hash': pwd_ctx.hash(password), 'role': role or 'viewer'}
        return jsonify({'email': email, 'role': role or 'viewer'}), 201

    # DB-enabled: insert using SQLAlchemy, writing to columns that exist
    try:
        with app.app_context():
            # inspect columns
            inspector = inspect(db.engine)
            cols = [c['name'] for c in inspector.get_columns('users')] if 'users' in inspector.get_table_names() else []

            insert_data = {}
            if 'email' in cols:
                insert_data['email'] = email
            if 'pwd_hash' in cols:
                insert_data['pwd_hash'] = pwd_ctx.hash(password)
            elif 'password' in cols:
                insert_data['password'] = password
            if 'names' in cols and names:
                insert_data['names'] = names
            if 'role' in cols and role:
                insert_data['role'] = role

            if not insert_data:
                return jsonify({'error': 'no writable columns available'}), 500

            db.session.execute(User.__table__.insert().values(**insert_data))
            # If the users table didn't include a `role` column but the caller
            # requested one, persist it in auth_user_roles so future lookups can
            # resolve it for login and token creation.
            if 'role' not in cols and role:
                try:
                    # fetch user id and insert role mapping
                    row = db.session.execute(text("SELECT id FROM users WHERE email=:email LIMIT 1"), {'email': email}).fetchone()
                    if row:
                        uid = row[0]
                        db.session.execute(AuthUserRole.__table__.insert().values(user_id=uid, role=role))
                except Exception:
                    try:
                        db.session.rollback()
                    except Exception:
                        pass

            db.session.commit()
            # Return the requested role so callers know what role was set.
            return jsonify({'email': email, 'role': role or insert_data.get('role')}), 201
    except Exception as e:
        try:
            db.session.rollback()
        except Exception:
            pass
        return jsonify({'error': 'could_not_create_user', 'detail': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)

