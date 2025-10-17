from flask import Blueprint, request, jsonify
from app.services.roles_service import RolesService
from app.util.auth_mw import require_auth, require_role
import os
import json
from urllib import request as urlreq, error as urlerror

bp = Blueprint("api", __name__, url_prefix="/api")
svc = RolesService()

@bp.get("/health")
def health():
    return {"status":"alive"}

# ------- Helpers de validación mínima --------
def get_json():
    return request.get_json(silent=True) or {}

def require_fields(data, fields):
    missing = [f for f in fields if f not in data]
    if missing:
        return {"error":"BAD_REQUEST","missing":missing}, 400
    return None

def as_bool(x, default=False):
    return bool(x) if x is not None else default

# --------------- Endpoints -------------------

@bp.get("/users-with-roles")
@require_auth
def users_with_roles():
    return jsonify(svc.list_users_with_roles())

@bp.put("/users/<int:uid>/roles-permissions")
@require_auth
@require_role("security_admin")
def set_user_roles_permissions(uid:int):
    data = get_json()
    err = require_fields(data, ["assignments"])
    if err: return err
    if not isinstance(data["assignments"], list):
        return {"error":"BAD_REQUEST","detail":"assignments debe ser lista"}, 400

    # normaliza items
    items = []
    for it in data["assignments"]:
        if not isinstance(it, dict) or "role_id" not in it:
            return {"error":"BAD_REQUEST","detail":"cada item requiere role_id"}, 400
        items.append({
            "role_id": it["role_id"],
            "can_create": as_bool(it.get("can_create"), False),
            "can_edit":   as_bool(it.get("can_edit"),   False),
            "can_delete": as_bool(it.get("can_delete"), False),
            "can_view":   as_bool(it.get("can_view"),   True),
        })

    res = svc.set_user_roles(uid, items)
    if not res: return {"error":"NOT_FOUND"}, 404
    return res

@bp.get("/users")
@require_auth
def list_users():
    users = svc.list_users()
    out = [dict(id=u.id, names=u.names, email=u.email) for u in users]
    return jsonify(out)

@bp.post("/users")
@require_auth
#@require_role("security_admin")
def create_user():
    data = get_json()
    err = require_fields(data, ["names","email"])
    if err: return err
    # Try to delegate user creation to auth-service if available
    auth_url = os.environ.get('AUTH_SERVICE_URL', 'http://auth-service:9001')
    payload = {'email': data['email'], 'password': data.get('password'), 'names': data['names'], 'role': data.get('role')}
    try:
        req = urlreq.Request(f"{auth_url}/auth/users", data=json.dumps(payload).encode('utf-8'),
                              headers={'Content-Type': 'application/json'}, method='POST')
        with urlreq.urlopen(req, timeout=5) as resp:
            if resp.status in (200, 201):
                # auth-service returns JSON with email and role
                j = json.load(resp)
                # After successful delegation, return local representation by fetching/creating via repo
                # Ensure local DB has the user row as well (best-effort)
                try:
                    u = svc.create_user(data["names"], data["email"], None, role_name=data.get('role'))
                except Exception:
                    # If local create fails due to duplicate, try to fetch existing
                    existing = svc.list_users()
                    u = next((x for x in existing if x.email == data['email']), None)
                    # If role was requested, ensure existing local user gets that role
                    if u and data.get('role'):
                        r = svc.repo.get_role_by_name(data.get('role'))
                        if r:
                            svc.set_user_roles(u.id, [{"role_id": r.id, "can_create": True, "can_edit": True, "can_delete": True, "can_view": True}])
                return dict(id=u.id, names=u.names, email=u.email), 201
            else:
                # fallback to local create
                raise Exception('delegation_failed')
    except urlerror.URLError:
        # auth-service unreachable; fallback to local create
        pass
    except Exception:
        # delegation failed for another reason; fallback to local create
        pass

    # Local create (existing behavior)
    try:
        u = svc.create_user(data["names"], data["email"], data.get("password"), role_name=data.get('role'))
        return dict(id=u.id, names=u.names, email=u.email), 201
    except ValueError as ve:
        if str(ve) == "email_exists":
            return {"error": "email_exists"}, 400
        raise
    except Exception:
        return {"error": "could_not_create_user"}, 500

@bp.get("/roles")
@require_auth
def list_roles():
    roles = svc.list_roles()
    out = [dict(id=r.id, name=r.name, description=r.description) for r in roles]
    return jsonify(out)

@bp.post("/roles")
@require_auth
#@require_role("security_admin")
def create_role():
    data = get_json()
    err = require_fields(data, ["name"])
    if err: return err
    r = svc.create_role(data["name"], data.get("description"))
    return dict(id=r.id, name=r.name, description=r.description), 201

##Se crea endpoint para verificar el control acceso de un usuario
@bp.post("/access-control")
@require_auth
def access_control():
    data = get_json()
    err = require_fields(data, ["email","rol","action"])
    if err: return err
    r = svc.access_control(data["email"],data["rol"],data["action"])
    return dict(email=r.email, rol=r.rol, action=r.action, permission=r.permission)
