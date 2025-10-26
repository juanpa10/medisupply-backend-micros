from flask import Blueprint, request, jsonify, current_app, send_file
from werkzeug.utils import secure_filename
from app.services.evidence_service import EvidenceService
from app.repositories.evidence_repository import EvidenceRepository
from app.util.auth_mw import require_auth
import os, time, hmac, hashlib, base64

bp = Blueprint("evidence", __name__, url_prefix="/evidence")

def get_service():
    repo = EvidenceRepository(current_app.session_factory)
    return EvidenceService(repo, current_app.config["UPLOAD_DIR"], current_app.config["SECRET_KEY"])

@bp.route("/upload", methods=["POST"])
@require_auth(optional=True)
def upload():
    f = request.files.get("file")
    if not f:
        return jsonify({"error": "Archivo requerido"}), 400

    evidence_type = request.form.get("evidence_type")
    client_id = request.form.get("client_id")
    product_id = request.form.get("product_id")
    visit_id = request.form.get("visit_id")
    lat = request.form.get("lat", type=float)
    lon = request.form.get("lon", type=float)

    meta = {
        "content_type": f.mimetype,
        "client_id": client_id, "product_id": product_id, "visit_id": visit_id,
        "lat": lat, "lon": lon,
        "evidence_type": evidence_type,
        "user": getattr(request, "user", None),
    }

    svc = get_service()
    # werkzeug no da size directo; usamos stream.tell tras read en servicio, así que pasamos len via Content-Length o form header si existe
    size = request.content_length or 0
    try:
        res = svc.save_upload(f.stream, secure_filename(f.filename), size, meta)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({"id": res.id, "message": "Evidencia cargada correctamente", "url": res.url}), 201

@bp.route("", methods=["GET"])
@require_auth(optional=True)
def list_recent():
    repo = EvidenceRepository(current_app.session_factory)
    items = repo.list_recent(limit=int(request.args.get("limit", 20)))
    data = [{
        "id": e.id, "filename": e.filename, "type": e.evidence_type,
        "created_at": e.created_at.isoformat() + "Z"
    } for e in items]
    return jsonify(data), 200

@bp.route("/<int:evid_id>", methods=["GET"])
@require_auth(optional=True)
def get_one(evid_id: int):
    repo = EvidenceRepository(current_app.session_factory)
    e = repo.get(evid_id)
    if not e:
        return jsonify({"error": "No existe"}), 404
    svc = get_service()
    return jsonify({
        "id": e.id,
        "filename": e.filename,
        "content_type": e.content_type,
        "size_bytes": e.size_bytes,
        "client_id": e.client_id,
        "product_id": e.product_id,
        "visit_id": e.visit_id,
        "evidence_type": e.evidence_type,
        "lat": e.lat, "lon": e.lon,
        "created_at": e.created_at.isoformat() + "Z",
        "processed": e.processed,
        "signed_url": svc.signed_url_for(e.filename, 900)
    }), 200
