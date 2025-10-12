"""
Script para gestionar migraciones de base de datos
"""
from flask.cli import FlaskGroup
from app import create_app
from app.config.database import db

app = create_app()
cli = FlaskGroup(app)


@cli.command("init_db")
def init_db():
    """Inicializa la base de datos"""
    db.create_all()
    print("✅ Base de datos inicializada")


@cli.command("drop_db")
def drop_db():
    """Elimina todas las tablas"""
    if input("¿Estás seguro? (y/n): ").lower() == 'y':
        db.drop_all()
        print("✅ Tablas eliminadas")


if __name__ == '__main__':
    cli()
