"""
Configuración de base de datos
Gestiona la conexión a PostgreSQL usando SQLAlchemy
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Crear engine de SQLAlchemy
# pool_pre_ping verifica la conexión antes de usarla
engine = create_engine(
    str(settings.DATABASE_URL),
    pool_pre_ping=True,
    echo=settings.DEBUG  # Muestra las queries SQL en modo debug
)

# SessionLocal es la clase que usaremos para crear sesiones de BD
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base es la clase base para todos los modelos ORM
Base = declarative_base()


def get_db():
    """
    Dependencia de FastAPI para obtener sesión de base de datos
    
    Yields:
        Session: Sesión de SQLAlchemy
        
    Example:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()