import os, pytest
from app.app import create_app
from app.db import Base, engine

@pytest.fixture(autouse=True)
def _db_reset():
    # Reinicia el schema en cada test para aislar datos
    with engine.begin() as conn:
        Base.metadata.drop_all(conn)
        Base.metadata.create_all(conn)
    yield

@pytest.fixture()
def client(tmp_path):
    # La app ya apunta a Postgres por defecto; para pruebas usamos SQLite si quieres cambiarlo.
    # Dejamos Postgres por defecto y sólo reiniciamos el schema con _db_reset.
    app = create_app()
    app.config.update(TESTING=True)
    with app.test_client() as c:
        yield c
