"""
Módulo de seguridad
Maneja autenticación JWT y hashing de contraseñas
"""
from datetime import datetime, timedelta
from typing import Optional, Union
import bcrypt
from jose import JWTError, jwt
from fastapi import HTTPException, status
from app.core.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un token JWT de acceso
    
    Args:
        data: Datos a incluir en el token (típicamente user_id, role)
        expires_delta: Tiempo de expiración personalizado
        
    Returns:
        str: Token JWT codificado
    """
    to_encode = data.copy()
    # jose exige que 'sub' sea string (RFC 7519 §4.1.2)
    if "sub" in to_encode:
        to_encode["sub"] = str(to_encode["sub"])

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    Crea un token JWT de refresco (duración más larga)
    
    Args:
        data: Datos a incluir en el token
        
    Returns:
        str: Token JWT de refresco
    """
    to_encode = data.copy()
    if "sub" in to_encode:
        to_encode["sub"] = str(to_encode["sub"])
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    """
    Decodifica y valida un token JWT
    
    Args:
        token: Token JWT a decodificar
        
    Returns:
        dict: Payload del token
        
    Raises:
        HTTPException: Si el token es inválido o ha expirado
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo validar las credenciales",
            headers={"WWW-Authenticate": "Bearer"},
        )


def validate_token_type(payload: dict, expected_type: str) -> None:
    """
    Valida que el tipo de token sea el esperado
    
    Args:
        payload: Payload del token decodificado
        expected_type: Tipo esperado ("access" o "refresh")
        
    Raises:
        HTTPException: Si el tipo no coincide
    """
    token_type = payload.get("type")
    if token_type != expected_type:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Tipo de token inválido. Se esperaba: {expected_type}",
        )