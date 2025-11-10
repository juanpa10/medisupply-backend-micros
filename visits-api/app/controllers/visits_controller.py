from flask import Blueprint, request, jsonify, current_app
from app.repositories.visits_repository import VisitsRepository
from app.services.visits_service import VisitsService
from app.util.auth_mw import require_auth

bp = Blueprint("visits", __name__, url_prefix="/visits")
def svc(): return VisitsService(VisitsRepository(current_app.session_factory))

@bp.post("")
@require_auth(optional=True)
def create_visit():
    b = request.get_json(force=True, silent=True) or {}
    visit_id = b.get("visit_id"); commercial_id = b.get("commercial_id"); date = b.get("date"); client_ids = b.get("client_ids")
    if not all([visit_id, commercial_id, date, client_ids]): return jsonify({"error":"missing_fields"}), 400
    try: v = svc().create_visit(int(visit_id), int(commercial_id), str(date), list(client_ids))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({"id": v.id, "commercial_id": v.commercial_id, "date": v.date.isoformat()+"Z",
                    "stops":[{"client_id": s.client_id, "position": s.position, "status": s.status} for s in sorted(v.stops, key=lambda x: x.position)]}), 201

@bp.get("")
@require_auth(optional=True)
def list_all():
    limit = min(int(request.args.get("limit",50)), 100); cursor = request.args.get("cursor", type=int)
    rows, nxt = svc().list_all(limit, cursor)
    data = [{"id":v.id,"commercial_id":v.commercial_id,"date":v.date.isoformat()+"Z",
             "stops":[{"client_id": s.client_id, "position": s.position, "status": s.status} for s in sorted(v.stops, key=lambda x: x.position)]} for v in rows]
    return jsonify({"items": data, "next_cursor": nxt})

@bp.get("/by-dates")
@require_auth(optional=True)
def by_dates():
    df = request.args.get("from"); dt = request.args.get("to")
    if not df or not dt: return jsonify({"error":"missing_dates"}), 400
    limit = min(int(request.args.get("limit",50)), 100); cursor = request.args.get("cursor", type=int)
    try: rows, nxt = svc().list_by_dates(df, dt, limit, cursor)
    except ValueError: return jsonify({"error":"invalid_date"}), 400
    data = [{"id":v.id,"commercial_id":v.commercial_id,"date":v.date.isoformat()+"Z",
             "stops":[{"client_id": s.client_id, "position": s.position, "status": s.status} for s in sorted(v.stops, key=lambda x: x.position)]} for v in rows]
    return jsonify({"items": data, "next_cursor": nxt})

@bp.get("/by-commercial/<int:commercial_id>")
@require_auth(optional=True)
def by_commercial(commercial_id:int):
    limit = min(int(request.args.get("limit",50)), 100); cursor = request.args.get("cursor", type=int)
    rows, nxt = svc().list_by_commercial(commercial_id, limit, cursor)
    data = [{"id":v.id,"commercial_id":v.commercial_id,"date":v.date.isoformat()+"Z",
             "stops":[{"client_id": s.client_id, "position": s.position, "status": s.status} for s in sorted(v.stops, key=lambda x: x.position)]} for v in rows]
    return jsonify({"items": data, "next_cursor": nxt})
