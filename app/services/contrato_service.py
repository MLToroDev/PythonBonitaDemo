"""
Servicio de lógica de negocio para Contratos.
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.bdm_models import Contrato
from app.schemas.bdm_schemas import (
    ContratoCreate,
    ContratoUpdate,
    Contrato as ContratoSchema,
    ContratoConRelaciones
)
from app.repositories.contrato_repository import ContratoRepository
from app.repositories.base import BaseRepository
from app.models.bdm_models import PerfilContratista, ContratoInterAdministrativo


class ContratoService:
    """
    Servicio que encapsula la lógica de negocio para Contratos.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.contrato_repo = ContratoRepository(Contrato, db)
        self.perfil_repo = BaseRepository(PerfilContratista, db)
        self.contrato_marco_repo = BaseRepository(ContratoInterAdministrativo, db)

    def get_contrato(self, contrato_id: UUID) -> Optional[ContratoSchema]:
        """Obtener un contrato por ID."""
        contrato = self.contrato_repo.get(contrato_id)
        if not contrato:
            return None
        return ContratoSchema.model_validate(contrato)

    def get_contrato_with_relations(self, contrato_id: UUID) -> Optional[ContratoConRelaciones]:
        """Obtener un contrato con todas sus relaciones."""
        contrato = self.contrato_repo.get_with_relations(contrato_id)
        if not contrato:
            return None
        return ContratoConRelaciones.model_validate(contrato)

    def get_contratos(
        self,
        skip: int = 0,
        limit: int = 100,
        estado: Optional[str] = None,
        numero_contrato: Optional[str] = None
    ) -> List[ContratoSchema]:
        """Obtener lista de contratos con filtros opcionales."""
        filters = {}
        if estado:
            filters["estado"] = estado
        if numero_contrato:
            filters["numero_contrato"] = numero_contrato
        
        contratos = self.contrato_repo.get_all(skip=skip, limit=limit, filters=filters)
        return [ContratoSchema.model_validate(c) for c in contratos]

    def get_contratos_by_usuario_bonita(
        self,
        id_usuario_bonita: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[ContratoSchema]:
        """
        Obtener contratos por ID de usuario de Bonita.
        Reemplaza la funcionalidad del BDM findByUsuarioBonita.
        """
        contratos = self.contrato_repo.get_by_usuario_bonita(
            id_usuario_bonita=id_usuario_bonita,
            skip=skip,
            limit=limit
        )
        return [ContratoSchema.model_validate(c) for c in contratos]

    def create_contrato(self, contrato_in: ContratoCreate) -> ContratoSchema:
        """
        Crear un nuevo contrato.
        Valida que existan las relaciones requeridas.
        """
        # Validar que el perfil contratista existe
        if not self.perfil_repo.exists(contrato_in.perfil_contratista_id):
            raise ValueError(f"PerfilContratista con ID {contrato_in.perfil_contratista_id} no existe")
        
        # Validar que el contrato marco existe
        if not self.contrato_marco_repo.exists(contrato_in.padre_id):
            raise ValueError(f"ContratoInterAdministrativo con ID {contrato_in.padre_id} no existe")
        
        contrato = self.contrato_repo.create(contrato_in)
        return ContratoSchema.model_validate(contrato)

    def update_contrato(
        self,
        contrato_id: UUID,
        contrato_in: ContratoUpdate
    ) -> Optional[ContratoSchema]:
        """
        Actualizar un contrato existente.
        Valida relaciones si se están actualizando.
        """
        # Validar relaciones si se están actualizando
        if contrato_in.perfil_contratista_id:
            if not self.perfil_repo.exists(contrato_in.perfil_contratista_id):
                raise ValueError(f"PerfilContratista con ID {contrato_in.perfil_contratista_id} no existe")
        
        if contrato_in.padre_id:
            if not self.contrato_marco_repo.exists(contrato_in.padre_id):
                raise ValueError(f"ContratoInterAdministrativo con ID {contrato_in.padre_id} no existe")
        
        contrato = self.contrato_repo.update(contrato_id, contrato_in)
        if not contrato:
            return None
        return ContratoSchema.model_validate(contrato)

    def delete_contrato(self, contrato_id: UUID) -> bool:
        """Eliminar un contrato."""
        return self.contrato_repo.delete(contrato_id)

    def count_contratos(
        self,
        estado: Optional[str] = None,
        numero_contrato: Optional[str] = None
    ) -> int:
        """Contar contratos con filtros opcionales."""
        filters = {}
        if estado:
            filters["estado"] = estado
        if numero_contrato:
            filters["numero_contrato"] = numero_contrato
        return self.contrato_repo.count(filters=filters)

