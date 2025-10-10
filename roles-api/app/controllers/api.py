from flask import Blueprint, request, jsonify
from app.services.roles_service import RolesService
from app.util.auth_mw import require_auth, require_role

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
#@require_role("security_admin")
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
    u = svc.create_user(data["names"], data["email"], data.get("password"))
    return dict(id=u.id, names=u.names, email=u.email), 201

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
