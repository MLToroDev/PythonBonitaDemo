from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response, status

from ...dependencies import get_bonita_client, get_contratos_service
from ...domain.contratos.services import ContratosService
from ...infrastructure.bonita.client import BonitaClient
from ..dto.contratos import (
    CompleteTaskPayloadDTO,
    ContractTaskDTO,
    to_contract_task_dto,
)


router = APIRouter(prefix="/tareas", tags=["Tareas"])


@router.get("/pendientes", response_model=List[ContractTaskDTO])
async def list_pending_tasks(
    service: ContratosService = Depends(get_contratos_service),
    client: BonitaClient = Depends(get_bonita_client),
) -> List[ContractTaskDTO]:
    session_info = client.get_session_info()
    user_id = _extract_user_id(session_info)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="No fue posible determinar el usuario autenticado en Bonita.",
        )

    tasks = service.listar_tareas(state="ready", user_id=user_id)
    return [to_contract_task_dto(task) for task in tasks]


@router.post(
    "/{task_id}/completar",
    response_class=Response,
)
async def complete_task(
    task_id: str,
    payload: CompleteTaskPayloadDTO,
    service: ContratosService = Depends(get_contratos_service),
) -> None:
    service.completar_tarea(
        task_id=task_id,
        contract_inputs=payload.contract_inputs or None,
        variables=payload.variables or None,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def _extract_user_id(session_info: dict) -> str | None:
    candidates = [
        "user_id",
        "userId",
        "userID",
        "user",
    ]
    for key in candidates:
        value = session_info.get(key)
        if value is not None:
            return str(value)
    # Algunos entornos exponen el identificador dentro de un sub-objeto.
    user_subinfo = session_info.get("user_info") or session_info.get("user")
    if isinstance(user_subinfo, dict):
        for key in ("id", "ID"):
            value = user_subinfo.get(key)
            if value is not None:
                return str(value)
    return None

