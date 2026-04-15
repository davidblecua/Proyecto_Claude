"""
Endpoints de Usuarios
Gestión de perfiles y usuarios
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.db.database import get_db
from app.schemas.user import (
    UserResponse, UserUpdate, UserListResponse,
    PasswordChange, UserUpdateRole
)
from app.services.user_service import UserService
from app.core.dependencies import get_current_user, require_admin
from app.models.user import User, UserRole

VALID_LANGUAGES = {"es", "ca", "en"}


class LanguageUpdate(BaseModel):
    language: str

router = APIRouter(prefix="/users", tags=["Usuarios"])


@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_user)):
    """Obtiene el perfil del usuario actual"""
    return current_user


@router.put("/me", response_model=UserResponse)
def update_my_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualiza el perfil del usuario actual"""
    return UserService.update_user(db, current_user.id, user_data)


@router.patch("/me/language", response_model=UserResponse)
def update_my_language(
    body: LanguageUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualiza el idioma preferido del usuario ('es', 'ca' o 'en')"""
    if body.language not in VALID_LANGUAGES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Idioma no válido. Valores permitidos: {sorted(VALID_LANGUAGES)}"
        )
    current_user.preferred_language = body.language
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/me/change-password", response_model=UserResponse)
def change_my_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cambia la contraseña del usuario actual"""
    return UserService.change_password(
        db,
        current_user.id,
        password_data.current_password,
        password_data.new_password
    )


@router.get("", response_model=List[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 100,
    role: Optional[UserRole] = None,
    is_active: Optional[bool] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Lista todos los usuarios (solo admin)
    
    Filtros opcionales:
    - **role**: Filtrar por rol
    - **is_active**: Filtrar por estado activo
    """
    return UserService.get_users(db, skip, limit, role, is_active)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Obtiene un usuario por ID (solo admin)"""
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return user


@router.put("/{user_id}/role", response_model=UserResponse)
def update_user_role(
    user_id: int,
    role_data: UserUpdateRole,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Actualiza el rol de un usuario (solo admin)"""
    return UserService.update_user_role(db, user_id, role_data.role)


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Desactiva un usuario (soft delete) (solo admin)"""
    UserService.delete_user(db, user_id)
    return {"message": "Usuario desactivado correctamente"}