"""
Punto de entrada principal de la aplicación CRM Service
"""
import os
from app import create_app
from app.config.database import db

# Crear instancia de la aplicación
app = create_app()

if __name__ == '__main__':
    # Crear directorios necesarios
    os.makedirs('logs', exist_ok=True)
    
    # Ejecutar aplicación
    app.run(
        host=os.getenv('FLASK_HOST', '0.0.0.0'),
        port=int(os.getenv('FLASK_PORT', 9004)),
        debug=os.getenv('FLASK_ENV') == 'development'
    )
