
import os, json, time
from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
from passlib.context import CryptContext

PORT = int(os.environ.get("PORT", "9001"))
JWT_SECRET = os.environ.get("JWT_SECRET", "supersecret")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
USERS_JSON = os.environ.get("USERS_JSON", '[{"email":"admin@medisupply.com","password":"Admin#123","role":"security_admin"},{"email":"viewer@medisupply.com","password":"Viewer#123","role":"viewer"}]')

pwd_ctx = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def load_users():
    data = json.loads(USERS_JSON)
    users = {}
    for u in data:
        users[u["email"]] = {"pwd_hash": pwd_ctx.hash(u["password"]), "role": u["role"]}
    return users

USERS = load_users()

app = Flask(__name__)
CORS(app)

def create_token(sub: str, role: str):
    now = int(time.time())
    payload = {"sub": sub, "role": role, "iat": now, "exp": now + ACCESS_TOKEN_EXPIRE_MINUTES * 60}
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def decode_token(token: str):
    return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/auth/login")
def login():
    body = request.get_json(force=True, silent=True) or {}
    email = body.get("email")
    password = body.get("password")
    if not email or not password:
        return jsonify({"error": "email and password are required"}), 400
    user = USERS.get(email)
    if not user or not pwd_ctx.verify(password, user["pwd_hash"]):
        return jsonify({"error": "invalid credentials"}), 401
    token = create_token(email, user["role"])
    return jsonify({"access_token": token, "token_type": "Bearer", "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60, "role": user["role"]})

@app.get("/auth/verify")
def verify():
    token = request.args.get("token")
    if not token:
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            token = auth.split(" ",1)[1]
    if not token:
        return jsonify({"valid": False, "error":"missing token"}), 400
    try:
        decoded = decode_token(token)
        return jsonify({"valid": True, "sub": decoded.get("sub"), "role": decoded.get("role")})
    except Exception as e:
        return jsonify({"valid": False, "error": str(e)}), 401

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
