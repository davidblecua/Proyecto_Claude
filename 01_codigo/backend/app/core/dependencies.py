"""
Dependencias de FastAPI
Funciones reutilizables para inyección de dependencias
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.security import decode_token, validate_token_type
from app.db.database import get_db
from app.models.user import User, UserRole

# Esquema OAuth2 para autenticación con Bearer token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Obtiene el usuario actual desde el token JWT
    
    Args:
        token: Token JWT del header Authorization
        db: Sesión de base de datos
        
    Returns:
        User: Usuario autenticado
        
    Raises:
        HTTPException: Si el token es inválido o el usuario no existe
    """
    # Decodificar token
    payload = decode_token(token)
    validate_token_type(payload, "access")
    
    # Extraer user_id (se guarda como string en el token, convertir a int)
    sub = payload.get("sub")
    if sub is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo validar las credenciales",
        )
    user_id = int(sub)

    # Buscar usuario en base de datos
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
        )
    
    # Verificar que el usuario esté activo
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo",
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Verifica que el usuario actual esté activo
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    return current_user


def require_role(*allowed_roles: UserRole):
    """
    Decorator factory para requerir roles específicos
    
    Args:
        allowed_roles: Roles permitidos para acceder al endpoint
        
    Returns:
        Función de dependencia que valida el rol del usuario
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado. Se requiere uno de estos roles: {[r.value for r in allowed_roles]}"
            )
        return current_user
    
    return role_checker


# Dependencias específicas por rol
async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Requiere rol de administrador"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador"
        )
    return current_user


async def require_publisher(current_user: User = Depends(get_current_user)) -> User:
    """Requiere rol de publicador o administrador"""
    if current_user.role not in [UserRole.ADMIN, UserRole.PUBLISHER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de publicador"
        )
    return current_user