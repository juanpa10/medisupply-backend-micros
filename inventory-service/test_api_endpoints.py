#!/usr/bin/env python3
"""
Script para crear datos maestros básicos mediante API
"""
import requests
import json

BASE_URL = "http://localhost:9008/api/v1"
AUTH_URL = "http://localhost:9001/auth/login"

def get_auth_token():
    """Obtiene token de autenticación del auth-service"""
    try:
        response = requests.post(AUTH_URL, json={
            "email": "admin@medisupply.com",
            "password": "Admin#123"
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"📄 Response completa: {json.dumps(data, indent=2)}")
            
            # Buscar token en diferentes posibles estructuras
            token = None
            if 'data' in data and 'access_token' in data['data']:
                token = data['data']['access_token']
            elif 'access_token' in data:
                token = data['access_token']
            elif 'token' in data:
                token = data['token']
            
            if token:
                print(f"✅ Token obtenido correctamente")
                return token
            else:
                print(f"❌ No se encontró token en la respuesta")
                return None
        else:
            print(f"❌ Error obteniendo token: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error conectando con auth-service: {e}")
        return None

def test_api_endpoint(endpoint, method="GET", data=None, files=None, token=None):
    """Prueba un endpoint de la API"""
    url = f"{BASE_URL}{endpoint}"
    headers = {}
    
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            if files:
                response = requests.post(url, data=data, files=files, headers=headers)
            else:
                headers['Content-Type'] = 'application/json'
                response = requests.post(url, json=data, headers=headers)
        
        print(f"{method} {endpoint}")
        print(f"Status: {response.status_code}")
        
        if response.status_code < 400:
            print(f"✅ Éxito: {response.json()}")
        else:
            print(f"❌ Error: {response.text}")
        
        return response
        
    except Exception as e:
        print(f"❌ Error en request: {e}")
        return None

def main():
    """Función principal para probar la API"""
    print("🧪 Iniciando pruebas de la API de productos...")
    
    # 1. Obtener token
    print("\n1. Obteniendo token de autenticación...")
    token = get_auth_token()
    if not token:
        print("❌ No se pudo obtener token. Saliendo...")
        return
    
    # 2. Probar documentación (sin auth)
    print("\n2. Probando endpoint de documentación...")
    test_api_endpoint("/products/docs")
    
    # 3. Probar listado de categorías
    print("\n3. Probando listado de categorías...")
    test_api_endpoint("/categorias", token=token)
    
    # 4. Crear una categoría
    print("\n4. Creando una categoría...")
    categoria_data = {
        "nombre": "Medicamentos Básicos",
        "descripcion": "Medicamentos de uso común y básico"
    }
    test_api_endpoint("/categorias", method="POST", data=categoria_data, token=token)
    
    # 5. Crear una unidad de medida
    print("\n5. Creando una unidad de medida...")
    unidad_data = {
        "nombre": "Tabletas",
        "abreviatura": "tab",
        "descripcion": "Tabletas o comprimidos"
    }
    test_api_endpoint("/unidades-medida", method="POST", data=unidad_data, token=token)
    
    # 6. Crear un proveedor
    print("\n6. Creando un proveedor...")
    proveedor_data = {
        "nombre": "Laboratorios Test SAS",
        "nit": "900123456-1",
        "contacto_nombre": "María González",
        "contacto_telefono": "+57 1 123-4567",
        "contacto_email": "contacto@labtest.com",
        "direccion": "Calle 100 #20-30, Bogotá",
        "pais": "Colombia"
    }
    test_api_endpoint("/proveedores", method="POST", data=proveedor_data, token=token)
    
    # 7. Probar listado de productos
    print("\n7. Probando listado de productos...")
    test_api_endpoint("/products", token=token)
    
    # 8. Crear un producto básico
    print("\n8. Creando un producto básico...")
    producto_data = {
        "nombre": "Paracetamol 500mg",
        "descripcion": "Analgésico y antipirético para alivio del dolor",
        "categoria_id": 1,
        "unidad_medida_id": 1,
        "proveedor_id": 1,
        "precio": 2500.00,
        "codigo": "PAR-500-001"
    }
    test_api_endpoint("/products", method="POST", data=producto_data, token=token)
    
    print("\n🎉 ¡Pruebas completadas!")

if __name__ == "__main__":
    main()