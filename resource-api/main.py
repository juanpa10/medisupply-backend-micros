from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
import os, jwt

JWT_SECRET = os.environ.get("JWT_SECRET", "supersecret")
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "*")

app = FastAPI(title="Resource API (FastAPI)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGINS] if ALLOWED_ORIGINS != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_user_from_token(request: Request):
    auth = request.headers.get("Authorization","")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    token = auth.split(" ",1)[1]
    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return decoded
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

def require_role(role: str):
    def checker(user=Depends(get_user_from_token)):
        if user.get("role") != role:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user
    return checker

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/whoami")
def whoami(user=Depends(get_user_from_token)):
    return {"user": user.get("sub") or user.get("user"), "role": user.get("role","unknown")}

@app.post("/admin/sensitive-op")
def sensitive_op_admin(user=Depends(require_role("security_admin"))):
    return {"ok": True, "operation": "sensitive-op", "by": user.get("sub")}
