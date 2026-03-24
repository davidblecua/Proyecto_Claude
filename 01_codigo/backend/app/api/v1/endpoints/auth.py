"""
Endpoints de Autenticación
Login, registro y gestión de tokens
"""
import secrets
import time
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from authlib.integrations.httpx_client import AsyncOAuth2Client
from app.db.database import get_db
from app.schemas.user import UserCreate, UserLogin, Token, TokenRefresh, UserResponse, ForgotPasswordRequest, ResetPasswordRequest
from app.services.user_service import UserService
from app.core.security import create_access_token, create_refresh_token, decode_token, validate_token_type, get_password_hash
from app.core.dependencies import get_current_user
from app.core.config import settings
from app.models.user import User

_logger = logging.getLogger("uvicorn")

router = APIRouter(prefix="/auth", tags=["Autenticación"])

# ── Almacén temporal de códigos SSO (one-time, TTL=60s) ─────────────────────
# Clave: código aleatorio  Valor: {access_token, refresh_token, expires_at}
_sso_codes: dict = {}
_SSO_CODE_TTL = 60  # segundos


def _cleanup_sso_codes():
    """Elimina los códigos SSO caducados."""
    now = time.time()
    expired = [k for k, v in _sso_codes.items() if v["expires_at"] < now]
    for k in expired:
        _sso_codes.pop(k, None)


# ── Almacén temporal de tokens de reset de contraseña (one-time, TTL=1h) ────
_reset_tokens: dict = {}
_RESET_TOKEN_TTL = 3600  # 1 hora


def _cleanup_reset_tokens():
    """Elimina los tokens de reset caducados."""
    now = time.time()
    expired = [k for k, v in _reset_tokens.items() if v["expires_at"] < now]
    for k in expired:
        _reset_tokens.pop(k, None)


def _send_reset_email(email: str, token: str, full_name: str):
    """
    Envía el email de recuperación de contraseña.
    Si SMTP no está configurado (entorno de desarrollo), registra la URL en el log.
    """
    reset_url = f"{settings.APP_URL}/?reset_token={token}"

    if not settings.SMTP_HOST or not settings.SMTP_USER:
        _logger.info(
            f"[DEV - sin SMTP] Enlace de recuperación para {email}: {reset_url}"
        )
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Recuperación de contraseña - RentaMaq"
    msg["From"] = settings.SMTP_USER
    msg["To"] = email

    body = (
        f"Hola {full_name or email},\n\n"
        "Has solicitado recuperar tu contraseña en RentaMaq.\n\n"
        f"Haz clic en el siguiente enlace para crear una nueva contraseña:\n{reset_url}\n\n"
        "Este enlace expira en 1 hora y solo puede usarse una vez.\n\n"
        "Si no solicitaste este cambio, puedes ignorar este correo.\n\n"
        "— El equipo de RentaMaq"
    )
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT or 587) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            smtp.send_message(msg)
    except Exception as exc:
        _logger.error(f"Error enviando email de recuperación a {email}: {exc}")


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
    Genera un código de un solo uso (SSO code, TTL=60s) y redirige al
    frontend con ese código en la URL. El frontend lo intercambia por los
    tokens JWT llamando a GET /auth/google/token?code=<sso_code>.
    Los tokens JWT nunca aparecen en la URL ni en el historial del navegador.
    """
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=501, detail="Google SSO no configurado")

    async with AsyncOAuth2Client(
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
    ) as client:
        await client.fetch_token(
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

    # Generar código de un solo uso y almacenar los tokens en memoria
    _cleanup_sso_codes()
    sso_code = secrets.token_urlsafe(32)
    _sso_codes[sso_code] = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_at": time.time() + _SSO_CODE_TTL,
    }

    # Solo el código (no el JWT) va en la URL de redirección
    return RedirectResponse(url=f"/?sso_code={sso_code}")


@router.get("/google/token")
def google_exchange_token(code: str):
    """
    Intercambia un SSO code de un solo uso por los tokens JWT.
    El código expira en 60 segundos y solo puede usarse una vez.
    """
    _cleanup_sso_codes()
    entry = _sso_codes.pop(code, None)

    if not entry:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Código SSO inválido o expirado"
        )

    if time.time() > entry["expires_at"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Código SSO expirado"
        )

    return {
        "access_token": entry["access_token"],
        "refresh_token": entry["refresh_token"],
        "token_type": "bearer",
    }


# ─── Recuperación de contraseña ────────────────────────────────────────────

@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Solicita la recuperación de contraseña.

    Genera un token de un solo uso (TTL=1h) y envía un email con el enlace.
    Siempre devuelve el mismo mensaje para evitar enumeración de emails.
    En desarrollo (sin SMTP configurado), el enlace se imprime en el log del servidor.
    """
    _cleanup_reset_tokens()

    user = UserService.get_user_by_email(db, payload.email)
    if user and user.is_active:
        token = secrets.token_urlsafe(32)
        _reset_tokens[token] = {
            "user_id": user.id,
            "expires_at": time.time() + _RESET_TOKEN_TTL,
        }
        _send_reset_email(payload.email, token, user.full_name or "")

    return {
        "message": "Si el email está registrado, recibirás instrucciones para recuperar tu contraseña en breve."
    }


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Establece una nueva contraseña usando el token de recuperación.
    El token es de un solo uso y expira en 1 hora.
    """
    _cleanup_reset_tokens()

    entry = _reset_tokens.pop(payload.token, None)
    if not entry or time.time() > entry["expires_at"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token de recuperación inválido o expirado"
        )

    user = UserService.get_user_by_id(db, entry["user_id"])
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario no encontrado"
        )

    user.hashed_password = get_password_hash(payload.new_password)
    db.commit()

    return {"message": "Contraseña actualizada correctamente. Ya puedes iniciar sesión."}