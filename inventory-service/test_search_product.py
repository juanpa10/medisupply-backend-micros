"""
Script de prueba para el endpoint de búsqueda por producto

Este script prueba la nueva funcionalidad de búsqueda de inventario
por nombre, código o referencia del producto.

Ejecutar: python test_search_product.py
"""
import requests
import json
from typing import Dict, Any


BASE_URL = "http://localhost:5003/api/v1"
AUTH_URL = "http://localhost:9001/api/v1/auth"


def print_section(title: str):
    """Imprime un título de sección"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def print_result(response: requests.Response):
    """Imprime el resultado de una petición"""
    print(f"\nStatus Code: {response.status_code}")
    try:
        data = response.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except:
        print(response.text)


def get_auth_token() -> str:
    """Obtiene un token de autenticación"""
    print_section("🔐 Obteniendo Token de Autenticación")
    
    try:
        response = requests.post(
            f"{AUTH_URL}/login",
            json={
                "username": "admin",
                "password": "admin123"
            },
            timeout=5
        )
        
        if response.status_code == 200:
            token = response.json().get('data', {}).get('token')
            print(f"✅ Token obtenido exitosamente")
            return token
        else:
            print(f"❌ Error al obtener token: {response.status_code}")
            print_result(response)
            return None
            
    except requests.exceptions.ConnectionError:
        print("⚠️  auth-service no está disponible en puerto 9001")
        print("   Continuando sin autenticación (algunos tests pueden fallar)")
        return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


def test_search_without_auth():
    """Test 1: Búsqueda sin autenticación (debe fallar)"""
    print_section("Test 1: Búsqueda sin autenticación")
    
    response = requests.get(
        f"{BASE_URL}/inventory/search-product",
        params={"q": "paracetamol"}
    )
    
    print_result(response)
    
    if response.status_code == 401:
        print("✅ Test PASADO: Rechaza peticiones sin autenticación")
    else:
        print("❌ Test FALLIDO: Debería rechazar peticiones sin token")


def test_search_without_query(token: str):
    """Test 2: Búsqueda sin parámetro q"""
    print_section("Test 2: Búsqueda sin parámetro 'q'")
    
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    response = requests.get(
        f"{BASE_URL}/inventory/search-product",
        headers=headers
    )
    
    print_result(response)
    
    if response.status_code == 400:
        print("✅ Test PASADO: Valida parámetro requerido")
    else:
        print("❌ Test FALLIDO: Debería validar parámetro 'q'")


def test_search_short_query(token: str):
    """Test 3: Búsqueda con query muy corto (< 2 caracteres)"""
    print_section("Test 3: Búsqueda con query muy corto")
    
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    response = requests.get(
        f"{BASE_URL}/inventory/search-product",
        params={"q": "a"},
        headers=headers
    )
    
    print_result(response)
    
    if response.status_code == 400:
        print("✅ Test PASADO: Valida longitud mínima")
    else:
        print("❌ Test FALLIDO: Debería validar longitud mínima de 2 caracteres")


def test_search_by_name(token: str):
    """Test 4: Búsqueda por nombre de producto"""
    print_section("Test 4: Búsqueda por nombre 'paracetamol'")
    
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    response = requests.get(
        f"{BASE_URL}/inventory/search-product",
        params={"q": "paracetamol"},
        headers=headers
    )
    
    print_result(response)
    
    if response.status_code == 200:
        data = response.json()
        results = data.get('data', [])
        
        if len(results) > 0:
            print(f"\n✅ Test PASADO: Encontró {len(results)} producto(s)")
            
            # Verificar estructura de respuesta
            first_item = results[0]
            if 'product_info' in first_item:
                product_info = first_item['product_info']
                print(f"\n📦 Producto encontrado:")
                print(f"   - Nombre: {product_info.get('nombre')}")
                print(f"   - Código: {product_info.get('codigo')}")
                print(f"   - Referencia: {product_info.get('referencia')}")
                print(f"   - Stock disponible: {first_item.get('cantidad_disponible')}")
                print(f"   - Ubicación: {first_item.get('ubicacion_completa')}")
                print("✅ Estructura de respuesta correcta")
            else:
                print("⚠️  Falta 'product_info' en la respuesta")
        else:
            print("⚠️  No se encontraron resultados")
    else:
        print("❌ Test FALLIDO")


def test_search_by_code(token: str):
    """Test 5: Búsqueda por código de producto"""
    print_section("Test 5: Búsqueda por código 'MED-001'")
    
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    response = requests.get(
        f"{BASE_URL}/inventory/search-product",
        params={"q": "MED-001"},
        headers=headers
    )
    
    print_result(response)
    
    if response.status_code == 200:
        data = response.json()
        results = data.get('data', [])
        
        if len(results) > 0:
            print(f"\n✅ Test PASADO: Encontró {len(results)} producto(s) por código")
        else:
            print("⚠️  No se encontraron resultados")
    else:
        print("❌ Test FALLIDO")


def test_search_by_reference(token: str):
    """Test 6: Búsqueda por referencia"""
    print_section("Test 6: Búsqueda por referencia 'REF-PARA'")
    
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    response = requests.get(
        f"{BASE_URL}/inventory/search-product",
        params={"q": "REF-PARA"},
        headers=headers
    )
    
    print_result(response)
    
    if response.status_code == 200:
        data = response.json()
        results = data.get('data', [])
        
        if len(results) > 0:
            print(f"\n✅ Test PASADO: Encontró {len(results)} producto(s) por referencia")
        else:
            print("⚠️  No se encontraron resultados")
    else:
        print("❌ Test FALLIDO")


def test_search_with_bodega_filter(token: str):
    """Test 7: Búsqueda con filtro de bodega"""
    print_section("Test 7: Búsqueda con filtro de bodega")
    
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    response = requests.get(
        f"{BASE_URL}/inventory/search-product",
        params={"q": "ibuprofeno", "bodega_id": 1},
        headers=headers
    )
    
    print_result(response)
    
    if response.status_code == 200:
        data = response.json()
        results = data.get('data', [])
        
        if len(results) > 0:
            print(f"\n✅ Test PASADO: Encontró {len(results)} en bodega 1")
            
            # Verificar que todos sean de bodega 1
            all_bodega_1 = all(item.get('bodega_id') == 1 for item in results)
            if all_bodega_1:
                print("✅ Filtro de bodega funcionando correctamente")
            else:
                print("⚠️  Algunos resultados no son de bodega 1")
        else:
            print("⚠️  No se encontraron resultados en bodega 1")
    else:
        print("❌ Test FALLIDO")


def test_search_case_insensitive(token: str):
    """Test 8: Búsqueda case-insensitive"""
    print_section("Test 8: Búsqueda case-insensitive (PARACETAMOL vs paracetamol)")
    
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    # Búsqueda en mayúsculas
    response_upper = requests.get(
        f"{BASE_URL}/inventory/search-product",
        params={"q": "PARACETAMOL"},
        headers=headers
    )
    
    # Búsqueda en minúsculas
    response_lower = requests.get(
        f"{BASE_URL}/inventory/search-product",
        params={"q": "paracetamol"},
        headers=headers
    )
    
    if response_upper.status_code == 200 and response_lower.status_code == 200:
        results_upper = len(response_upper.json().get('data', []))
        results_lower = len(response_lower.json().get('data', []))
        
        if results_upper == results_lower and results_upper > 0:
            print(f"✅ Test PASADO: Ambas búsquedas retornan {results_upper} resultado(s)")
            print("   La búsqueda es case-insensitive")
        else:
            print(f"⚠️  Mayúsculas: {results_upper}, Minúsculas: {results_lower}")
    else:
        print("❌ Test FALLIDO")


def test_search_partial_match(token: str):
    """Test 9: Búsqueda con coincidencia parcial"""
    print_section("Test 9: Búsqueda parcial 'meta' (debería encontrar Metformina)")
    
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    response = requests.get(
        f"{BASE_URL}/inventory/search-product",
        params={"q": "meta"},
        headers=headers
    )
    
    print_result(response)
    
    if response.status_code == 200:
        data = response.json()
        results = data.get('data', [])
        
        if len(results) > 0:
            print(f"\n✅ Test PASADO: Búsqueda parcial funciona ({len(results)} resultados)")
            for item in results:
                nombre = item.get('product_info', {}).get('nombre', 'N/A')
                print(f"   - {nombre}")
        else:
            print("⚠️  No se encontraron resultados")
    else:
        print("❌ Test FALLIDO")


def test_search_no_results(token: str):
    """Test 10: Búsqueda sin resultados"""
    print_section("Test 10: Búsqueda sin resultados (producto inexistente)")
    
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    response = requests.get(
        f"{BASE_URL}/inventory/search-product",
        params={"q": "ProductoQueNoExiste123"},
        headers=headers
    )
    
    print_result(response)
    
    if response.status_code == 200:
        data = response.json()
        results = data.get('data', [])
        
        if len(results) == 0:
            print("\n✅ Test PASADO: Retorna lista vacía cuando no hay coincidencias")
        else:
            print(f"⚠️  Se esperaba 0 resultados, obtuvo {len(results)}")
    else:
        print("❌ Test FALLIDO")


def main():
    """Ejecuta todos los tests"""
    print("\n" + "="*70)
    print("  🧪 SUITE DE PRUEBAS - BÚSQUEDA POR PRODUCTO")
    print("="*70)
    print("\n📍 Endpoint: GET /api/v1/inventory/search-product")
    print("🎯 Funcionalidad: Buscar inventario por nombre, código o referencia")
    
    # Obtener token de autenticación
    token = get_auth_token()
    
    # Ejecutar tests
    test_search_without_auth()
    
    if token:
        test_search_without_query(token)
        test_search_short_query(token)
        test_search_by_name(token)
        test_search_by_code(token)
        test_search_by_reference(token)
        test_search_with_bodega_filter(token)
        test_search_case_insensitive(token)
        test_search_partial_match(token)
        test_search_no_results(token)
    else:
        print("\n⚠️  Tests con autenticación omitidos (no hay token)")
    
    # Resumen
    print_section("📊 RESUMEN DE PRUEBAS")
    print("\n✅ Suite de pruebas completada")
    print("\n💡 Para ejecutar el servicio:")
    print("   cd inventory-service && python run.py")
    print("\n💡 Para reiniciar la base de datos:")
    print("   cd inventory-service && python init_db.py")
    print("\n" + "="*70 + "\n")


if __name__ == '__main__':
    main()
