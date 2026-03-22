"""
Servicio de Usuarios
Contiene la lógica de negocio para gestión de usuarios
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate, UserUpdateRole
from app.core.security import get_password_hash, verify_password
from datetime import datetime


class UserService:
    """Servicio para operaciones CRUD de usuarios"""
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Obtiene un usuario por ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Obtiene un usuario por email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Obtiene un usuario por username"""
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_users(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        role: Optional[UserRole] = None,
        is_active: Optional[bool] = None
    ) -> List[User]:
        """
        Obtiene lista de usuarios con filtros opcionales
        
        Args:
            db: Sesión de base de datos
            skip: Número de registros a saltar (paginación)
            limit: Número máximo de registros a devolver
            role: Filtrar por rol
            is_active: Filtrar por estado activo
        """
        query = db.query(User)
        
        if role is not None:
            query = query.filter(User.role == role)
        
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """
        Crea un nuevo usuario
        
        Args:
            db: Sesión de base de datos
            user_data: Datos del usuario a crear
            
        Returns:
            User: Usuario creado
            
        Raises:
            HTTPException: Si el email o username ya existen
        """
        # Verificar si el email ya existe
        if UserService.get_user_by_email(db, user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )
        
        # Verificar si el username ya existe
        if UserService.get_user_by_username(db, user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre de usuario ya está en uso"
            )
        
        # Crear usuario
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            phone=user_data.phone,
            company_name=user_data.company_name,
            tax_id=user_data.tax_id,
            address=user_data.address,
            role=user_data.role,
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def update_user(db: Session, user_id: int, user_data: UserUpdate) -> User:
        """
        Actualiza un usuario
        
        Args:
            db: Sesión de base de datos
            user_id: ID del usuario a actualizar
            user_data: Datos a actualizar
            
        Returns:
            User: Usuario actualizado
            
        Raises:
            HTTPException: Si el usuario no existe
        """
        db_user = UserService.get_user_by_id(db, user_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Actualizar campos
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def update_user_role(db: Session, user_id: int, new_role: UserRole) -> User:
        """
        Actualiza el rol de un usuario (solo admin)
        
        Args:
            db: Sesión de base de datos
            user_id: ID del usuario
            new_role: Nuevo rol
            
        Returns:
            User: Usuario actualizado
        """
        db_user = UserService.get_user_by_id(db, user_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        db_user.role = new_role
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """
        Elimina un usuario (soft delete - marca como inactivo)
        
        Args:
            db: Sesión de base de datos
            user_id: ID del usuario a eliminar
            
        Returns:
            bool: True si se eliminó correctamente
        """
        db_user = UserService.get_user_by_id(db, user_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        db_user.is_active = False
        db.commit()
        return True
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """
        Autentica un usuario
        
        Args:
            db: Sesión de base de datos
            email: Email del usuario
            password: Contraseña en texto plano
            
        Returns:
            User: Usuario autenticado o None si las credenciales son incorrectas
        """
        user = UserService.get_user_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        
        # Actualizar last_login
        user.last_login = datetime.utcnow()
        db.commit()
        
        return user
    
    @staticmethod
    def change_password(
        db: Session,
        user_id: int,
        current_password: str,
        new_password: str
    ) -> User:
        """
        Cambia la contraseña de un usuario
        
        Args:
            db: Sesión de base de datos
            user_id: ID del usuario
            current_password: Contraseña actual
            new_password: Nueva contraseña
            
        Returns:
            User: Usuario actualizado
            
        Raises:
            HTTPException: Si la contraseña actual es incorrecta
        """
        db_user = UserService.get_user_by_id(db, user_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Verificar contraseña actual
        if not verify_password(current_password, db_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contraseña actual incorrecta"
            )
        
        # Actualizar contraseña
        db_user.hashed_password = get_password_hash(new_password)
        db.commit()
        db.refresh(db_user)
        return db_user