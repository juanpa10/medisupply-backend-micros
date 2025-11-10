import requests

# Probar el endpoint de productos normal (multipart funciona)
auth_response = requests.post(
    "http://localhost:9001/auth/login",
    json={"email": "admin@medisupply.com", "password": "Admin#123"}
)
token = auth_response.json()["access_token"]

url = "http://localhost:9008/api/v1/products/bulk-upload"

csv_content = """nombre,codigo,descripcion,categoria_id,unidad_medida_id,proveedor_id,precio_compra,precio_venta
Test CSV Direct,TEST-CSV-DIRECT,Test para CSV directo,1,1,1,1.00,2.00"""

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'text/csv; charset=utf-8'
}

print("=== Test con text/csv y charset ===")
response = requests.post(url, headers=headers, data=csv_content.encode('utf-8'))
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")

# Test content-type alternativo
headers2 = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/csv'  
}

print("\n=== Test con application/csv ===")
response2 = requests.post(url, headers=headers2, data=csv_content)
print(f"Status: {response2.status_code}")
print(f"Response: {response2.text}")