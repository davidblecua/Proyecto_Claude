"""
Aplicación Principal FastAPI - RentaMaq
Plataforma de alquiler de maquinaria de construcción
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from pathlib import Path
from app.core.config import settings
from app.api.v1.endpoints import auth, users, machinery, bookings, dashboard
from app.db.database import engine, Base

# Crear tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Crear aplicación FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Plataforma de alquiler de maquinaria de construcción tipo Airbnb",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Handler global: convierte errores de validación en JSON legible
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"] if loc != "body")
        errors.append(f"{field}: {error['msg']}" if field else error["msg"])
    return JSONResponse(
        status_code=422,
        content={"detail": "; ".join(errors)}
    )

# Handler global: captura errores 500 inesperados y devuelve JSON
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Error interno del servidor: {type(exc).__name__}: {str(exc)}"}
    )

# Montar archivos estáticos (CSS, JS, imágenes)
static_path = Path(__file__).parent.parent.parent / "frontend" / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Incluir routers de la API v1
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(users.router, prefix=settings.API_V1_PREFIX)
app.include_router(machinery.router, prefix=settings.API_V1_PREFIX)
app.include_router(bookings.router, prefix=settings.API_V1_PREFIX)
app.include_router(dashboard.router, prefix=settings.API_V1_PREFIX)


@app.get("/", response_class=HTMLResponse)
async def root():
    """
    Página principal - Redirige al frontend
    """
    html_path = Path(__file__).parent.parent.parent / "frontend" / "templates" / "index.html"
    
    if html_path.exists():
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    
    return """
    <html>
        <head>
            <title>RentaMaq - Plataforma de Alquiler de Maquinaria</title>
        </head>
        <body style="font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px;">
            <h1>🏗️ RentaMaq - Plataforma de Alquiler de Maquinaria</h1>
            <p>Bienvenido a la API de RentaMaq</p>
            <h2>Documentación:</h2>
            <ul>
                <li><a href="/docs">Swagger UI - Documentación Interactiva</a></li>
                <li><a href="/redoc">ReDoc - Documentación Alternativa</a></li>
            </ul>
            <h2>Endpoints principales:</h2>
            <ul>
                <li><strong>POST /api/v1/auth/register</strong> - Registrar usuario</li>
                <li><strong>POST /api/v1/auth/login</strong> - Iniciar sesión</li>
                <li><strong>GET /api/v1/machinery/search</strong> - Buscar maquinaria</li>
                <li><strong>POST /api/v1/machinery</strong> - Publicar maquinaria</li>
                <li><strong>POST /api/v1/bookings</strong> - Crear reserva</li>
            </ul>
        </body>
    </html>
    """


@app.get("/health")
async def health_check():
    """
    Endpoint de health check para monitoreo
    """
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


@app.get("/api/v1/info")
async def api_info():
    """
    Información de la API
    """
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "api_prefix": settings.API_V1_PREFIX,
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc"
        },
        "endpoints": {
            "auth": f"{settings.API_V1_PREFIX}/auth",
            "users": f"{settings.API_V1_PREFIX}/users",
            "machinery": f"{settings.API_V1_PREFIX}/machinery",
            "bookings": f"{settings.API_V1_PREFIX}/bookings"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )