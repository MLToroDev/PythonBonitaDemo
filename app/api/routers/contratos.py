from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ...dependencies import get_contratos_service
from ...domain.contratos.services import ContratosService
from ...infrastructure.bonita.client import BonitaClientError
from ..dto.contratos import (
    AssignTaskPayloadDTO,
    CompleteTaskPayloadDTO,
    ContractCaseWithVariablesDTO,
    ContractProcessDTO,
    ContractTaskDTO,
    StartProcessPayloadDTO,
    StartProcessResponseDTO,
    to_contract_case_with_variables_dto,
    to_contract_process_dto,
    to_contract_task_dto,
    to_start_process_response_dto,
)


router = APIRouter(prefix="/bonita", tags=["Bonita"])


def _handle_bonita_error(exc: BonitaClientError) -> None:
    detail = {"message": str(exc)}
    status_code = status.HTTP_502_BAD_GATEWAY
    if hasattr(exc, "details") and exc.details:
        detail["details"] = exc.details
        raw_status = exc.details.get("status_code")
        if isinstance(raw_status, int) and 100 <= raw_status < 600:
            status_code = raw_status
    raise HTTPException(status_code=status_code, detail=detail) from exc


@router.get("/processes", response_model=List[ContractProcessDTO])
async def list_processes(
    page: int = Query(default=0, ge=0),
    count: int = Query(default=10, ge=1, le=100),
    sort: Optional[str] = Query(
        default=None, description="Formato esperado: campo ASC|DESC"
    ),
    service: ContratosService = Depends(get_contratos_service),
) -> List[ContractProcessDTO]:
    try:
        processes = service.listar_procesos(page=page, count=count, sort=sort)
        return [to_contract_process_dto(proc) for proc in processes]
    except BonitaClientError as exc:
        _handle_bonita_error(exc)


@router.post(
    "/processes/{process_id}/start",
    response_model=StartProcessResponseDTO,
    status_code=status.HTTP_201_CREATED,
)
async def start_process_instance(
    process_id: str,
    payload: StartProcessPayloadDTO,
    service: ContratosService = Depends(get_contratos_service),
) -> StartProcessResponseDTO:
    try:
        contract_inputs = payload.root or None
        response = service.iniciar_proceso(
            process_id=process_id, contract_inputs=contract_inputs
        )
        return to_start_process_response_dto(response)
    except BonitaClientError as exc:
        _handle_bonita_error(exc)


@router.get("/tasks", response_model=List[ContractTaskDTO])
async def list_tasks(
    state: Optional[str] = Query(default="ready"),
    page: int = Query(default=0, ge=0),
    count: int = Query(default=10, ge=1, le=100),
    user_id: Optional[str] = Query(default=None),
    process_id: Optional[str] = Query(default=None),
    sort: Optional[str] = Query(
        default=None,
        description="Formato: campo ASC|DESC",
    ),
    service: ContratosService = Depends(get_contratos_service),
) -> List[ContractTaskDTO]:
    try:
        tasks = service.listar_tareas(
            state=state,
            page=page,
            count=count,
            user_id=user_id,
            process_id=process_id,
            sort=sort,
        )
        return [to_contract_task_dto(task) for task in tasks]
    except BonitaClientError as exc:
        _handle_bonita_error(exc)


@router.post("/tasks/{task_id}/assign", status_code=status.HTTP_204_NO_CONTENT)
async def assign_task(
    task_id: str,
    payload: AssignTaskPayloadDTO,
    service: ContratosService = Depends(get_contratos_service),
) -> None:
    try:
        service.asignar_tarea(task_id=task_id, user_id=payload.user_id)
    except BonitaClientError as exc:
        _handle_bonita_error(exc)


@router.post("/tasks/{task_id}/complete", status_code=status.HTTP_204_NO_CONTENT)
async def complete_task(
    task_id: str,
    payload: CompleteTaskPayloadDTO,
    service: ContratosService = Depends(get_contratos_service),
) -> None:
    try:
        service.completar_tarea(
            task_id=task_id,
            contract_inputs=payload.contract_inputs or None,
            variables=payload.variables or None,
        )
    except BonitaClientError as exc:
        _handle_bonita_error(exc)


@router.get("/cases/{case_id}", response_model=ContractCaseWithVariablesDTO)
async def get_case(
    case_id: str,
    include_variables: bool = Query(default=True),
    service: ContratosService = Depends(get_contratos_service),
) -> ContractCaseWithVariablesDTO:
    try:
        case = service.obtener_caso_con_variables(
            case_id=case_id, include_variables=include_variables
        )
        return to_contract_case_with_variables_dto(case)
    except BonitaClientError as exc:
        _handle_bonita_error(exc)


