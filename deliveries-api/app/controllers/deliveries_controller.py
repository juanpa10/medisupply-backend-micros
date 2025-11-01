from flask import Blueprint, request, jsonify, current_app
from app.repositories.deliveries_repository import DeliveriesRepository
from app.services.deliveries_service import DeliveriesService
from app.domain.delivery import ALLOWED_STATUSES
from app.util.auth_mw import require_auth

bp = Blueprint("deliveries", __name__, url_prefix="/deliveries")
def svc(): return DeliveriesService(DeliveriesRepository(current_app.session_factory))

@bp.post("")
@require_auth(optional=True)
def create_delivery():
    body = request.get_json(force=True, silent=True) or {}
    order_id = body.get("order_id"); client_id = body.get("client_id")
    delivery_date = body.get("delivery_date"); status = body.get("status")
    if not all([order_id, client_id, delivery_date, status]):
        return jsonify({"error":"missing_fields"}), 400
    try:
        d = svc().create(int(order_id), int(client_id), str(delivery_date), str(status))
    except ValueError as e:
        if str(e) == "invalid_status":
            return jsonify({"error":"invalid_status","allowed":sorted(ALLOWED_STATUSES)}), 400
        return jsonify({"error":"invalid_date"}), 400
    return jsonify({"id": d.id, "order_id": d.order_id, "client_id": d.client_id,
                    "delivery_date": d.delivery_date.isoformat()+"Z", "status": d.status}), 201

@bp.get("")
@require_auth(optional=True)
def list_deliveries():
    limit = min(int(request.args.get("limit",50)), 100)
    cursor = request.args.get("cursor", type=int)
    rows, nxt = svc().list_all(limit=limit, cursor=cursor)
    data = [{"id":x.id,"order_id":x.order_id,"client_id":x.client_id,
             "delivery_date":x.delivery_date.isoformat()+"Z","status":x.status} for x in rows]
    return jsonify({"items": data, "next_cursor": nxt})

@bp.get("/client/<int:client_id>")
@require_auth(optional=True)
def by_client(client_id:int):
    limit = min(int(request.args.get("limit",50)), 100)
    cursor = request.args.get("cursor", type=int)
    rows, nxt = svc().list_by_client(client_id=client_id, limit=limit, cursor=cursor)
    data = [{"id":x.id,"order_id":x.order_id,"client_id":x.client_id,
             "delivery_date":x.delivery_date.isoformat()+"Z","status":x.status} for x in rows]
    return jsonify({"items": data, "next_cursor": nxt})
