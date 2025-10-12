# 📖 Ejemplos de Uso - CRM Service API

## Tabla de Contenidos
- [cURL](#curl)
- [Python](#python)
- [JavaScript (Fetch)](#javascript-fetch)
- [JavaScript (Axios)](#javascript-axios)
- [Java](#java)
- [C#](#csharp)

---

## cURL

### Health Check
```bash
curl -X GET http://localhost:5000/health
```

### Crear Proveedor
```bash
curl -X POST http://localhost:5000/api/v1/suppliers \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "razon_social=Farmacéutica Colombia SA" \
  -F "nit=900123456-7" \
  -F "representante_legal=Carlos Rodríguez" \
  -F "pais=Colombia" \
  -F "nombre_contacto=Ana López" \
  -F "celular_contacto=3001234567" \
  -F "email=contacto@farmacol.com" \
  -F "ciudad=Bogotá" \
  -F "certificado=@/path/to/certificate.pdf"
```

### Listar Proveedores
```bash
curl -X GET "http://localhost:5000/api/v1/suppliers?page=1&per_page=10" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Obtener Proveedor por ID
```bash
curl -X GET http://localhost:5000/api/v1/suppliers/1 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Actualizar Proveedor
```bash
curl -X PUT http://localhost:5000/api/v1/suppliers/1 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "nombre_contacto=Nuevo Contacto" \
  -F "celular_contacto=3009876543"
```

### Eliminar Proveedor
```bash
curl -X DELETE http://localhost:5000/api/v1/suppliers/1 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## Python

### Usando requests

```python
import requests

BASE_URL = "http://localhost:5000/api/v1"
TOKEN = "YOUR_JWT_TOKEN"

headers = {
    "Authorization": f"Bearer {TOKEN}"
}

# Crear proveedor
def create_supplier():
    url = f"{BASE_URL}/suppliers"
    
    data = {
        "razon_social": "Farmacéutica Colombia SA",
        "nit": "900123456-7",
        "representante_legal": "Carlos Rodríguez",
        "pais": "Colombia",
        "nombre_contacto": "Ana López",
        "celular_contacto": "3001234567",
        "email": "contacto@farmacol.com",
        "ciudad": "Bogotá"
    }
    
    files = {
        "certificado": open("certificate.pdf", "rb")
    }
    
    response = requests.post(url, headers=headers, data=data, files=files)
    return response.json()

# Listar proveedores
def list_suppliers(page=1, per_page=10):
    url = f"{BASE_URL}/suppliers"
    params = {"page": page, "per_page": per_page}
    
    response = requests.get(url, headers=headers, params=params)
    return response.json()

# Obtener proveedor
def get_supplier(supplier_id):
    url = f"{BASE_URL}/suppliers/{supplier_id}"
    response = requests.get(url, headers=headers)
    return response.json()

# Buscar proveedores
def search_suppliers(search_term=None, pais=None):
    url = f"{BASE_URL}/suppliers"
    params = {}
    
    if search_term:
        params["search"] = search_term
    if pais:
        params["pais"] = pais
    
    response = requests.get(url, headers=headers, params=params)
    return response.json()

# Actualizar proveedor
def update_supplier(supplier_id, data):
    url = f"{BASE_URL}/suppliers/{supplier_id}"
    response = requests.put(url, headers=headers, data=data)
    return response.json()

# Eliminar proveedor
def delete_supplier(supplier_id):
    url = f"{BASE_URL}/suppliers/{supplier_id}"
    response = requests.delete(url, headers=headers)
    return response.json()

# Estadísticas
def get_stats():
    url = f"{BASE_URL}/suppliers/stats"
    response = requests.get(url, headers=headers)
    return response.json()

# Ejemplo de uso
if __name__ == "__main__":
    # Crear
    result = create_supplier()
    print("Proveedor creado:", result)
    
    # Listar
    suppliers = list_suppliers(page=1, per_page=10)
    print("Total proveedores:", suppliers["pagination"]["total"])
    
    # Buscar
    results = search_suppliers(pais="Colombia")
    print("Proveedores en Colombia:", len(results["data"]))
```

---

## JavaScript (Fetch)

```javascript
const BASE_URL = "http://localhost:5000/api/v1";
const TOKEN = "YOUR_JWT_TOKEN";

const headers = {
    "Authorization": `Bearer ${TOKEN}`
};

// Crear proveedor
async function createSupplier(supplierData, certificateFile) {
    const formData = new FormData();
    
    Object.keys(supplierData).forEach(key => {
        formData.append(key, supplierData[key]);
    });
    
    formData.append("certificado", certificateFile);
    
    const response = await fetch(`${BASE_URL}/suppliers`, {
        method: "POST",
        headers: headers,
        body: formData
    });
    
    return await response.json();
}

// Listar proveedores
async function listSuppliers(page = 1, perPage = 10) {
    const url = `${BASE_URL}/suppliers?page=${page}&per_page=${perPage}`;
    
    const response = await fetch(url, {
        method: "GET",
        headers: headers
    });
    
    return await response.json();
}

// Obtener proveedor
async function getSupplier(supplierId) {
    const response = await fetch(`${BASE_URL}/suppliers/${supplierId}`, {
        method: "GET",
        headers: headers
    });
    
    return await response.json();
}

// Buscar proveedores
async function searchSuppliers(filters) {
    const params = new URLSearchParams(filters);
    const url = `${BASE_URL}/suppliers?${params}`;
    
    const response = await fetch(url, {
        method: "GET",
        headers: headers
    });
    
    return await response.json();
}

// Actualizar proveedor
async function updateSupplier(supplierId, updateData) {
    const formData = new FormData();
    
    Object.keys(updateData).forEach(key => {
        formData.append(key, updateData[key]);
    });
    
    const response = await fetch(`${BASE_URL}/suppliers/${supplierId}`, {
        method: "PUT",
        headers: headers,
        body: formData
    });
    
    return await response.json();
}

// Eliminar proveedor
async function deleteSupplier(supplierId) {
    const response = await fetch(`${BASE_URL}/suppliers/${supplierId}`, {
        method: "DELETE",
        headers: headers
    });
    
    return await response.json();
}

// Ejemplo de uso
const supplierData = {
    razon_social: "Farmacéutica Colombia SA",
    nit: "900123456-7",
    representante_legal: "Carlos Rodríguez",
    pais: "Colombia",
    nombre_contacto: "Ana López",
    celular_contacto: "3001234567",
    email: "contacto@farmacol.com"
};

// Con file input de HTML
const fileInput = document.querySelector('input[type="file"]');
const certificateFile = fileInput.files[0];

createSupplier(supplierData, certificateFile)
    .then(result => console.log("Proveedor creado:", result))
    .catch(error => console.error("Error:", error));
```

---

## JavaScript (Axios)

```javascript
import axios from 'axios';

const BASE_URL = "http://localhost:5000/api/v1";
const TOKEN = "YOUR_JWT_TOKEN";

const api = axios.create({
    baseURL: BASE_URL,
    headers: {
        "Authorization": `Bearer ${TOKEN}`
    }
});

// Crear proveedor
async function createSupplier(supplierData, certificateFile) {
    const formData = new FormData();
    
    Object.keys(supplierData).forEach(key => {
        formData.append(key, supplierData[key]);
    });
    
    formData.append("certificado", certificateFile);
    
    try {
        const response = await api.post("/suppliers", formData, {
            headers: {
                "Content-Type": "multipart/form-data"
            }
        });
        return response.data;
    } catch (error) {
        console.error("Error:", error.response.data);
        throw error;
    }
}

// Listar proveedores
async function listSuppliers(page = 1, perPage = 10) {
    try {
        const response = await api.get("/suppliers", {
            params: { page, per_page: perPage }
        });
        return response.data;
    } catch (error) {
        console.error("Error:", error.response.data);
        throw error;
    }
}

// Buscar proveedores
async function searchSuppliers(filters) {
    try {
        const response = await api.get("/suppliers", {
            params: filters
        });
        return response.data;
    } catch (error) {
        console.error("Error:", error.response.data);
        throw error;
    }
}

// Ejemplo con React
function SupplierForm() {
    const [formData, setFormData] = React.useState({
        razon_social: "",
        nit: "",
        representante_legal: "",
        pais: "",
        nombre_contacto: "",
        celular_contacto: "",
        email: ""
    });
    
    const [certificate, setCertificate] = React.useState(null);
    
    const handleSubmit = async (e) => {
        e.preventDefault();
        
        try {
            const result = await createSupplier(formData, certificate);
            alert("Proveedor creado exitosamente!");
            console.log(result);
        } catch (error) {
            alert("Error al crear proveedor");
        }
    };
    
    return (
        <form onSubmit={handleSubmit}>
            {/* Form fields */}
            <input
                type="file"
                accept=".pdf,.jpg,.jpeg,.png,.txt"
                onChange={(e) => setCertificate(e.target.files[0])}
                required
            />
            <button type="submit">Registrar Proveedor</button>
        </form>
    );
}
```

---

## Java

```java
import java.io.*;
import java.net.http.*;
import java.nio.file.*;
import org.json.*;

public class SupplierClient {
    private static final String BASE_URL = "http://localhost:5000/api/v1";
    private static final String TOKEN = "YOUR_JWT_TOKEN";
    
    private HttpClient client;
    
    public SupplierClient() {
        this.client = HttpClient.newHttpClient();
    }
    
    // Listar proveedores
    public JSONObject listSuppliers(int page, int perPage) throws Exception {
        String url = String.format("%s/suppliers?page=%d&per_page=%d", 
                                   BASE_URL, page, perPage);
        
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(url))
            .header("Authorization", "Bearer " + TOKEN)
            .GET()
            .build();
        
        HttpResponse<String> response = client.send(request, 
                                          HttpResponse.BodyHandlers.ofString());
        
        return new JSONObject(response.body());
    }
    
    // Obtener proveedor
    public JSONObject getSupplier(int supplierId) throws Exception {
        String url = String.format("%s/suppliers/%d", BASE_URL, supplierId);
        
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(url))
            .header("Authorization", "Bearer " + TOKEN)
            .GET()
            .build();
        
        HttpResponse<String> response = client.send(request, 
                                          HttpResponse.BodyHandlers.ofString());
        
        return new JSONObject(response.body());
    }
    
    // Ejemplo de uso
    public static void main(String[] args) {
        try {
            SupplierClient client = new SupplierClient();
            
            // Listar proveedores
            JSONObject suppliers = client.listSuppliers(1, 10);
            System.out.println("Total: " + 
                suppliers.getJSONObject("pagination").getInt("total"));
            
            // Obtener un proveedor
            JSONObject supplier = client.getSupplier(1);
            System.out.println("Proveedor: " + 
                supplier.getJSONObject("data").getString("razon_social"));
            
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
```

---

## C#

```csharp
using System;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Threading.Tasks;
using Newtonsoft.Json;

public class SupplierClient
{
    private readonly HttpClient _client;
    private const string BaseUrl = "http://localhost:5000/api/v1";
    private const string Token = "YOUR_JWT_TOKEN";
    
    public SupplierClient()
    {
        _client = new HttpClient();
        _client.DefaultRequestHeaders.Authorization = 
            new AuthenticationHeaderValue("Bearer", Token);
    }
    
    // Listar proveedores
    public async Task<dynamic> ListSuppliersAsync(int page = 1, int perPage = 10)
    {
        var url = $"{BaseUrl}/suppliers?page={page}&per_page={perPage}";
        var response = await _client.GetAsync(url);
        
        response.EnsureSuccessStatusCode();
        
        var content = await response.Content.ReadAsStringAsync();
        return JsonConvert.DeserializeObject(content);
    }
    
    // Obtener proveedor
    public async Task<dynamic> GetSupplierAsync(int supplierId)
    {
        var url = $"{BaseUrl}/suppliers/{supplierId}";
        var response = await _client.GetAsync(url);
        
        response.EnsureSuccessStatusCode();
        
        var content = await response.Content.ReadAsStringAsync();
        return JsonConvert.DeserializeObject(content);
    }
    
    // Crear proveedor
    public async Task<dynamic> CreateSupplierAsync(
        SupplierData data, 
        byte[] certificateBytes, 
        string fileName)
    {
        using var content = new MultipartFormDataContent();
        
        content.Add(new StringContent(data.RazonSocial), "razon_social");
        content.Add(new StringContent(data.Nit), "nit");
        content.Add(new StringContent(data.RepresentanteLegal), "representante_legal");
        content.Add(new StringContent(data.Pais), "pais");
        content.Add(new StringContent(data.NombreContacto), "nombre_contacto");
        content.Add(new StringContent(data.CelularContacto), "celular_contacto");
        
        var fileContent = new ByteArrayContent(certificateBytes);
        fileContent.Headers.ContentType = MediaTypeHeaderValue.Parse("application/pdf");
        content.Add(fileContent, "certificado", fileName);
        
        var response = await _client.PostAsync($"{BaseUrl}/suppliers", content);
        response.EnsureSuccessStatusCode();
        
        var responseContent = await response.Content.ReadAsStringAsync();
        return JsonConvert.DeserializeObject(responseContent);
    }
    
    // Ejemplo de uso
    public static async Task Main(string[] args)
    {
        var client = new SupplierClient();
        
        try
        {
            // Listar
            var suppliers = await client.ListSuppliersAsync(1, 10);
            Console.WriteLine($"Total: {suppliers.pagination.total}");
            
            // Obtener uno
            var supplier = await client.GetSupplierAsync(1);
            Console.WriteLine($"Proveedor: {supplier.data.razon_social}");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error: {ex.Message}");
        }
    }
}

public class SupplierData
{
    public string RazonSocial { get; set; }
    public string Nit { get; set; }
    public string RepresentanteLegal { get; set; }
    public string Pais { get; set; }
    public string NombreContacto { get; set; }
    public string CelularContacto { get; set; }
    public string Email { get; set; }
}
```

---

## Respuestas de la API

### Respuesta Exitosa (Crear)
```json
{
    "success": true,
    "message": "Proveedor registrado exitosamente",
    "data": {
        "id": 1,
        "razon_social": "Farmacéutica Colombia SA",
        "nit": "900123456-7",
        "representante_legal": "Carlos Rodríguez",
        "pais": "Colombia",
        "nombre_contacto": "Ana López",
        "celular_contacto": "3001234567",
        "certificado_filename": "certificate.pdf",
        "email": "contacto@farmacol.com",
        "created_at": "2025-10-12T14:30:00",
        "created_by": "operador01"
    }
}
```

### Respuesta Exitosa (Lista con Paginación)
```json
{
    "success": true,
    "message": "Proveedores obtenidos exitosamente",
    "data": [
        {
            "id": 1,
            "razon_social": "Farmacéutica Colombia SA",
            "nit": "900123456-7",
            "pais": "Colombia",
            "nombre_contacto": "Ana López",
            "celular_contacto": "3001234567",
            "status": "active",
            "created_at": "2025-10-12T14:30:00"
        }
    ],
    "pagination": {
        "page": 1,
        "per_page": 10,
        "total": 12480,
        "total_pages": 1248,
        "has_next": true,
        "has_prev": false
    }
}
```

### Respuesta de Error
```json
{
    "success": false,
    "message": "Error de validación",
    "errors": {
        "nit": ["El NIT es obligatorio"],
        "celular_contacto": ["Formato de teléfono inválido"]
    }
}
```

---

**¡Usa estos ejemplos como referencia para integrar el CRM Service en tu aplicación! 🚀**
