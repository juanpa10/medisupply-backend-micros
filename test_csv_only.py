import requests

# Obtener token
auth_response = requests.post(
    "http://localhost:9001/auth/login",
    json={"email": "admin@medisupply.com", "password": "Admin#123"}
)
token = auth_response.json()["access_token"]

# URL del endpoint
url = "http://localhost:9008/api/v1/products/bulk-upload"

# Contenido CSV
csv_content = """nombre,codigo,descripcion,categoria_id,unidad_medida_id,proveedor_id,precio_compra,precio_venta
Producto Test,TEST-001,Producto de prueba,1,1,1,1.00,2.00"""

# Probar con text/csv directo
print("=== Probando SOLO text/csv directo ===")
csv_headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'text/csv'
}
response = requests.post(url, headers=csv_headers, data=csv_content)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")