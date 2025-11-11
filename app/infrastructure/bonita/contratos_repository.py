from __future__ import annotations

from typing import Iterable, List, Optional

from ...domain.contratos.entities import (
    ContractCase,
    ContractCaseVariable,
    ContractCaseWithVariables,
    ContractProcess,
    ContractTask,
    StartProcessResult,
)
from ...domain.contratos.repositories import ContratosRepository
from .client import BonitaClient, BonitaClientError


class BonitaContratosRepository(ContratosRepository):
    """
    Implementación del repositorio que utiliza la API REST de Bonita.
    """

    def __init__(self, client: BonitaClient) -> None:
        self._client = client

    def listar_procesos(
        self, *, page: int = 0, count: int = 10, sort: str | None = None
    ) -> Iterable[ContractProcess]:
        procesos_raw = self._client.get_processes(page=page, count=count, sort=sort)
        return [self._map_process(proc) for proc in procesos_raw]

    def iniciar_proceso(
        self, process_id: str, *, contract_inputs: dict | None = None
    ) -> StartProcessResult:
        resultado = self._client.start_process(
            process_id=process_id, contract_inputs=contract_inputs
        )
        return StartProcessResult(
            case_id=str(resultado.get("caseId", "")),
            process_definition_id=str(resultado.get("processDefinitionId", "")),
            metadata=resultado,
        )

    def listar_tareas(
        self,
        *,
        state: str | None = "ready",
        page: int = 0,
        count: int = 10,
        user_id: str | None = None,
        process_id: str | None = None,
        sort: str | None = None,
    ) -> Iterable[ContractTask]:
        tareas_raw = self._client.get_tasks(
            state=state,
            page=page,
            count=count,
            user_id=user_id,
            process_id=process_id,
            sort=sort,
        )
        return [self._map_task(task) for task in tareas_raw]

    def asignar_tarea(self, task_id: str, user_id: str) -> None:
        self._client.assign_task(task_id=task_id, user_id=user_id)

    def completar_tarea(
        self,
        task_id: str,
        *,
        contract_inputs: dict | None = None,
        variables: dict | None = None,
    ) -> None:
        self._client.complete_task(
            task_id=task_id, contract_inputs=contract_inputs, variables=variables
        )

    def obtener_caso(self, case_id: str) -> ContractCase:
        caso_raw = self._client.get_case(case_id)
        return self._map_case(caso_raw)

    def obtener_variables_caso(
        self, case_id: str, *, page: int = 0, count: int = 50
    ) -> Iterable[ContractCaseVariable]:
        variables_raw = self._client.get_case_variables(
            case_id, page=page, count=count
        )
        return [self._map_case_variable(var) for var in variables_raw]

    def obtener_caso_con_variables(
        self, case_id: str, *, include_variables: bool = True
    ) -> ContractCaseWithVariables:
        case = self.obtener_caso(case_id)
        variables: List[ContractCaseVariable] = []
        if include_variables:
            variables = list(self.obtener_variables_caso(case_id))
        return ContractCaseWithVariables(case=case, variables=variables)

    @staticmethod
    def _map_process(data: dict) -> ContractProcess:
        return ContractProcess(
            id=str(data.get("id", "")),
            name=data.get("name", ""),
            display_name=data.get("displayName", data.get("display_name", "")),
            version=data.get("version", ""),
            metadata=data,
        )

    @staticmethod
    def _map_task(data: dict) -> ContractTask:
        return ContractTask(
            id=str(data.get("id", "")),
            name=data.get("name", ""),
            display_name=data.get("displayName", data.get("display_name", "")),
            state=data.get("state", ""),
            assigned_id=data.get("assigned_id") or data.get("assignedId"),
            metadata=data,
        )

    @staticmethod
    def _map_case(data: dict) -> ContractCase:
        return ContractCase(
            id=str(data.get("id", "")),
            process_definition_id=str(data.get("processDefinitionId", "")),
            state=data.get("state", ""),
            started_by=data.get("started_by") or data.get("startedBy"),
            metadata=data,
        )

    @staticmethod
    def _map_case_variable(data: dict) -> ContractCaseVariable:
        return ContractCaseVariable(
            id=str(data.get("id")) if data.get("id") is not None else None,
            case_id=str(data.get("case_id"))
            if data.get("case_id") is not None
            else data.get("caseId"),
            name=data.get("name", ""),
            value=data.get("value"),
            metadata=data,
        )


