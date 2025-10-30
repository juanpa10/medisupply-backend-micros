"""
Configuración de base de datos
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Instancias de extensiones
db = SQLAlchemy()
migrate = Migrate()
