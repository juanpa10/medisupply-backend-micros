import requests
import json

# Obtener token
auth_response = requests.post(
    "http://localhost:9001/auth/login",
    json={"email": "admin@medisupply.com", "password": "Admin#123"}
)
token = auth_response.json()["access_token"]

url = "http://localhost:9008/api/v1/products/bulk-upload"

# CSV con varios productos
csv_content = """nombre,codigo,descripcion,categoria_id,unidad_medida_id,proveedor_id,precio_compra,precio_venta,requiere_ficha_tecnica,requiere_condiciones_almacenamiento,requiere_certificaciones_sanitarias
Jeringa 3ml Final,JER-3ML-FINAL,Jeringa de 3ml para uso médico final,1,1,1,1.10,1.85,true,false,true
Mascarilla FFP2 Final,MASC-FFP2-FINAL,Mascarilla de protección respiratoria FFP2 final,2,2,2,0.95,1.65,false,false,true
Gasas Especiales Final,GAS-ESP-FINAL,Gasas especiales de algodón 10x10cm final,3,3,1,0.30,0.85,false,true,false
Producto Sin Precios,PROD-SIN-PRECIO,Producto de ejemplo sin precios,1,1,1,,,false,false,false"""

print("=== PRUEBA COMPLETA BULK UPLOAD ===")
print("URL:", url)
print("CSV Content:")
print(csv_content)
print("\n" + "="*50)

# Test 1: multipart/form-data
print("\n1. TEST MULTIPART/FORM-DATA:")
headers = {'Authorization': f'Bearer {token}'}
files = {'csv_file': ('productos_completos.csv', csv_content, 'text/csv')}
response = requests.post(url, headers=headers, files=files)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

# Test 2: text/csv directo
print("\n2. TEST TEXT/CSV DIRECTO:")
csv_headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'text/csv; charset=utf-8'
}
# Usar códigos únicos para evitar duplicados
csv_content_direct = csv_content.replace("FINAL", "DIRECT").replace("final", "directo")
response = requests.post(url, headers=csv_headers, data=csv_content_direct.encode('utf-8'))
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

# Test 3: CSV con errores
print("\n3. TEST CSV CON ERRORES:")
csv_with_errors = """nombre,codigo,descripcion,categoria_id,unidad_medida_id,proveedor_id,precio_compra,precio_venta
,ERROR-001,Sin nombre,1,1,1,1.00,2.00
Producto OK,OK-001,Producto correcto,1,1,1,1.50,2.50
Producto Sin Categoria,,Sin categoria ni codigo,999,1,1,1.00,2.00"""

files_error = {'csv_file': ('error_test.csv', csv_with_errors, 'text/csv')}
response = requests.post(url, headers=headers, files=files_error)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

print("\n" + "="*50)
print("TESTS COMPLETADOS")