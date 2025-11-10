import requests

# URL del endpoint de prueba SIN autenticación
url = "http://localhost:9008/api/v1/test-bulk-upload"

# Contenido CSV
csv_content = """nombre,codigo,descripcion,categoria_id,unidad_medida_id,proveedor_id,precio_compra,precio_venta
Producto Debug,DEBUG-001,Producto de prueba para debug,1,1,1,1.00,2.00"""

print("=== Probando endpoint SIN autenticación ===")

# Probar con text/csv directo
print("--- text/csv ---")
csv_headers = {'Content-Type': 'text/csv'}
response = requests.post(url, headers=csv_headers, data=csv_content)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
print()

# Probar con multipart/form-data  
print("--- multipart/form-data ---")
files = {'csv_file': ('debug.csv', csv_content, 'text/csv')}
response = requests.post(url, files=files)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")