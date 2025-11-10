# Carga Masiva de Productos - Documentación

## Endpoint
`POST /api/v1/products/bulk-upload`

## Descripción
Permite cargar múltiples productos desde un archivo CSV de forma masiva.

## Autenticación
Requiere token JWT válido en el header Authorization.

## Request
- **Content-Type**: `multipart/form-data`
- **Campo requerido**: `csv_file` (archivo CSV)

## Estructura del CSV

### Columnas Obligatorias
| Columna | Tipo | Descripción | Ejemplo |
|---------|------|-------------|---------|
| `nombre` | string | Nombre del producto | "Paracetamol 500mg" |
| `codigo` | string | Código único (A-Z, 0-9, -) | "PAR-500-001" |
| `descripcion` | string | Descripción del producto | "Analgésico y antipirético" |
| `categoria_id` | integer | ID de categoría existente | 1 |
| `unidad_medida_id` | integer | ID de unidad de medida existente | 1 |
| `proveedor_id` | integer | ID de proveedor existente | 1 |

### Columnas Opcionales
| Columna | Tipo | Descripción | Ejemplo |
|---------|------|-------------|---------|
| `referencia` | string | Referencia del producto | "REF-PAR-500" |
| `precio_compra` | decimal | Precio de compra | 1000.00 |
| `precio_venta` | decimal | Precio de venta | 1500.00 |
| `requiere_ficha_tecnica` | boolean | Requiere ficha técnica | true/false |
| `requiere_condiciones_almacenamiento` | boolean | Requiere condiciones especiales | true/false |
| `requiere_certificaciones_sanitarias` | boolean | Requiere certificaciones | true/false |

## Ejemplo de CSV
```csv
nombre,codigo,descripcion,categoria_id,unidad_medida_id,proveedor_id,referencia,precio_compra,precio_venta,requiere_ficha_tecnica,requiere_condiciones_almacenamiento,requiere_certificaciones_sanitarias
"Paracetamol 500mg","PAR-500-001","Analgésico y antipirético",1,1,1,"REF-PAR-500",1000.00,1500.00,false,false,false
"Ibuprofeno 600mg","IBU-600-001","Antiinflamatorio",1,1,1,"REF-IBU-600",1200.00,1800.00,true,false,true
```

## Respuestas

### 201 - Éxito Total
Todos los productos fueron creados exitosamente.

```json
{
    "success": true,
    "message": "Todos los 5 productos fueron creados exitosamente",
    "data": {
        "success_count": 5,
        "error_count": 0,
        "errors": [],
        "created_products": [
            {
                "id": 123,
                "codigo": "PAR-500-001",
                "nombre": "Paracetamol 500mg"
            }
        ]
    }
}
```

### 207 - Éxito Parcial
Algunos productos creados, algunos con errores.

```json
{
    "success": true,
    "message": "Carga parcialmente exitosa: 3 creados, 2 errores",
    "data": {
        "success_count": 3,
        "error_count": 2,
        "errors": [
            "Fila 2: Ya existe un producto con código 'PAR-500-001'",
            "Fila 4: El campo categoria_id es obligatorio"
        ],
        "created_products": [...]
    }
}
```

### 400 - Error Total
Ningún producto pudo ser creado.

```json
{
    "success": false,
    "message": "No se pudo crear ningún producto. 5 errores encontrados",
    "data": {
        "success_count": 0,
        "error_count": 5,
        "errors": [
            "Fila 1: El código ya existe",
            "Fila 2: Categoría inválida"
        ],
        "created_products": []
    }
}
```

## Validaciones

### A Nivel de Archivo
- El archivo debe ser formato CSV
- Debe contener todas las columnas obligatorias
- No debe estar vacío

### A Nivel de Fila
- Todos los campos obligatorios deben tener valor
- Los códigos deben ser únicos
- Los IDs de categoría, unidad y proveedor deben existir
- Los precios deben ser números positivos
- Los códigos solo pueden tener letras mayúsculas, números y guiones

## Uso con cURL

```bash
curl -X POST "http://localhost:5000/api/v1/products/bulk-upload" \
  -H "Authorization: Bearer your-jwt-token" \
  -F "csv_file=@/path/to/products.csv"
```

## Notas Importantes

1. **Códigos únicos**: Si un código ya existe, esa fila fallará pero el procesamiento continuará
2. **Transacciones independientes**: Cada fila se procesa por separado
3. **Encoding**: El archivo debe estar en UTF-8 o Latin1
4. **Tamaño**: No hay límite específico pero se recomienda archivos de máximo 1000 filas
5. **Validación previa**: Asegúrate de que existan las categorías, unidades y proveedores referenciados