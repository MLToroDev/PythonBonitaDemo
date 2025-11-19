"""
Schemas Pydantic para validación y serialización.
"""
from app.schemas.bdm_schemas import (
    # PerfilContratista
    PerfilContratista,
    PerfilContratistaCreate,
    PerfilContratistaUpdate,
    # ContratoInterAdministrativo
    ContratoInterAdministrativo,
    ContratoInterAdministrativoCreate,
    ContratoInterAdministrativoUpdate,
    # Componente
    Componente,
    ComponenteCreate,
    ComponenteUpdate,
    # ObjetivoContrato
    ObjetivoContrato,
    ObjetivoContratoCreate,
    ObjetivoContratoUpdate,
    # EvidenciaContrato
    EvidenciaContrato,
    EvidenciaContratoCreate,
    EvidenciaContratoUpdate,
    # Contrato
    Contrato,
    ContratoCreate,
    ContratoUpdate,
    ContratoConRelaciones,
    # Obligacion
    Obligacion,
    ObligacionCreate,
    ObligacionUpdate,
    # Informe
    Informe,
    InformeCreate,
    InformeUpdate,
    InformeConRelaciones,
    # Ejecucion
    Ejecucion,
    EjecucionCreate,
    EjecucionUpdate,
    EjecucionConRelaciones,
    # DescripcionEjecucion
    DescripcionEjecucion,
    DescripcionEjecucionCreate,
    DescripcionEjecucionUpdate,
    # Paginación
    PaginatedResponse,
)

__all__ = [
    "PerfilContratista",
    "PerfilContratistaCreate",
    "PerfilContratistaUpdate",
    "ContratoInterAdministrativo",
    "ContratoInterAdministrativoCreate",
    "ContratoInterAdministrativoUpdate",
    "Componente",
    "ComponenteCreate",
    "ComponenteUpdate",
    "ObjetivoContrato",
    "ObjetivoContratoCreate",
    "ObjetivoContratoUpdate",
    "EvidenciaContrato",
    "EvidenciaContratoCreate",
    "EvidenciaContratoUpdate",
    "Contrato",
    "ContratoCreate",
    "ContratoUpdate",
    "ContratoConRelaciones",
    "Obligacion",
    "ObligacionCreate",
    "ObligacionUpdate",
    "Informe",
    "InformeCreate",
    "InformeUpdate",
    "InformeConRelaciones",
    "Ejecucion",
    "EjecucionCreate",
    "EjecucionUpdate",
    "EjecucionConRelaciones",
    "DescripcionEjecucion",
    "DescripcionEjecucionCreate",
    "DescripcionEjecucionUpdate",
    "PaginatedResponse",
]

