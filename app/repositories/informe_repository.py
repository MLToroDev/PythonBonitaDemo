"""
Repositorio específico para Informe con consultas personalizadas.
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_

from app.models.bdm_models import Informe, Contrato
from app.schemas.bdm_schemas import (
    InformeCreate,
    InformeUpdate
)
from app.repositories.base import BaseRepository


class InformeRepository(BaseRepository[Informe, InformeCreate, InformeUpdate]):
    """
    Repositorio para Informe con métodos específicos de negocio.
    """
    
    def get_by_contrato_id(
        self,
        contrato_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Informe]:
        """
        Obtener informes por ID de contrato.
        Equivalente a la query findByContratoId del BDM.
        """
        return (
            self.db.query(self.model)
            .filter(self.model.contrato_id == contrato_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_periodo(
        self,
        anio: int,
        mes: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Informe]:
        """Obtener informes por año y opcionalmente por mes."""
        query = self.db.query(self.model).filter(self.model.anio == anio)
        
        if mes is not None:
            query = query.filter(self.model.mes == mes)
        
        return query.offset(skip).limit(limit).all()

    def get_by_estado(
        self,
        estado: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Informe]:
        """Obtener informes por estado."""
        return (
            self.db.query(self.model)
            .filter(self.model.estado == estado)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_with_relations(self, id: UUID) -> Optional[Informe]:
        """Obtener informe con todas sus relaciones cargadas."""
        return (
            self.db.query(self.model)
            .options(
                joinedload(self.model.contrato),
                joinedload(self.model.ejecuciones).joinedload("obligacion"),
                joinedload(self.model.ejecuciones).joinedload("descripciones")
            )
            .filter(self.model.id == id)
            .first()
        )

