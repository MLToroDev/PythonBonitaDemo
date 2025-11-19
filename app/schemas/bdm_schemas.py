"""
Schemas Pydantic para validación y serialización de datos.
Contratos de entrada/salida para la API REST.
"""
from datetime import date
from decimal import Decimal
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


# ==================== PerfilContratista ====================

class PerfilContratistaBase(BaseModel):
    nombre_completo: Optional[str] = None
    documento_identidad: Optional[str] = None
    id_usuario_bonita: Optional[str] = None
    estado: Optional[int] = None


class PerfilContratistaCreate(PerfilContratistaBase):
    pass


class PerfilContratistaUpdate(BaseModel):
    nombre_completo: Optional[str] = None
    documento_identidad: Optional[str] = None
    id_usuario_bonita: Optional[str] = None
    estado: Optional[int] = None


class PerfilContratista(PerfilContratistaBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)


# ==================== ContratoInterAdministrativo ====================

class ContratoInterAdministrativoBase(BaseModel):
    numero_contrato: Optional[str] = None
    supervisor: Optional[int] = None
    contratista: Optional[int] = None


class ContratoInterAdministrativoCreate(ContratoInterAdministrativoBase):
    pass


class ContratoInterAdministrativoUpdate(BaseModel):
    numero_contrato: Optional[str] = None
    supervisor: Optional[int] = None
    contratista: Optional[int] = None


class ContratoInterAdministrativo(ContratoInterAdministrativoBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)


# ==================== Componente ====================

class ComponenteBase(BaseModel):
    indice: Optional[int] = None
    descripcion: Optional[str] = None
    componente_padre_id: Optional[UUID] = None


class ComponenteCreate(ComponenteBase):
    contrato_marco_id: Optional[UUID] = None


class ComponenteUpdate(BaseModel):
    indice: Optional[int] = None
    descripcion: Optional[str] = None
    componente_padre_id: Optional[UUID] = None
    contrato_marco_id: Optional[UUID] = None


class Componente(ComponenteBase):
    id: UUID
    contrato_marco_id: Optional[UUID] = None
    model_config = ConfigDict(from_attributes=True)


# ==================== ObjetivoContrato ====================

class ObjetivoContratoBase(BaseModel):
    indice: Optional[int] = None
    descripcion: Optional[str] = None


class ObjetivoContratoCreate(ObjetivoContratoBase):
    componente_id: Optional[UUID] = None


class ObjetivoContratoUpdate(BaseModel):
    indice: Optional[int] = None
    descripcion: Optional[str] = None
    componente_id: Optional[UUID] = None


class ObjetivoContrato(ObjetivoContratoBase):
    id: UUID
    componente_id: Optional[UUID] = None
    model_config = ConfigDict(from_attributes=True)


# ==================== EvidenciaContrato ====================

class EvidenciaContratoBase(BaseModel):
    indice: Optional[int] = None
    descripcion: Optional[str] = None


class EvidenciaContratoCreate(EvidenciaContratoBase):
    objetivo_contrato_id: Optional[UUID] = None
    obligacion_id: Optional[UUID] = None


class EvidenciaContratoUpdate(BaseModel):
    indice: Optional[int] = None
    descripcion: Optional[str] = None
    objetivo_contrato_id: Optional[UUID] = None
    obligacion_id: Optional[UUID] = None


class EvidenciaContrato(EvidenciaContratoBase):
    id: UUID
    objetivo_contrato_id: Optional[UUID] = None
    obligacion_id: Optional[UUID] = None
    model_config = ConfigDict(from_attributes=True)


# ==================== Contrato ====================

class ContratoBase(BaseModel):
    numero_contrato: Optional[str] = None
    fecha_inicio: Optional[date] = None
    estado: Optional[str] = None
    plazo: Optional[str] = None
    objeto: Optional[str] = None
    valor_contrato: Optional[Decimal] = None
    supervisor: Optional[int] = None


class ContratoCreate(ContratoBase):
    perfil_contratista_id: UUID
    padre_id: UUID


class ContratoUpdate(BaseModel):
    numero_contrato: Optional[str] = None
    fecha_inicio: Optional[date] = None
    estado: Optional[str] = None
    plazo: Optional[str] = None
    objeto: Optional[str] = None
    valor_contrato: Optional[Decimal] = None
    supervisor: Optional[int] = None
    perfil_contratista_id: Optional[UUID] = None
    padre_id: Optional[UUID] = None


class Contrato(ContratoBase):
    id: UUID
    perfil_contratista_id: UUID
    padre_id: UUID
    model_config = ConfigDict(from_attributes=True)


# ==================== Obligacion ====================

class ObligacionBase(BaseModel):
    indice: Optional[int] = None
    descripcion: Optional[str] = None


class ObligacionCreate(ObligacionBase):
    contrato_id: Optional[UUID] = None


class ObligacionUpdate(BaseModel):
    indice: Optional[int] = None
    descripcion: Optional[str] = None
    contrato_id: Optional[UUID] = None


class Obligacion(ObligacionBase):
    id: UUID
    contrato_id: Optional[UUID] = None
    model_config = ConfigDict(from_attributes=True)


# ==================== Informe ====================

class InformeBase(BaseModel):
    valor_periodo: Optional[Decimal] = None
    estado: Optional[str] = None
    mes: Optional[int] = None
    anio: Optional[int] = None
    fecha_inicio_periodo: Optional[date] = None
    fecha_fin_periodo: Optional[date] = None


class InformeCreate(InformeBase):
    contrato_id: Optional[UUID] = None


class InformeUpdate(BaseModel):
    valor_periodo: Optional[Decimal] = None
    estado: Optional[str] = None
    mes: Optional[int] = None
    anio: Optional[int] = None
    fecha_inicio_periodo: Optional[date] = None
    fecha_fin_periodo: Optional[date] = None
    contrato_id: Optional[UUID] = None


class Informe(InformeBase):
    id: UUID
    contrato_id: Optional[UUID] = None
    model_config = ConfigDict(from_attributes=True)


# ==================== Ejecucion ====================

class EjecucionBase(BaseModel):
    evidencia_adjunta: Optional[str] = None


class EjecucionCreate(EjecucionBase):
    obligacion_id: UUID
    informe_id: UUID


class EjecucionUpdate(BaseModel):
    evidencia_adjunta: Optional[str] = None
    obligacion_id: Optional[UUID] = None
    informe_id: Optional[UUID] = None


class Ejecucion(EjecucionBase):
    id: UUID
    obligacion_id: UUID
    informe_id: UUID
    model_config = ConfigDict(from_attributes=True)


# ==================== DescripcionEjecucion ====================

class DescripcionEjecucionBase(BaseModel):
    indice: Optional[int] = None
    descripcion: Optional[str] = None


class DescripcionEjecucionCreate(DescripcionEjecucionBase):
    ejecucion_id: UUID


class DescripcionEjecucionUpdate(BaseModel):
    indice: Optional[int] = None
    descripcion: Optional[str] = None
    ejecucion_id: Optional[UUID] = None


class DescripcionEjecucion(DescripcionEjecucionBase):
    id: UUID
    ejecucion_id: UUID
    model_config = ConfigDict(from_attributes=True)


# ==================== Schemas con relaciones (para respuestas completas) ====================

class ContratoConRelaciones(Contrato):
    """Contrato con todas sus relaciones cargadas."""
    perfil_contratista: Optional[PerfilContratista] = None
    informes: List[Informe] = []
    obligaciones: List[Obligacion] = []


class InformeConRelaciones(Informe):
    """Informe con ejecuciones cargadas."""
    ejecuciones: List[Ejecucion] = []


class EjecucionConRelaciones(Ejecucion):
    """Ejecución con descripciones cargadas."""
    descripciones: List[DescripcionEjecucion] = []


# ==================== Paginación ====================

class PaginatedResponse(BaseModel):
    """Respuesta paginada genérica."""
    items: List[BaseModel]
    total: int
    page: int
    size: int
    pages: int

