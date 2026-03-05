"""
Servicio de Maquinaria
Contiene la lógica de negocio para gestión de maquinaria
"""
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from fastapi import HTTPException, status
from app.models.machinery import Machinery, MachineryType
from app.schemas.machinery import MachineryCreate, MachineryUpdate, MachinerySearch
import json


class MachineryService:
    """Servicio para operaciones CRUD de maquinaria"""
    
    @staticmethod
    def get_machinery_by_id(db: Session, machinery_id: int) -> Optional[Machinery]:
        """Obtiene una máquina por ID"""
        return db.query(Machinery).filter(Machinery.id == machinery_id).first()
    
    @staticmethod
    def get_machinery_list(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        owner_id: Optional[int] = None,
        is_available: Optional[bool] = None,
        is_active: bool = True
    ) -> List[Machinery]:
        """
        Obtiene lista de maquinaria con filtros básicos
        """
        query = db.query(Machinery).filter(Machinery.is_active == is_active)
        
        if owner_id is not None:
            query = query.filter(Machinery.owner_id == owner_id)
        
        if is_available is not None:
            query = query.filter(Machinery.is_available == is_available)
        
        return query.order_by(Machinery.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def search_machinery(
        db: Session,
        search_params: MachinerySearch
    ) -> Tuple[List[Machinery], int]:
        """
        Búsqueda avanzada de maquinaria
        
        Args:
            db: Sesión de base de datos
            search_params: Parámetros de búsqueda
            
        Returns:
            Tuple[List[Machinery], int]: Lista de máquinas y total de resultados
        """
        query = db.query(Machinery).filter(Machinery.is_active == True)
        
        # Filtro por disponibilidad
        if search_params.is_available:
            query = query.filter(Machinery.is_available == True)
        
        # Filtro por tipo de maquinaria
        if search_params.machinery_type:
            query = query.filter(Machinery.machinery_type == search_params.machinery_type)
        
        # Filtro por ciudad
        if search_params.location_city:
            query = query.filter(
                Machinery.location_city.ilike(f"%{search_params.location_city}%")
            )
        
        # Filtro por provincia
        if search_params.location_province:
            query = query.filter(
                Machinery.location_province.ilike(f"%{search_params.location_province}%")
            )
        
        # Filtro por rango de precio
        if search_params.min_price is not None:
            query = query.filter(Machinery.daily_rate >= search_params.min_price)
        
        if search_params.max_price is not None:
            query = query.filter(Machinery.daily_rate <= search_params.max_price)
        
        # Búsqueda por texto (título, descripción, marca, modelo)
        if search_params.search_text:
            search_pattern = f"%{search_params.search_text}%"
            query = query.filter(
                or_(
                    Machinery.title.ilike(search_pattern),
                    Machinery.description.ilike(search_pattern),
                    Machinery.brand.ilike(search_pattern),
                    Machinery.model.ilike(search_pattern)
                )
            )
        
        # Filtro por requiere operador
        if search_params.requires_operator is not None:
            query = query.filter(Machinery.requires_operator == search_params.requires_operator)
        
        # Filtro por entrega disponible
        if search_params.delivery_available is not None:
            query = query.filter(Machinery.delivery_available == search_params.delivery_available)
        
        # Contar total antes de paginación
        total = query.count()
        
        # Ordenamiento
        if search_params.sort_by == "daily_rate":
            order_col = Machinery.daily_rate
        elif search_params.sort_by == "title":
            order_col = Machinery.title
        else:
            order_col = Machinery.created_at
        
        if search_params.sort_order == "asc":
            query = query.order_by(order_col.asc())
        else:
            query = query.order_by(order_col.desc())
        
        # Paginación
        machinery_list = query.offset(search_params.skip).limit(search_params.limit).all()
        
        return machinery_list, total
    
    @staticmethod
    def create_machinery(
        db: Session,
        machinery_data: MachineryCreate,
        owner_id: int
    ) -> Machinery:
        """
        Crea nueva maquinaria
        
        Args:
            db: Sesión de base de datos
            machinery_data: Datos de la maquinaria
            owner_id: ID del propietario
            
        Returns:
            Machinery: Maquinaria creada
        """
        # Convertir lista de imágenes a JSON string si existe
        images_json = None
        if machinery_data.images:
            images_json = json.dumps(machinery_data.images)
        
        db_machinery = Machinery(
            **machinery_data.dict(exclude={'images'}),
            owner_id=owner_id,
            images=images_json
        )
        
        db.add(db_machinery)
        db.commit()
        db.refresh(db_machinery)
        return db_machinery
    
    @staticmethod
    def update_machinery(
        db: Session,
        machinery_id: int,
        machinery_data: MachineryUpdate,
        user_id: int
    ) -> Machinery:
        """
        Actualiza maquinaria
        
        Args:
            db: Sesión de base de datos
            machinery_id: ID de la maquinaria
            machinery_data: Datos a actualizar
            user_id: ID del usuario que actualiza (debe ser propietario)
            
        Returns:
            Machinery: Maquinaria actualizada
            
        Raises:
            HTTPException: Si no existe o no tiene permisos
        """
        db_machinery = MachineryService.get_machinery_by_id(db, machinery_id)
        
        if not db_machinery:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Maquinaria no encontrada"
            )
        
        # Verificar que sea el propietario
        if db_machinery.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para actualizar esta maquinaria"
            )
        
        # Actualizar campos
        update_data = machinery_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_machinery, field, value)
        
        db.commit()
        db.refresh(db_machinery)
        return db_machinery
    
    @staticmethod
    def delete_machinery(db: Session, machinery_id: int, user_id: int) -> bool:
        """
        Elimina maquinaria (soft delete)
        
        Args:
            db: Sesión de base de datos
            machinery_id: ID de la maquinaria
            user_id: ID del usuario (debe ser propietario)
            
        Returns:
            bool: True si se eliminó correctamente
        """
        db_machinery = MachineryService.get_machinery_by_id(db, machinery_id)
        
        if not db_machinery:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Maquinaria no encontrada"
            )
        
        if db_machinery.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para eliminar esta maquinaria"
            )
        
        db_machinery.is_active = False
        db_machinery.is_available = False
        db.commit()
        return True
    
    @staticmethod
    def toggle_availability(
        db: Session,
        machinery_id: int,
        user_id: int,
        is_available: bool
    ) -> Machinery:
        """
        Cambia la disponibilidad de la maquinaria
        """
        db_machinery = MachineryService.get_machinery_by_id(db, machinery_id)
        
        if not db_machinery:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Maquinaria no encontrada"
            )
        
        if db_machinery.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para modificar esta maquinaria"
            )
        
        db_machinery.is_available = is_available
        db.commit()
        db.refresh(db_machinery)
        return db_machinery
    
    @staticmethod
    def get_machinery_types_stats(db: Session) -> dict:
        """
        Obtiene estadísticas de tipos de maquinaria disponibles
        """
        stats = {}
        for machinery_type in MachineryType:
            count = db.query(Machinery).filter(
                Machinery.machinery_type == machinery_type,
                Machinery.is_active == True,
                Machinery.is_available == True
            ).count()
            stats[machinery_type.value] = count
        
        return stats