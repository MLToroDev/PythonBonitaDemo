from __future__ import annotations

from typing import Dict, List

from fastapi import APIRouter, Depends

from ...dependencies import get_contratos_service
from ...domain.contratos.entities import ContractProcess
from ...domain.contratos.services import ContratosService
from ...domain.flows.catalog import (
    FlowProcessResolutionError,
    FlowDefinition,
    get_defined_flows,
    resolve_process_id_for_flow,
)
from ..dto.flows import FlowSummaryDTO


router = APIRouter(prefix="", tags=["Procesos"])


@router.get("/procesos-disponibles", response_model=List[FlowSummaryDTO])
async def list_available_processes(
    service: ContratosService = Depends(get_contratos_service),
) -> List[FlowSummaryDTO]:
    processes = list(service.listar_procesos(page=0, count=100))
    processes_by_id = {process.id: process for process in processes}
    flow_definitions = get_defined_flows()

    summaries: List[FlowSummaryDTO] = []
    for slug, definition in flow_definitions.items():
        summaries.append(
            _make_flow_summary(
                slug=slug,
                definition=definition,
                processes=processes,
                processes_by_id=processes_by_id,
            )
        )

    return summaries


def _make_flow_summary(
    *,
    slug: str,
    definition: FlowDefinition,
    processes: List[ContractProcess],
    processes_by_id: Dict[str, ContractProcess],
) -> FlowSummaryDTO:
    bonita_process_id = definition.process_id
    bonita_process_name = None
    bonita_version = None
    disponible = False

    if bonita_process_id:
        process = processes_by_id.get(bonita_process_id)
        if process is not None:
            disponible = True
            bonita_process_name = process.name
            bonita_version = process.version
        else:
            # Intento de resolución adicional en caso de que la lista inicial no contuviera el proceso
            matching = [
                p for p in processes if p.id == bonita_process_id or p.name == bonita_process_id
            ]
            if matching:
                process = matching[0]
                disponible = True
                bonita_process_name = process.name
                bonita_version = process.version
    else:
        try:
            resolved_id = resolve_process_id_for_flow(slug, processes)
        except FlowProcessResolutionError:
            resolved_id = None
        if resolved_id:
            bonita_process_id = resolved_id
            process = processes_by_id.get(resolved_id)
            if process:
                disponible = True
                bonita_process_name = process.name
                bonita_version = process.version

    metadata = {}
    if definition.metadata:
        metadata.update(definition.metadata)  # type: ignore[arg-type]
    if bonita_process_id:
        metadata.setdefault("bonita_process_id", bonita_process_id)

    return FlowSummaryDTO.model_validate(
        {
            "slug": slug,
            "display_name": definition.display_name,
            "disponible": disponible,
            "bonita_process_id": bonita_process_id,
            "bonita_process_name": bonita_process_name,
            "bonita_version": bonita_version,
            "metadata": metadata,
        }
    )

