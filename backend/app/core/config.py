"""
Configuración central de la aplicación
Maneja variables de entorno y configuración general
"""
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, validator


class Settings(BaseSettings):
    """
    Configuración de la aplicación usando Pydantic Settings
    Las variables se cargan desde .env o variables de entorno
    """
    
    # Información de la aplicación
    APP_NAME: str = "RentaMaq"
    APP_VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/api/v1"
    
    # Base de datos PostgreSQL
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_HOST: str
    DATABASE_PORT: str = "5432"
    DATABASE_NAME: str
    DATABASE_URL: Optional[PostgresDsn] = None
    
    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict) -> str:
        """Construye la URL de conexión a la base de datos"""
        if isinstance(v, str):
            return v
        return f"postgresql://{values.get('DATABASE_USER')}:{values.get('DATABASE_PASSWORD')}@{values.get('DATABASE_HOST')}:{values.get('DATABASE_PORT')}/{values.get('DATABASE_NAME')}"
    
    # Seguridad JWT
    SECRET_KEY: str  # Generar con: openssl rand -hex 32
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # AWS Configuración
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "eu-west-1"
    AWS_S3_BUCKET: Optional[str] = None
    
    # CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8000"]
    
    # Email (para futuras notificaciones)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    # Configuración de desarrollo
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Instancia global de configuración
settings = Settings()