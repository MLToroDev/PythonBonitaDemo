from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ..dependencies import get_bonita_client
from ..models.schemas import (
    AssignTaskPayload,
    CaseDetails,
    CaseVariable,
    CaseWithVariables,
    CompleteTaskPayload,
    ProcessDefinition,
    StartProcessPayload,
    StartProcessResponse,
    Task,
)
from ..services.bonita_client import BonitaClient, BonitaClientError


router = APIRouter(prefix="/bonita", tags=["Bonita"])


def _handle_bonita_error(exc: BonitaClientError) -> None:
    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail=f"Error comunicándose con Bonita: {exc}",
    ) from exc


@router.get("/processes", response_model=List[ProcessDefinition])
async def list_processes(
    page: int = Query(default=0, ge=0),
    count: int = Query(default=10, ge=1, le=100),
    sort: Optional[str] = Query(
        default=None, description="Formato esperado: campo ASC|DESC"
    ),
    client: BonitaClient = Depends(get_bonita_client),
) -> List[ProcessDefinition]:
    try:
        processes = client.get_processes(page=page, count=count, sort=sort)
        return processes
    except BonitaClientError as exc:
        _handle_bonita_error(exc)


@router.post(
    "/processes/{process_id}/start",
    response_model=StartProcessResponse,
    status_code=status.HTTP_201_CREATED,
)
async def start_process_instance(
    process_id: str,
    payload: StartProcessPayload,
    client: BonitaClient = Depends(get_bonita_client),
) -> StartProcessResponse:
    try:
        contract_inputs = payload.root
        response = client.start_process(
            process_id=process_id,
            contract_inputs=contract_inputs or None,
        )
        return response
    except BonitaClientError as exc:
        _handle_bonita_error(exc)


@router.get("/tasks", response_model=List[Task])
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
    client: BonitaClient = Depends(get_bonita_client),
) -> List[Task]:
    try:
        tasks = client.get_tasks(
            state=state,
            page=page,
            count=count,
            user_id=user_id,
            process_id=process_id,
            sort=sort,
        )
        return tasks
    except BonitaClientError as exc:
        _handle_bonita_error(exc)


@router.post("/tasks/{task_id}/assign")
async def assign_task(
    task_id: str,
    payload: AssignTaskPayload,
    client: BonitaClient = Depends(get_bonita_client),
) -> dict:
    try:
        return client.assign_task(task_id=task_id, user_id=payload.user_id)
    except BonitaClientError as exc:
        _handle_bonita_error(exc)


@router.post("/tasks/{task_id}/complete")
async def complete_task(
    task_id: str,
    payload: CompleteTaskPayload,
    client: BonitaClient = Depends(get_bonita_client),
) -> dict:
    try:
        return client.complete_task(
            task_id=task_id,
            contract_inputs=payload.contract_inputs or None,
        )
    except BonitaClientError as exc:
        _handle_bonita_error(exc)


@router.get("/cases/{case_id}", response_model=CaseWithVariables)
async def get_case(
    case_id: str,
    include_variables: bool = Query(default=True),
    client: BonitaClient = Depends(get_bonita_client),
) -> CaseWithVariables:
    try:
        case_data = client.get_case(case_id)
        variables: List[CaseVariable] = []
        if include_variables:
            variables_raw = client.get_case_variables(case_id)
            variables = [CaseVariable(**item) for item in variables_raw]

        case = CaseDetails(**case_data)
        return CaseWithVariables(case=case, variables=variables)
    except BonitaClientError as exc:
        _handle_bonita_error(exc)


