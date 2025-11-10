import requests

# URL del endpoint
url = "http://localhost:9008/api/v1/products/bulk-upload"

# Obtener nuevo token 
import requests

auth_response = requests.post(
    "http://localhost:9001/auth/login",
    json={"email": "admin@medisupply.com", "password": "Admin#123"}
)
token = auth_response.json()["access_token"]

# Headers
headers = {
    'Authorization': f'Bearer {token}'
}

# Contenido CSV con códigos únicos
csv_content = """nombre,codigo,descripcion,categoria_id,unidad_medida_id,proveedor_id,precio_compra,precio_venta
Jeringa Desechable 5ml,JER-5ML,Jeringa de 5ml para uso médico,1,1,1,1.20,2.00
Mascarilla KN95,MASC-KN95,Mascarilla de protección respiratoria KN95,2,2,2,0.90,1.60
Gasas No Estériles,GAS-NEST,Gasas no estériles de algodón 5x5cm,3,3,1,0.20,0.60"""

# Probar con multipart/form-data
print("=== Probando con multipart/form-data ===")
files = {'csv_file': ('test_productos.csv', csv_content, 'text/csv')}
response = requests.post(url, headers=headers, files=files)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
print()

# Probar con text/csv directo
print("=== Probando con text/csv directo ===")
csv_headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'text/csv'
}
response = requests.post(url, headers=csv_headers, data=csv_content)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")