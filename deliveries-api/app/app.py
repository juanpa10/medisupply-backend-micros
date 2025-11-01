from flask import Flask, jsonify
from app.db import Base, engine, SessionLocal
from app.controllers.deliveries_controller import bp as deliveries_bp

def create_app():
    app = Flask(__name__)
    Base.metadata.create_all(bind=engine)
    app.session_factory = SessionLocal
    app.register_blueprint(deliveries_bp)

    @app.get("/health")
    def health():
        return jsonify({"status":"ok"}), 200

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9021, debug=True)
