# Guía de Instalación - RentaMaq

Esta guía te ayudará a instalar y configurar la plataforma RentaMaq en tu entorno local y en AWS.

## Tabla de Contenidos
1. [Requisitos Previos](#requisitos-previos)
2. [Instalación Local](#instalación-local)
3. [Configuración de Base de Datos](#configuración-de-base-de-datos)
4. [Configuración de Variables de Entorno](#configuración-de-variables-de-entorno)
5. [Iniciar la Aplicación](#iniciar-la-aplicación)
6. [Verificación](#verificación)
7. [Solución de Problemas](#solución-de-problemas)

## Requisitos Previos

### Software Necesario
- **Python**: 3.11 o superior
- **PostgreSQL**: 14 o superior
- **Git**: Para control de versiones
- **VSCode**: Editor recomendado
- **pip**: Gestor de paquetes de Python
- **Cuenta AWS**: Para despliegue en producción

### Verificar Instalaciones

```bash
# Verificar Python
python --version  # Debe ser 3.11+

# Verificar PostgreSQL
psql --version

# Verificar Git
git --version

# Verificar pip
pip --version
```

## Instalación Local

### 1. Clonar el Repositorio

```bash
# Clonar el repositorio
git clone <URL-DE-TU-REPOSITORIO>
cd rentamaq-platform
```

### 2. Configurar Entorno Virtual de Python

```bash
# Navegar al directorio backend
cd backend

# Crear entorno virtual
python -m venv venv

# Activar el entorno virtual
# En Linux/Mac:
source venv/bin/activate

# En Windows:
venv\Scripts\activate

# Deberías ver (venv) en tu terminal
```

### 3. Instalar Dependencias de Python

```bash
# Asegúrate de estar en el directorio backend con el venv activado
pip install --upgrade pip
pip install -r requirements.txt

# Esto instalará todas las dependencias necesarias:
# - FastAPI
# - SQLAlchemy
# - PostgreSQL driver
# - JWT authentication
# - AWS SDK
# - etc.
```

## Configuración de Base de Datos

### 1. Instalar PostgreSQL

**En Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**En macOS:**
```bash
brew install postgresql@14
brew services start postgresql@14
```

**En Windows:**
- Descargar desde: https://www.postgresql.org/download/windows/
- Ejecutar el instalador
- Configurar contraseña para usuario postgres

### 2. Crear Base de Datos

```bash
# Conectar a PostgreSQL
sudo -u postgres psql

# O en Windows:
psql -U postgres
```

```sql
-- Crear usuario
CREATE USER rentamaq_user WITH PASSWORD 'rentamaq_use_v1_735';# tu_password_seguro

-- Crear base de datos
CREATE DATABASE rentamaq_db;

-- Dar permisos al usuario
GRANT ALL PRIVILEGES ON DATABASE rentamaq_db TO rentamaq_user;

-- Salir
\q
```

### 3. Verificar Conexión

```bash
# Conectar con el nuevo usuario
psql -U rentamaq_user -d rentamaq_db -h localhost

# Si te conectas correctamente, la configuración es correcta
\q
```

## Configuración de Variables de Entorno

### 1. Copiar Archivo de Ejemplo

```bash
# Desde el directorio backend
cp .env.example .env
```

### 2. Editar Archivo .env

Abre el archivo `.env` con tu editor favorito y configura las variables:

```bash
# Configuración de Base de Datos
DATABASE_USER=rentamaq_user
DATABASE_PASSWORD=rentamaq_use_v1_735#tu_password_seguro_aqui
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=rentamaq_db

# Seguridad - Generar clave secreta
# Ejecuta: openssl rand -hex 32
SECRET_KEY=tu_clave_secreta_super_segura_generada_con_openssl
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# AWS (dejar vacío para desarrollo local)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=eu-west-1
AWS_S3_BUCKET=

# Desarrollo
DEBUG=True
```

### 3. Generar Secret Key

```bash
# En Linux/Mac:
openssl rand -hex 32

# Copia el resultado y pégalo en SECRET_KEY en tu archivo .env
```

## Iniciar la Aplicación

### 1. Inicializar Base de Datos

```bash
# Asegúrate de estar en el directorio backend con venv activado
python -m app.db.init_db

# Cuando te pregunte si deseas crear datos de muestra, escribe 's'
# Esto creará usuarios de prueba y maquinaria de ejemplo
```

### 2. Iniciar el Servidor de Desarrollo

```bash
# Método 1: Con uvicorn directamente
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Método 2: Con Python
python -m app.main

# El servidor se iniciará en: http://localhost:8000
```

### 3. Acceder a la Aplicación

Abre tu navegador y visita:

- **Frontend**: http://localhost:8000
- **Documentación API (Swagger)**: http://localhost:8000/docs
- **Documentación API (ReDoc)**: http://localhost:8000/redoc

## Verificación

### 1. Verificar que la API Funciona

```bash
# Prueba el endpoint de health check
curl http://localhost:8000/health

# Respuesta esperada:
# {"status":"healthy","app_name":"RentaMaq","version":"0.1.0"}
```

### 2. Verificar Frontend

1. Visita http://localhost:8000
2. Deberías ver la página principal con el buscador
3. Intenta buscar maquinaria

### 3. Probar Login con Datos de Muestra

Si creaste datos de muestra, puedes probar con estas credenciales:

- **Administrador**:
  - Email: admin@rentamaq.com
  - Contraseña: Admin123!

- **Publicador**:
  - Email: empresa@construcciones.com
  - Contraseña: Publisher123!

- **Consumidor**:
  - Email: cliente@ejemplo.com
  - Contraseña: Consumer123!

## Solución de Problemas

### Error: "No se puede conectar a la base de datos"

**Solución:**
```bash
# Verificar que PostgreSQL está corriendo
sudo systemctl status postgresql

# Verificar credenciales en .env
cat .env | grep DATABASE

# Verificar que la base de datos existe
psql -U postgres -c "\l"
```

### Error: "ModuleNotFoundError"

**Solución:**
```bash
# Asegúrate de que el entorno virtual está activado
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Reinstala las dependencias
pip install -r requirements.txt
```

### Error: "Puerto 8000 ya en uso"

**Solución:**
```bash
# Encontrar proceso usando el puerto
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Matar el proceso o usar otro puerto
uvicorn app.main:app --reload --port 8001
```

### Error: "SECRET_KEY not set"

**Solución:**
```bash
# Genera una nueva clave
openssl rand -hex 32

# Agrégala al archivo .env
echo "SECRET_KEY=tu_nueva_clave_aqui" >> .env
```

### La aplicación no carga los archivos estáticos

**Solución:**
```bash
# Verificar que la estructura de directorios es correcta
ls -R frontend/

# Debe existir:
# frontend/static/css/
# frontend/static/js/
# frontend/templates/
```

## Próximos Pasos

Una vez que la instalación local funciona correctamente:

1. Lee la [Documentación de la API](API_DOCUMENTATION.md)
2. Revisa el [Esquema de Base de Datos](DATABASE_SCHEMA.md)
3. Para despliegue en producción, consulta [Despliegue en AWS](AWS_DEPLOYMENT.md)

## Comandos Útiles de Desarrollo

```bash
# Activar entorno virtual
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Desactivar entorno virtual
deactivate

# Actualizar dependencias
pip install --upgrade -r requirements.txt

# Crear nueva migración de base de datos (si usas Alembic)
alembic revision --autogenerate -m "descripción del cambio"

# Aplicar migraciones
alembic upgrade head

# Ver logs en tiempo real
uvicorn app.main:app --reload --log-level debug

# Ejecutar tests
pytest tests/ -v

# Ver cobertura de tests
pytest --cov=app tests/
```

## Soporte

Si encuentras problemas durante la instalación:

1. Revisa los logs del servidor
2. Verifica que todas las dependencias están instaladas
3. Consulta la documentación adicional
4. Crea un issue en el repositorio

¡Listo! Tu instalación de RentaMaq debería estar funcionando correctamente.