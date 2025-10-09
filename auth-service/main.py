from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from passlib.context import CryptContext
from typing import List
import os, json, time, jwt

JWT_SECRET = os.environ.get("JWT_SECRET", "supersecret")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
USERS_JSON = os.environ.get("USERS_JSON", '[{"user":"admin","password":"Admin#123","role":"security_admin"},{"user":"viewer","password":"Viewer#123","role":"viewer"}]')
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(BaseModel):
    user: str
    password: str
    role: str

class LoginRequest(BaseModel):
    user: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int

def make_users() -> List[User]:
    data = json.loads(USERS_JSON)
    users = []
    for u in data:
        users.append(User(**u))
    return users

USERS = make_users()
HASHED = {u.user: pwd_ctx.hash(u.password) for u in USERS}
ROLES = {u.user: u.role for u in USERS}

app = FastAPI(title="Auth Service (FastAPI)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def verify_user(username: str, password: str) -> str:
    if username not in HASHED:
        return None
    if not pwd_ctx.verify(password, HASHED[username]):
        return None
    return ROLES[username]

def create_access_token(sub: str, role: str, expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    now = int(time.time())
    payload = {"sub": sub, "role": role, "iat": now, "exp": now + expires_minutes * 60}
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

@app.post("/auth/login", response_model=TokenResponse)
def login(req: LoginRequest):
    role = verify_user(req.username, req.password)
    if not role:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(req.username, role)
    return TokenResponse(access_token=token, expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60)

class VerifyResponse(BaseModel):
    sub: str
    role: str
    valid: bool

@app.get("/auth/verify", response_model=VerifyResponse)
def verify(token: str):
    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return VerifyResponse(sub=decoded.get("sub") or decoded.get("user"), role=decoded.get("role","unknown"), valid=True)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
