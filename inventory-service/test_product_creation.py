#!/usr/bin/env python3
"""
Script de prueba exitosa para crear un producto completo con todos los datos requeridos
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
            token = response.json().get('access_token')
            if token:
                print(f"✅ Token obtenido correctamente")
                return token
        
        print(f"❌ Error obteniendo token: {response.status_code}")
        return None
    except Exception as e:
        print(f"❌ Error conectando con auth-service: {e}")
        return None

def create_product_test():
    """Prueba crear un producto completo"""
    print("🧪 Iniciando prueba de creación de producto completo...")
    
    # 1. Obtener token
    token = get_auth_token()
    if not token:
        print("❌ No se pudo obtener token. Saliendo...")
        return
    
    headers = {
        "Authorization": f"Bearer {token}"
        # NO incluir Content-Type para form-data
    }
    
    # 2. Crear producto con todos los campos requeridos (como form data)
    print("\n📋 Creando producto con todos los campos requeridos...")
    producto_data = {
        "nombre": "Acetaminofen 500mg - Prueba API",
        "codigo": "ACET-500-API-001",
        "descripcion": "Analgésico y antipirético para alivio del dolor y fiebre. Caja x 20 tabletas",
        "categoria_id": "1",  # Como string para form data
        "unidad_medida_id": "9",  # Como string para form data
        "proveedor_id": "6",  # Como string para form data
        "precio_compra": "2000.00",
        "precio_venta": "2500.00",
        "requiere_ficha_tecnica": "true",
        "requiere_condiciones_almacenamiento": "true",
        "requiere_certificaciones_sanitarias": "true"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/products", data=producto_data, headers=headers)
        
        print(f"Status: {response.status_code}")
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Producto creado exitosamente!")
            print(f"   ID: {result['data']['id']}")
            print(f"   Nombre: {result['data']['nombre']}")
            print(f"   Código: {result['data']['codigo']}")
            print(f"   Disponible en catálogo: {result['data'].get('disponible_catalogo', 'No especificado')}")
            return result['data']['id']
        else:
            print(f"❌ Error creando producto: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error en request: {e}")
        return None

def get_product_details(product_id, token):
    """Obtiene detalles completos del producto"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/products/{product_id}", headers=headers)
        
        if response.status_code == 200:
            product = response.json()['data']
            print(f"\n📄 Detalles del producto creado:")
            print(f"   Nombre: {product['nombre']}")
            print(f"   Código: {product['codigo']}")
            print(f"   Descripción: {product['descripcion']}")
            print(f"   Precio compra: ${product.get('precio_compra', 'N/A')}")
            print(f"   Precio venta: ${product.get('precio_venta', 'N/A')}")
            print(f"   Estado: {product['status']}")
            return product
        else:
            print(f"❌ Error obteniendo detalles: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    """Función principal"""
    # Crear producto
    product_id = create_product_test()
    
    if product_id:
        # Obtener token de nuevo (podría haber expirado)
        token = get_auth_token()
        if token:
            # Obtener detalles
            get_product_details(product_id, token)
    
    print("\n🎉 ¡Prueba completada!")

if __name__ == "__main__":
    main()