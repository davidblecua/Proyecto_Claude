"""
Schemas de Usuario
Validación y serialización de datos de usuario usando Pydantic
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator
from app.models.user import UserRole


class UserBase(BaseModel):
    """Schema base de usuario"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    company_name: Optional[str] = Field(None, max_length=255)
    tax_id: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = Field(None, max_length=500)


class UserCreate(UserBase):
    """Schema para crear usuario"""
    password: str = Field(..., min_length=8, max_length=100)
    role: Optional[UserRole] = UserRole.PUBLISHER
    
    @validator('password')
    def password_strength(cls, v):
        """Valida la fortaleza de la contraseña"""
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        if not any(char.isdigit() for char in v):
            raise ValueError('La contraseña debe contener al menos un número')
        if not any(char.isupper() for char in v):
            raise ValueError('La contraseña debe contener al menos una mayúscula')
        return v


class UserUpdate(BaseModel):
    """Schema para actualizar usuario"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    company_name: Optional[str] = None
    tax_id: Optional[str] = None
    address: Optional[str] = None
    is_active: Optional[bool] = None


class UserUpdateRole(BaseModel):
    """Schema para actualizar rol (solo admin)"""
    role: UserRole


class UserResponse(UserBase):
    """Schema de respuesta de usuario"""
    id: int
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True  # Permite crear desde modelos ORM


class UserLogin(BaseModel):
    """Schema para login"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Schema de respuesta de autenticación"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenRefresh(BaseModel):
    """Schema para refrescar token"""
    refresh_token: str


class PasswordChange(BaseModel):
    """Schema para cambiar contraseña"""
    current_password: str
    new_password: str = Field(..., min_length=8)
    
    @validator('new_password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        if not any(char.isdigit() for char in v):
            raise ValueError('La contraseña debe contener al menos un número')
        if not any(char.isupper() for char in v):
            raise ValueError('La contraseña debe contener al menos una mayúscula')
        return v


class UserListResponse(BaseModel):
    """Schema para lista de usuarios"""
    total: int
    users: list[UserResponse]


class ForgotPasswordRequest(BaseModel):
    """Schema para solicitar recuperación de contraseña"""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Schema para establecer nueva contraseña con token"""
    token: str = Field(..., min_length=10)
    new_password: str = Field(..., min_length=8, max_length=100)

    @validator('new_password')
    def password_strength(cls, v):
        if not any(c.isdigit() for c in v):
            raise ValueError('La contraseña debe contener al menos un número')
        if not any(c.isupper() for c in v):
            raise ValueError('La contraseña debe contener al menos una mayúscula')
        return v