from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class FlowSummaryDTO(BaseModel):
    slug: str = Field(..., description="Identificador semántico del flujo de negocio.")
    display_name: str = Field(
        ..., description="Nombre legible del flujo expuesto a la capa cliente."
    )
    disponible: bool = Field(
        ...,
        description="Indica si el flujo está configurado y disponible en Bonita.",
    )
    bonita_process_id: Optional[str] = Field(
        default=None, description="Identificador real del proceso en Bonita."
    )
    bonita_process_name: Optional[str] = Field(
        default=None,
        description="Nombre técnico del proceso en Bonita (oculto a clientes).",
    )
    bonita_version: Optional[str] = Field(
        default=None,
        description="Versión activa del proceso en Bonita.",
    )
    metadata: Dict[str, Any] = Field(default_factory=dict)


class StartFlowPayloadDTO(BaseModel):
    contract_inputs: Dict[str, Any] = Field(
        default_factory=dict,
        description="Payload del contrato esperado por el proceso.",
    )

