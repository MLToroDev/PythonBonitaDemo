from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status

from ...dependencies import get_contratos_service
from ...domain.contratos.services import ContratosService
from ...domain.flows.catalog import (
    FlowNotDefinedError,
    FlowProcessResolutionError,
    get_defined_flows,
    resolve_process_id_for_flow,
)
from ..dto.contratos import StartProcessResponseDTO, to_start_process_response_dto
from ..dto.flows import StartFlowPayloadDTO


router = APIRouter(prefix="/flujos", tags=["Flujos"])


@router.post(
    "/{flow_slug}/iniciar",
    response_model=StartProcessResponseDTO,
    status_code=status.HTTP_201_CREATED,
)
async def start_flow_instance(
    flow_slug: str,
    payload: StartFlowPayloadDTO,
    service: ContratosService = Depends(get_contratos_service),
) -> StartProcessResponseDTO:
    processes = list(service.listar_procesos(page=0, count=100))

    try:
        process_id = resolve_process_id_for_flow(flow_slug, processes)
    except FlowNotDefinedError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": f"El flujo '{flow_slug}' no está definido en la configuración.",
                "timestamp": datetime.utcnow().isoformat() + "Z",
            },
        ) from None
    except FlowProcessResolutionError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": str(exc),
                "flow_slug": flow_slug,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            },
        ) from exc

    contract_inputs = payload.contract_inputs or None
    result = service.iniciar_proceso(
        process_id=process_id,
        contract_inputs=contract_inputs,
    )

    dto = to_start_process_response_dto(result)
    dto.metadata.update(
        _build_flow_metadata(
            flow_slug=flow_slug,
            process_id=process_id,
        )
    )
    return dto


def _build_flow_metadata(*, flow_slug: str, process_id: str) -> Dict[str, Any]:
    # Exponemos datos adicionales del flujo para uso del cliente.
    flows = get_defined_flows()
    flow_definition = flows.get(flow_slug)
    payload: Dict[str, Any] = {
        "flow_slug": flow_slug,
        "bonita_process_id": process_id,
    }
    if flow_definition:
        payload.setdefault("flow_display_name", flow_definition.display_name)
        if flow_definition.metadata:
            payload.setdefault("flow_metadata", flow_definition.metadata)
    return payload

