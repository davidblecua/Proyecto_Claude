"""
Endpoints de Autenticación
Login, registro y gestión de tokens
"""
import secrets
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from authlib.integrations.httpx_client import AsyncOAuth2Client
from app.db.database import get_db
from app.schemas.user import UserCreate, UserLogin, Token, TokenRefresh, UserResponse
from app.services.user_service import UserService
from app.core.security import create_access_token, create_refresh_token, decode_token, validate_token_type
from app.core.dependencies import get_current_user
from app.core.config import settings
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Registra un nuevo usuario en la plataforma
    
    - **email**: Email único del usuario
    - **username**: Nombre de usuario único
    - **password**: Contraseña (mínimo 8 caracteres, con número y mayúscula)
    - **role**: Rol del usuario (consumer, publisher, admin)
    """
    new_user = UserService.create_user(db, user_data)
    return new_user


@router.post("/login", response_model=Token)
def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Autentica un usuario y devuelve tokens de acceso
    
    - **email**: Email del usuario
    - **password**: Contraseña
    
    Returns:
        - **access_token**: Token JWT para autenticación (30 minutos)
        - **refresh_token**: Token para renovar el access_token (7 días)
        - **user**: Información del usuario autenticado
    """
    # Autenticar usuario
    user = UserService.authenticate_user(db, credentials.email, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo. Contacta con soporte."
        )
    
    # Crear tokens
    access_token = create_access_token(data={"sub": user.id, "role": user.role.value})
    refresh_token = create_refresh_token(data={"sub": user.id})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user
    }


@router.post("/refresh", response_model=Token)
def refresh_token(
    token_data: TokenRefresh,
    db: Session = Depends(get_db)
):
    """
    Renueva el access token usando un refresh token válido
    
    - **refresh_token**: Token de refresco obtenido en el login
    """
    # Decodificar y validar refresh token
    payload = decode_token(token_data.refresh_token)
    validate_token_type(payload, "refresh")
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )
    
    # Obtener usuario
    user = UserService.get_user_by_id(db, user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o inactivo"
        )
    
    # Crear nuevos tokens
    access_token = create_access_token(data={"sub": user.id, "role": user.role.value})
    new_refresh_token = create_refresh_token(data={"sub": user.id})
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "user": user
    }


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene la información del usuario autenticado actual
    
    Requiere: Token de autenticación válido
    """
    return current_user


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    """
    Cierra sesión del usuario actual

    Nota: En una implementación JWT stateless, el logout es principalmente
    del lado del cliente (eliminar token). Para invalidación real se necesitaría
    una lista negra de tokens o tokens de sesión en base de datos.
    """
    return {
        "message": "Sesión cerrada correctamente",
        "user_id": current_user.id
    }


# ─── Google SSO ───────────────────────────────────────────────────────────────

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


@router.get("/google")
async def google_login():
    """
    Redirige al usuario a la pantalla de login de Google.
    Requiere GOOGLE_CLIENT_ID y GOOGLE_CLIENT_SECRET en .env
    """
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google SSO no configurado. Añade GOOGLE_CLIENT_ID y GOOGLE_CLIENT_SECRET en el archivo .env"
        )
    state = secrets.token_urlsafe(16)
    params = (
        f"?client_id={settings.GOOGLE_CLIENT_ID}"
        f"&redirect_uri={settings.GOOGLE_REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=openid%20email%20profile"
        f"&state={state}"
    )
    return RedirectResponse(url=GOOGLE_AUTH_URL + params)


@router.get("/google/callback")
async def google_callback(code: str, db: Session = Depends(get_db)):
    """
    Callback de Google OAuth2.
    Crea o recupera el usuario y devuelve tokens JWT.
    """
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=501, detail="Google SSO no configurado")

    async with AsyncOAuth2Client(
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
    ) as client:
        token_response = await client.fetch_token(
            GOOGLE_TOKEN_URL,
            code=code,
            redirect_uri=settings.GOOGLE_REDIRECT_URI,
        )
        userinfo_response = await client.get(GOOGLE_USERINFO_URL)
        userinfo = userinfo_response.json()

    email = userinfo.get("email")
    full_name = userinfo.get("name", "")
    google_id = userinfo.get("sub")

    if not email:
        raise HTTPException(status_code=400, detail="No se pudo obtener el email de Google")

    # Buscar usuario existente o crear uno nuevo
    user = UserService.get_user_by_email(db, email)
    if not user:
        from app.schemas.user import UserCreate
        from app.models.user import UserRole
        user_data = UserCreate(
            email=email,
            username=f"google_{google_id}",
            full_name=full_name,
            password=secrets.token_urlsafe(32),
            role=UserRole.CONSUMER,
        )
        user = UserService.create_user(db, user_data)

    access_token = create_access_token(data={"sub": user.id, "role": user.role.value})
    refresh_token = create_refresh_token(data={"sub": user.id})

    # Redirige al frontend con los tokens en la URL (el JS los captura y guarda)
    frontend_url = (
        f"/?access_token={access_token}"
        f"&refresh_token={refresh_token}"
        f"&user_id={user.id}"
    )
    return RedirectResponse(url=frontend_url)