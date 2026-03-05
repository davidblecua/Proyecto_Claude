# 📂 ÍNDICE DE ARCHIVOS - RENTAMAQ PLATFORM

## 🎯 DOCUMENTACIÓN PRINCIPAL

### Documentos de Lectura Obligatoria
1. **GUIA_COMPLETA.md** - ⭐ EMPEZAR AQUÍ - Guía maestra con todos los pasos
2. **README.md** - Visión general del proyecto
3. **docs/INSTALLATION.md** - Guía detallada de instalación
4. **docs/API_DOCUMENTATION.md** - Documentación completa de la API
5. **docs/GIT_GUIDE.md** - Guía de uso de Git

---

## 🔧 BACKEND (Python + FastAPI)

### Configuración
- **backend/requirements.txt** - Dependencias de Python
- **backend/.env.example** - Variables de entorno (copiar a .env)
- **backend/app/core/config.py** - Configuración de la aplicación
- **backend/app/core/security.py** - Seguridad JWT y passwords
- **backend/app/core/dependencies.py** - Dependencias de FastAPI

### Base de Datos
- **backend/app/db/database.py** - Configuración SQLAlchemy
- **backend/app/db/init_db.py** - Script de inicialización
- **backend/app/models/user.py** - Modelo de Usuario
- **backend/app/models/machinery.py** - Modelo de Maquinaria
- **backend/app/models/booking.py** - Modelo de Reservas

### Validación (Schemas Pydantic)
- **backend/app/schemas/user.py** - Validación de usuarios
- **backend/app/schemas/machinery.py** - Validación de maquinaria
- **backend/app/schemas/booking.py** - Validación de reservas

### Servicios (Lógica de Negocio)
- **backend/app/services/user_service.py** - Lógica de usuarios
- **backend/app/services/machinery_service.py** - Lógica de maquinaria
- **backend/app/services/booking_service.py** - Lógica de reservas

### API Endpoints
- **backend/app/api/v1/endpoints/auth.py** - Login, registro, tokens
- **backend/app/api/v1/endpoints/users.py** - Gestión de usuarios
- **backend/app/api/v1/endpoints/machinery.py** - CRUD de maquinaria
- **backend/app/api/v1/endpoints/bookings.py** - Gestión de reservas

### Aplicación Principal
- **backend/app/main.py** - ⭐ Aplicación FastAPI principal

---

## 🎨 FRONTEND (HTML/CSS/JS)

### Estilos
- **frontend/static/css/main.css** - Estilos principales CSS

### JavaScript
- **frontend/static/js/main.js** - ⭐ JavaScript principal
- **frontend/static/js/auth.js** - Autenticación frontend
- **frontend/static/js/search.js** - Búsqueda y reservas

### HTML
- **frontend/templates/index.html** - ⭐ Página principal

---

## 🔑 ARCHIVOS DE CONFIGURACIÓN

### Git
- **.gitignore** - Archivos ignorados por Git

---

## 📋 CANTIDAD DE ARCHIVOS POR TIPO

### Backend Python
- **30 archivos Python** (.py)
- **8 archivos __init__.py** (módulos)
- **22 archivos de código** funcional

### Frontend
- **1 archivo HTML**
- **1 archivo CSS**
- **3 archivos JavaScript**

### Documentación
- **5 archivos Markdown** (.md)

### Configuración
- **3 archivos** (requirements.txt, .env.example, .gitignore)

**TOTAL: ~42 archivos de código + documentación**

---

## 🚀 ORDEN RECOMENDADO DE LECTURA

Para entender el proyecto completamente:

1. **GUIA_COMPLETA.md** - Vista general
2. **README.md** - Contexto del proyecto
3. **docs/INSTALLATION.md** - Cómo instalarlo
4. **backend/app/main.py** - Punto de entrada
5. **backend/app/models/user.py** - Entender modelos
6. **backend/app/services/user_service.py** - Lógica de negocio
7. **backend/app/api/v1/endpoints/auth.py** - API endpoints
8. **frontend/templates/index.html** - Frontend
9. **frontend/static/js/main.js** - JavaScript
10. **docs/API_DOCUMENTATION.md** - Referencia API

---

## 📊 LÍNEAS DE CÓDIGO APROXIMADAS

- **Backend Python**: ~3,500 líneas
- **Frontend (HTML/CSS/JS)**: ~1,500 líneas
- **Documentación**: ~2,000 líneas
- **TOTAL**: ~7,000 líneas de código y documentación

---

## 🎯 ARCHIVOS MÁS IMPORTANTES

### Top 10 - Por Importancia
1. **backend/app/main.py** - Corazón de la aplicación
2. **backend/app/models/** - Define estructura de datos
3. **backend/app/services/** - Toda la lógica de negocio
4. **backend/app/api/v1/endpoints/** - API REST
5. **frontend/static/js/main.js** - Funcionalidad frontend
6. **backend/app/core/config.py** - Configuración
7. **backend/app/core/security.py** - Seguridad
8. **backend/app/db/init_db.py** - Inicialización
9. **docs/API_DOCUMENTATION.md** - Referencia
10. **GUIA_COMPLETA.md** - Documentación maestra

---

## 📁 ARCHIVOS POR FUNCIONALIDAD

### Autenticación
- backend/app/core/security.py
- backend/app/api/v1/endpoints/auth.py
- backend/app/services/user_service.py
- frontend/static/js/auth.js

### Búsqueda de Maquinaria
- backend/app/services/machinery_service.py
- backend/app/api/v1/endpoints/machinery.py
- frontend/static/js/search.js

### Sistema de Reservas
- backend/app/services/booking_service.py
- backend/app/api/v1/endpoints/bookings.py
- frontend/static/js/search.js

### Base de Datos
- backend/app/db/database.py
- backend/app/db/init_db.py
- backend/app/models/*.py

---

## 🔍 CÓMO ENCONTRAR CÓDIGO ESPECÍFICO

### "¿Dónde está el código de...?"

**Login/Autenticación:**
- Backend: `backend/app/api/v1/endpoints/auth.py`
- Frontend: `frontend/static/js/auth.js`

**Búsqueda de máquinas:**
- Backend: `backend/app/services/machinery_service.py` → método `search_machinery`
- Frontend: `frontend/static/js/search.js` → función `searchMachinery`

**Crear reserva:**
- Backend: `backend/app/services/booking_service.py` → método `create_booking`
- Frontend: `frontend/static/js/search.js` → función `initiateBooking`

**Validación de datos:**
- `backend/app/schemas/*.py` - Todos los schemas Pydantic

**Configuración de base de datos:**
- `backend/app/core/config.py` - Variables de entorno
- `backend/app/db/database.py` - Conexión SQLAlchemy

**Estilos visuales:**
- `frontend/static/css/main.css` - Todo el CSS

---

## 💾 DESCARGAR TODO EL PROYECTO

Hay dos formas de obtener todos los archivos:

### Opción 1: Archivo ZIP
- **rentamaq-platform.zip** - Contiene todo el proyecto listo para descomprimir

### Opción 2: Carpeta Individual
- **rentamaq-platform/** - Carpeta con toda la estructura

---

## 🛠️ ARCHIVOS PARA EDITAR PRIMERO

Si vas a personalizar la plataforma, estos son los primeros archivos a modificar:

1. **backend/.env** - Tus credenciales y configuración
2. **frontend/static/css/main.css** - Colores y estilos (variables CSS al inicio)
3. **backend/app/core/config.py** - Nombre de la app, configuración general
4. **frontend/templates/index.html** - Logo y textos de la página
5. **backend/app/models/machinery.py** - Agregar/quitar tipos de maquinaria

---

## ✅ CHECKLIST DE ARCHIVOS NECESARIOS

Antes de empezar, verifica que tienes:

- [x] Todos los archivos .py del backend
- [x] requirements.txt
- [x] Archivos HTML/CSS/JS del frontend
- [x] Documentación (README, docs/)
- [x] .env.example (para crear tu .env)
- [x] .gitignore
- [x] GUIA_COMPLETA.md

Si falta alguno, descarga de nuevo el ZIP completo.

---

## 📞 AYUDA RÁPIDA

**¿Qué archivo modifico para...?**

- Cambiar colores: `frontend/static/css/main.css` (líneas 1-20)
- Agregar endpoint: `backend/app/api/v1/endpoints/`
- Modificar validación: `backend/app/schemas/`
- Cambiar lógica de negocio: `backend/app/services/`
- Agregar tabla a BD: `backend/app/models/`

**¿Dónde veo ejemplos de uso?**

- `docs/API_DOCUMENTATION.md` - Ejemplos de cada endpoint
- `backend/app/db/init_db.py` - Datos de muestra
- `frontend/static/js/` - Ejemplos de llamadas a API

---

## 🎓 PARA APRENDER

Si quieres entender cómo funciona todo, lee en este orden:

1. Modelos (backend/app/models/) - ¿Qué datos guardamos?
2. Schemas (backend/app/schemas/) - ¿Cómo validamos datos?
3. Servicios (backend/app/services/) - ¿Qué hace la aplicación?
4. Endpoints (backend/app/api/v1/endpoints/) - ¿Cómo se expone la API?
5. Frontend (frontend/) - ¿Cómo interactúa el usuario?

---

¡Todo el proyecto está aquí y documentado! 🚀
