from flask import Flask
from app.db import Base, engine
from app.controllers.api import bp, svc

def create_app():
    app = Flask(__name__)

    try:
        app.json.ensure_ascii = False          # Flask >=2.2 / 3.x
    except Exception:
        app.config['JSON_AS_ASCII'] = False    # fallback versiones viejas

    # opcional: deja claro el charset en la cabecera
    app.config['JSONIFY_MIMETYPE'] = 'application/json; charset=utf-8'

    Base.metadata.create_all(bind=engine)
    svc.seed()
    app.register_blueprint(bp)
    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9003, debug=True)
