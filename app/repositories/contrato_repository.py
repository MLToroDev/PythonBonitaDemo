"""
Repositorio específico para Contrato con consultas personalizadas.
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_

from app.models.bdm_models import Contrato, PerfilContratista
from app.schemas.bdm_schemas import (
    ContratoCreate,
    ContratoUpdate
)
from app.repositories.base import BaseRepository


class ContratoRepository(BaseRepository[Contrato, ContratoCreate, ContratoUpdate]):
    """
    Repositorio para Contrato con métodos específicos de negocio.
    """
    
    def get_by_usuario_bonita(
        self,
        id_usuario_bonita: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Contrato]:
        """
        Obtener contratos por ID de usuario de Bonita.
        Equivalente a la query findByUsuarioBonita del BDM.
        """
        return (
            self.db.query(Contrato)
            .join(PerfilContratista)
            .filter(PerfilContratista.id_usuario_bonita == id_usuario_bonita)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_estado(
        self,
        estado: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Contrato]:
        """Obtener contratos por estado."""
        return (
            self.db.query(self.model)
            .filter(self.model.estado == estado)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_with_relations(self, id: UUID) -> Optional[Contrato]:
        """Obtener contrato con todas sus relaciones cargadas."""
        return (
            self.db.query(self.model)
            .options(
                joinedload(self.model.perfil_contratista),
                joinedload(self.model.informes),
                joinedload(self.model.obligaciones)
            )
            .filter(self.model.id == id)
            .first()
        )

    def get_by_numero_contrato(self, numero_contrato: str) -> Optional[Contrato]:
        """Obtener contrato por número de contrato."""
        return (
            self.db.query(self.model)
            .filter(self.model.numero_contrato == numero_contrato)
            .first()
        )

