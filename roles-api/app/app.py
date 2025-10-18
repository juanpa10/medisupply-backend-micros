from flask import Flask
from app.db import Base, engine
from app.controllers.api import bp, svc
from sqlalchemy import inspect, text


def create_app():
    app = Flask(__name__)

    try:
        app.json.ensure_ascii = False          # Flask >=2.2 / 3.x
    except Exception:
        app.config['JSON_AS_ASCII'] = False    # fallback versiones viejas

    # opcional: deja claro el charset en la cabecera
    app.config['JSONIFY_MIMETYPE'] = 'application/json; charset=utf-8'

    # Defensive DB init: if a pre-existing `users` table exists but its schema
    # doesn't match what this service expects, drop it so SQLAlchemy can create
    # the correct tables. This happens when another service (e.g. auth-service)
    # previously created a different `users` table in the same DB.
    try:
        inspector = inspect(engine)
        if 'users' in inspector.get_table_names():
            cols = [c['name'] for c in inspector.get_columns('users')]
            expected = {'id', 'names', 'email', 'password'}
            if not expected.issubset(set(cols)):
                print('[init] incompatible users schema detected, dropping users table')
                with engine.begin() as conn:
                    conn.execute(text('DROP TABLE IF EXISTS users CASCADE'))
    except Exception as e:
        # best-effort: log and continue to create_all which may also fail
        print(f'[init] warning inspecting users table: {e}')

    Base.metadata.create_all(bind=engine)
    svc.seed()
    app.register_blueprint(bp)

    @app.get("/health")
    def health_root():
        return {"status": "alive"}

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9003, debug=True)
