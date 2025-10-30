import os
from flask import Flask, jsonify, send_file, request
from app.db import Base, engine, SessionLocal
from app.controllers.evidence_controller import bp as evidence_bp
from app.domain.evidence import Evidence
import hmac, hashlib, base64, time

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev")
    app.config["UPLOAD_DIR"] = os.getenv("UPLOAD_DIR", "./data/uploads")

    Base.metadata.create_all(bind=engine)
    app.session_factory = SessionLocal

    app.register_blueprint(evidence_bp)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"}), 200

    # endpoint para servir archivos con URL firmada temporal (/files?path=...&exp=...&sig=...)
    @app.get("/files")
    def get_file_signed():
        path = request.args.get("path", "")
        exp = int(request.args.get("exp", "0"))
        sig = request.args.get("sig", "")

        if exp < int(time.time()):
            return jsonify({"error": "URL expirada"}), 403

        msg = f"{path}:{exp}".encode("utf-8")
        expected = hmac.new(app.config["SECRET_KEY"].encode("utf-8"), msg, hashlib.sha256).digest()
        expected_b64 = base64.urlsafe_b64encode(expected).decode("ascii").rstrip("=")
        if not hmac.compare_digest(sig, expected_b64):
            return jsonify({"error": "Firma inválida"}), 403

        full = os.path.join(app.config["UPLOAD_DIR"], os.path.basename(path))
        if not os.path.exists(full):
            return jsonify({"error": "No existe"}), 404
        return send_file(full, as_attachment=False)

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9005, debug=True)
