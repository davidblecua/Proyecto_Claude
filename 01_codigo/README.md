# RentaMaq - Plataforma de Alquiler de Maquinaria de Obra

## 📋 Descripción
Plataforma web tipo Airbnb para el alquiler de maquinaria de construcción entre empresas y particulares.

## 🎯 Versión 0.1 - Características

### Roles de Usuario
- **Admin de Empresa**: Puede publicar máquinas y gestionar permisos
- **Consumidor**: Puede buscar y reservar máquinas
- **Publicador**: Puede publicar máquinas para alquilar

### Funcionalidades
- Sistema de autenticación JWT
- Búsqueda avanzada de maquinaria
- Gestión de publicaciones
- Sistema de reservas
- Panel de administración por roles

## 🛠️ Stack Tecnológico

- **Backend**: Python 3.11+ con FastAPI
- **Base de Datos**: PostgreSQL en AWS RDS
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Despliegue**: AWS (EC2 + RDS + S3)
- **Control de versiones**: Git
- **Editor**: VSCode

## 📁 Estructura del Proyecto

```
rentamaq-platform/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       └── endpoints/
│   │   │           ├── auth.py
│   │   │           ├── users.py
│   │   │           ├── machinery.py
│   │   │           └── bookings.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── dependencies.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── machinery.py
│   │   │   └── booking.py
│   │   ├── schemas/
│   │   │   ├── user.py
│   │   │   ├── machinery.py
│   │   │   └── booking.py
│   │   ├── services/
│   │   │   ├── user_service.py
│   │   │   ├── machinery_service.py
│   │   │   └── booking_service.py
│   │   ├── db/
│   │   │   ├── database.py
│   │   │   └── init_db.py
│   │   └── main.py
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   │   ├── main.css
│   │   │   └── components.css
│   │   ├── js/
│   │   │   ├── main.js
│   │   │   ├── auth.js
│   │   │   └── search.js
│   │   └── images/
│   └── templates/
│       ├── index.html
│       ├── login.html
│       ├── register.html
│       ├── dashboard.html
│       ├── machinery-list.html
│       └── machinery-detail.html
├── docs/
│   ├── INSTALLATION.md
│   ├── API_DOCUMENTATION.md
│   ├── DATABASE_SCHEMA.md
│   └── AWS_DEPLOYMENT.md
├── scripts/
│   ├── setup_db.py
│   └── deploy.sh
├── .github/
│   └── workflows/
│       └── ci.yml
├── .gitignore
├── README.md
└── docker-compose.yml
```

## 🚀 Instalación Rápida

### Prerrequisitos
- Python 3.11+
- PostgreSQL 14+
- Git
- VSCode
- Cuenta AWS

### Instalación Local

1. **Clonar el repositorio**
```bash
git clone <tu-repositorio>
cd rentamaq-platform
```

2. **Configurar entorno virtual**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env con tus credenciales
```

4. **Inicializar base de datos**
```bash
python -m app.db.init_db
```

5. **Ejecutar el servidor**
```bash
uvicorn app.main:app --reload
```

6. **Acceder a la aplicación**
- Frontend: http://localhost:8000
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📚 Documentación Adicional

- [Guía de Instalación Completa](docs/INSTALLATION.md)
- [Documentación de la API](docs/API_DOCUMENTATION.md)
- [Esquema de Base de Datos](docs/DATABASE_SCHEMA.md)
- [Despliegue en AWS](docs/AWS_DEPLOYMENT.md)

## 🔧 Desarrollo

### Estructura de Código
- Los **modelos** definen las tablas de la base de datos
- Los **schemas** validan y serializan datos JSON
- Los **servicios** contienen la lógica de negocio
- Los **endpoints** manejan las peticiones HTTP

### Convenciones de Código
- Seguir PEP 8
- Usar type hints
- Documentar funciones con docstrings
- Escribir tests para nuevas funcionalidades

## 🧪 Testing

```bash
cd backend
pytest tests/ -v
```

## 📦 Despliegue

Ver [AWS_DEPLOYMENT.md](docs/AWS_DEPLOYMENT.md) para instrucciones detalladas.

## 🤝 Contribuir

1. Hacer fork del proyecto
2. Crear una rama feature (`git checkout -b feature/NuevaCaracteristica`)
3. Commit cambios (`git commit -m 'Agregar nueva característica'`)
4. Push a la rama (`git push origin feature/NuevaCaracteristica`)
5. Abrir Pull Request

## 📝 Licencia

Este proyecto es privado y propietario.

## 👥 Autores

- Tu Nombre - Desarrollo inicial

## 📞 Soporte

Para soporte, contactar a: tu-email@ejemplo.com