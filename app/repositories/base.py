"""
Repositorio base con operaciones CRUD genéricas.
"""
from typing import Generic, TypeVar, Type, Optional, List, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from pydantic import BaseModel

from app.models.bdm_models import Base as ModelBase

ModelType = TypeVar("ModelType", bound=ModelBase)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Repositorio base con operaciones CRUD genéricas.
    """
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get(self, id: UUID) -> Optional[ModelType]:
        """Obtener un registro por ID."""
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[dict] = None,
        order_by: Optional[str] = None
    ) -> List[ModelType]:
        """Obtener múltiples registros con paginación y filtros."""
        query = self.db.query(self.model)
        
        # Aplicar filtros
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key) and value is not None:
                    if isinstance(value, list):
                        query = query.filter(getattr(self.model, key).in_(value))
                    else:
                        query = query.filter(getattr(self.model, key) == value)
        
        # Ordenar
        if order_by:
            if order_by.startswith("-"):
                # Orden descendente
                field = order_by[1:]
                if hasattr(self.model, field):
                    query = query.order_by(getattr(self.model, field).desc())
            else:
                # Orden ascendente
                if hasattr(self.model, order_by):
                    query = query.order_by(getattr(self.model, order_by))
        
        return query.offset(skip).limit(limit).all()

    def count(self, filters: Optional[dict] = None) -> int:
        """Contar registros con filtros opcionales."""
        query = self.db.query(self.model)
        
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key) and value is not None:
                    if isinstance(value, list):
                        query = query.filter(getattr(self.model, key).in_(value))
                    else:
                        query = query.filter(getattr(self.model, key) == value)
        
        return query.count()

    def create(self, obj_in: CreateSchemaType) -> ModelType:
        """Crear un nuevo registro."""
        obj_data = obj_in.model_dump() if hasattr(obj_in, "model_dump") else obj_in.dict()
        db_obj = self.model(**obj_data)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, id: UUID, obj_in: UpdateSchemaType) -> Optional[ModelType]:
        """Actualizar un registro existente."""
        db_obj = self.get(id)
        if not db_obj:
            return None
        
        obj_data = obj_in.model_dump(exclude_unset=True) if hasattr(obj_in, "model_dump") else obj_in.dict(exclude_unset=True)
        
        for field, value in obj_data.items():
            setattr(db_obj, field, value)
        
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, id: UUID) -> bool:
        """Eliminar un registro."""
        db_obj = self.get(id)
        if not db_obj:
            return False
        
        self.db.delete(db_obj)
        self.db.commit()
        return True

    def exists(self, id: UUID) -> bool:
        """Verificar si un registro existe."""
        return self.db.query(self.model).filter(self.model.id == id).first() is not None

