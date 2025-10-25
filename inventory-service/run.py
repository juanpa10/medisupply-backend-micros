"""
Punto de entrada de la aplicación Inventory Service
"""
import os
from app import create_app

# Crear la aplicación
app = create_app()

if __name__ == '__main__':
    # Crear directorios necesarios
    os.makedirs('logs', exist_ok=True)
    
    # Obtener puerto del entorno
    port = int(os.environ.get('PORT', 5003))
    
    # Ejecutar aplicación
    app.run(
        host='0.0.0.0',
        port=port,
        debug=app.config.get('DEBUG', False)
    )
