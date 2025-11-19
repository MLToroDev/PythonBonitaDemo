"""
Servicio de lógica de negocio para Informes.
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.bdm_models import Informe, Contrato
from app.schemas.bdm_schemas import (
    InformeCreate,
    InformeUpdate,
    Informe as InformeSchema,
    InformeConRelaciones
)
from app.repositories.informe_repository import InformeRepository
from app.repositories.base import BaseRepository


class InformeService:
    """
    Servicio que encapsula la lógica de negocio para Informes.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.informe_repo = InformeRepository(Informe, db)
        self.contrato_repo = BaseRepository(Contrato, db)

    def get_informe(self, informe_id: UUID) -> Optional[InformeSchema]:
        """Obtener un informe por ID."""
        informe = self.informe_repo.get(informe_id)
        if not informe:
            return None
        return InformeSchema.model_validate(informe)

    def get_informe_with_relations(self, informe_id: UUID) -> Optional[InformeConRelaciones]:
        """Obtener un informe con todas sus relaciones."""
        informe = self.informe_repo.get_with_relations(informe_id)
        if not informe:
            return None
        return InformeConRelaciones.model_validate(informe)

    def get_informes(
        self,
        skip: int = 0,
        limit: int = 100,
        estado: Optional[str] = None,
        anio: Optional[int] = None,
        mes: Optional[int] = None
    ) -> List[InformeSchema]:
        """Obtener lista de informes con filtros opcionales."""
        filters = {}
        if estado:
            filters["estado"] = estado
        if anio:
            filters["anio"] = anio
        if mes:
            filters["mes"] = mes
        
        informes = self.informe_repo.get_all(skip=skip, limit=limit, filters=filters)
        return [InformeSchema.model_validate(i) for i in informes]

    def get_informes_by_contrato_id(
        self,
        contrato_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[InformeSchema]:
        """
        Obtener informes por ID de contrato.
        Reemplaza la funcionalidad del BDM findByContratoId.
        """
        informes = self.informe_repo.get_by_contrato_id(
            contrato_id=contrato_id,
            skip=skip,
            limit=limit
        )
        return [InformeSchema.model_validate(i) for i in informes]

    def get_informes_by_periodo(
        self,
        anio: int,
        mes: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[InformeSchema]:
        """Obtener informes por período (año y opcionalmente mes)."""
        informes = self.informe_repo.get_by_periodo(
            anio=anio,
            mes=mes,
            skip=skip,
            limit=limit
        )
        return [InformeSchema.model_validate(i) for i in informes]

    def create_informe(self, informe_in: InformeCreate) -> InformeSchema:
        """
        Crear un nuevo informe.
        Valida que exista el contrato asociado.
        """
        # Validar que el contrato existe
        if informe_in.contrato_id and not self.contrato_repo.exists(informe_in.contrato_id):
            raise ValueError(f"Contrato con ID {informe_in.contrato_id} no existe")
        
        informe = self.informe_repo.create(informe_in)
        return InformeSchema.model_validate(informe)

    def update_informe(
        self,
        informe_id: UUID,
        informe_in: InformeUpdate
    ) -> Optional[InformeSchema]:
        """
        Actualizar un informe existente.
        Valida relaciones si se están actualizando.
        """
        # Validar contrato si se está actualizando
        if informe_in.contrato_id:
            if not self.contrato_repo.exists(informe_in.contrato_id):
                raise ValueError(f"Contrato con ID {informe_in.contrato_id} no existe")
        
        informe = self.informe_repo.update(informe_id, informe_in)
        if not informe:
            return None
        return InformeSchema.model_validate(informe)

    def delete_informe(self, informe_id: UUID) -> bool:
        """Eliminar un informe."""
        return self.informe_repo.delete(informe_id)

    def count_informes(
        self,
        estado: Optional[str] = None,
        anio: Optional[int] = None,
        mes: Optional[int] = None
    ) -> int:
        """Contar informes con filtros opcionales."""
        filters = {}
        if estado:
            filters["estado"] = estado
        if anio:
            filters["anio"] = anio
        if mes:
            filters["mes"] = mes
        return self.informe_repo.count(filters=filters)

