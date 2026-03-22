# Documentación de la API - RentaMaq v0.1

Esta documentación detalla todos los endpoints disponibles en la API REST de RentaMaq.

## URL Base

```
Desarrollo: http://localhost:8000/api/v1
Producción: https://tu-dominio.com/api/v1
```

## Autenticación

La API utiliza **JWT (JSON Web Tokens)** para autenticación.

### Obtener Token

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "usuario@ejemplo.com",
  "password": "Password123!"
}
```

**Respuesta:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "usuario@ejemplo.com",
    "username": "usuario",
    "full_name": "Usuario Ejemplo",
    "role": "consumer",
    "is_active": true
  }
}
```

### Usar Token en Peticiones

Incluir el token en el header `Authorization`:

```http
GET /api/v1/machinery/search
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

## Endpoints de Autenticación

### POST /auth/register
Registra un nuevo usuario.

**Body:**
```json
{
  "email": "nuevo@ejemplo.com",
  "username": "nuevo_usuario",
  "password": "Password123!",
  "full_name": "Nombre Completo",
  "role": "consumer",
  "phone": "+34 600000000",
  "company_name": "Mi Empresa S.L."
}
```

**Roles disponibles:** `consumer`, `publisher`, `admin`

**Respuesta:** `201 Created`
```json
{
  "id": 1,
  "email": "nuevo@ejemplo.com",
  "username": "nuevo_usuario",
  "role": "consumer",
  "is_active": true,
  "created_at": "2024-03-15T10:00:00Z"
}
```

### POST /auth/login
Inicia sesión y obtiene tokens.

### POST /auth/refresh
Renueva el access token usando el refresh token.

**Body:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### GET /auth/me
Obtiene información del usuario actual.

**Headers:** `Authorization: Bearer <token>`

## Endpoints de Maquinaria

### GET /machinery/search
Busca maquinaria con filtros avanzados.

**Query Parameters:**
- `machinery_type` (opcional): Tipo de máquina
- `location_city` (opcional): Ciudad
- `location_province` (opcional): Provincia  
- `min_price` (opcional): Precio mínimo/día
- `max_price` (opcional): Precio máximo/día
- `search_text` (opcional): Búsqueda en texto
- `skip` (default: 0): Paginación
- `limit` (default: 20): Resultados por página
- `sort_by` (default: created_at): Campo de ordenamiento
- `sort_order` (default: desc): asc o desc

**Ejemplo:**
```http
GET /machinery/search?location_city=Madrid&max_price=300&limit=10
```

**Respuesta:**
```json
{
  "total": 45,
  "machinery": [
    {
      "id": 1,
      "title": "Excavadora Caterpillar 320D",
      "description": "Excavadora hidráulica...",
      "machinery_type": "excavadora",
      "brand": "Caterpillar",
      "model": "320D",
      "daily_rate": 250.0,
      "location_city": "Madrid",
      "location_province": "Madrid",
      "is_available": true,
      "owner_id": 2
    }
  ],
  "page": 1,
  "page_size": 10,
  "total_pages": 5
}
```

### GET /machinery/{machinery_id}
Obtiene detalles de una máquina específica.

### POST /machinery
Crea nueva maquinaria (requiere rol `publisher` o `admin`).

**Headers:** `Authorization: Bearer <token>`

**Body:**
```json
{
  "title": "Excavadora Caterpillar 320D",
  "description": "Excavadora hidráulica en excelente estado...",
  "machinery_type": "excavadora",
  "brand": "Caterpillar",
  "model": "320D",
  "year": 2020,
  "condition": "excelente",
  "daily_rate": 250.0,
  "weekly_rate": 1400.0,
  "monthly_rate": 5000.0,
  "deposit": 2000.0,
  "location_city": "Madrid",
  "location_province": "Madrid",
  "delivery_available": true,
  "delivery_cost": 150.0
}
```

### PUT /machinery/{machinery_id}
Actualiza maquinaria existente (solo propietario).

### DELETE /machinery/{machinery_id}
Elimina maquinaria (soft delete, solo propietario).

### PATCH /machinery/{machinery_id}/availability
Cambia la disponibilidad de la máquina.

**Query Parameter:**
- `is_available`: true o false

## Endpoints de Reservas

### GET /bookings/my-bookings
Obtiene las reservas del usuario actual.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `skip` (default: 0)
- `limit` (default: 20)
- `status` (opcional): Filtrar por estado

**Respuesta:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "machinery_id": 5,
    "start_date": "2024-04-01T09:00:00Z",
    "end_date": "2024-04-07T18:00:00Z",
    "daily_rate": 250.0,
    "total_days": 6,
    "subtotal": 1500.0,
    "total_cost": 1650.0,
    "status": "confirmed",
    "created_at": "2024-03-15T10:00:00Z"
  }
]
```

### POST /bookings
Crea una nueva reserva.

**Headers:** `Authorization: Bearer <token>`

**Body:**
```json
{
  "machinery_id": 5,
  "start_date": "2024-04-01T09:00:00",
  "end_date": "2024-04-07T18:00:00",
  "notes": "Necesito la máquina para excavación",
  "needs_delivery": true,
  "delivery_address": "Calle Principal 123",
  "delivery_city": "Madrid",
  "delivery_province": "Madrid"
}
```

**Validaciones automáticas:**
- Verifica disponibilidad de la máquina
- Calcula costes totales
- Valida fechas

### GET /bookings/{booking_id}
Obtiene detalles de una reserva.

### PATCH /bookings/{booking_id}/status
Actualiza el estado de una reserva (solo propietario o admin).

**Body:**
```json
{
  "status": "confirmed",
  "admin_notes": "Confirmado, entrega programada"
}
```

**Estados disponibles:**
- `pending`: Pendiente
- `confirmed`: Confirmada
- `in_progress`: En curso
- `completed`: Completada
- `cancelled`: Cancelada

### POST /bookings/{booking_id}/cancel
Cancela una reserva (solo el usuario que la creó).

**Body:**
```json
{
  "cancellation_reason": "Cambio de planes en el proyecto"
}
```

### GET /bookings/machinery/{machinery_id}/check-availability
Verifica disponibilidad de una máquina en fechas específicas.

**Query Parameters:**
- `start_date`: Fecha inicio (ISO format)
- `end_date`: Fecha fin (ISO format)

**Respuesta:**
```json
{
  "machinery_id": 5,
  "start_date": "2024-04-01T09:00:00",
  "end_date": "2024-04-07T18:00:00",
  "is_available": true
}
```

## Endpoints de Usuarios

### GET /users/me
Obtiene el perfil del usuario actual.

### PUT /users/me
Actualiza el perfil del usuario actual.

**Body:**
```json
{
  "full_name": "Nombre Actualizado",
  "phone": "+34 600111222",
  "company_name": "Nueva Empresa S.L."
}
```

### POST /users/me/change-password
Cambia la contraseña del usuario.

**Body:**
```json
{
  "current_password": "PasswordViejo123!",
  "new_password": "PasswordNuevo123!"
}
```

### GET /users (Solo Admin)
Lista todos los usuarios.

### PUT /users/{user_id}/role (Solo Admin)
Actualiza el rol de un usuario.

## Códigos de Estado HTTP

- `200 OK`: Petición exitosa
- `201 Created`: Recurso creado exitosamente
- `400 Bad Request`: Datos inválidos
- `401 Unauthorized`: No autenticado o token inválido
- `403 Forbidden`: Sin permisos suficientes
- `404 Not Found`: Recurso no encontrado
- `409 Conflict`: Conflicto (ej: fechas ocupadas)
- `422 Unprocessable Entity`: Error de validación
- `500 Internal Server Error`: Error del servidor

## Formatos de Respuesta de Error

```json
{
  "detail": "Descripción del error"
}
```

**Ejemplo de error de validación:**
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

## Tipos de Maquinaria Disponibles

- `excavadora`: Excavadora
- `retroexcavadora`: Retroexcavadora
- `dumper`: Dumper
- `pala_cargadora`: Pala Cargadora
- `hormigonera`: Hormigonera
- `camion_grua`: Camión Grúa
- `grua_torre`: Grúa Torre
- `manipulador_telescopico`: Manipulador Telescópico
- `plataforma_elevadora`: Plataforma Elevadora
- `carretilla_elevadora`: Carretilla Elevadora
- `compactadora`: Compactadora
- `bulldozer`: Bulldozer
- `martillo_hidraulico`: Martillo Hidráulico
- `generador`: Generador Eléctrico
- `compresor`: Compresor

## Documentación Interactiva

La API incluye documentación interactiva automática:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Puedes probar todos los endpoints directamente desde Swagger UI.

## Rate Limiting

Actualmente no hay límite de peticiones en desarrollo.
En producción se recomienda implementar rate limiting.

## Versionado

La API usa versionado en la URL: `/api/v1/`

Futuras versiones serán: `/api/v2/`, etc.

## Soporte

Para más información, consulta:
- README.md
- INSTALLATION.md
- DATABASE_SCHEMA.md