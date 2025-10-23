from flask import Flask
from app.db import Base, engine
from app.controllers.api import bp, svc
from sqlalchemy import inspect, text
import os


def create_app(config=None):
    app = Flask(__name__)
    if config:
        app.config.update(config)

    try:
        app.json.ensure_ascii = False
    except Exception:
        app.config['JSON_AS_ASCII'] = False

    app.config['JSONIFY_MIMETYPE'] = 'application/json; charset=utf-8'

    try:
        inspector = inspect(engine)
        # defensive: we don't expect a conflicting orders table from other services
    except Exception as e:
        print(f'[init] warning inspecting orders table: {e}')

    Base.metadata.create_all(bind=engine)
    # Seed only when explicitly enabled (tests expect an empty DB)
    seed_flag = app.config.get('SEED', False) or os.getenv('SEED_ORDERS') == '1'
    if seed_flag:
        svc.seed()
    app.register_blueprint(bp)

    @app.get('/health')
    def health():
        return {'status': 'alive'}

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=9006, debug=True)
