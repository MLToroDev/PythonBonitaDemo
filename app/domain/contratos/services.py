from __future__ import annotations

from typing import Iterable

from .entities import (
    ContractCase,
    ContractCaseVariable,
    ContractCaseWithVariables,
    ContractProcess,
    ContractTask,
    StartProcessResult,
)
from .repositories import ContratosRepository


class ContratosService:
    """
    Coordina la lógica de negocio del dominio de contratos y orquesta los repositorios.
    """

    def __init__(self, repository: ContratosRepository) -> None:
        self._repository = repository

    def listar_procesos(
        self, *, page: int = 0, count: int = 10, sort: str | None = None
    ) -> Iterable[ContractProcess]:
        return self._repository.listar_procesos(page=page, count=count, sort=sort)

    def iniciar_proceso(
        self, process_id: str, *, contract_inputs: dict | None = None
    ) -> StartProcessResult:
        return self._repository.iniciar_proceso(
            process_id, contract_inputs=contract_inputs
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
        return self._repository.listar_tareas(
            state=state,
            page=page,
            count=count,
            user_id=user_id,
            process_id=process_id,
            sort=sort,
        )

    def asignar_tarea(self, task_id: str, user_id: str) -> None:
        self._repository.asignar_tarea(task_id, user_id)

    def completar_tarea(
        self,
        task_id: str,
        *,
        contract_inputs: dict | None = None,
        variables: dict | None = None,
    ) -> None:
        self._repository.completar_tarea(
            task_id, contract_inputs=contract_inputs, variables=variables
        )

    def obtener_caso(self, case_id: str) -> ContractCase:
        return self._repository.obtener_caso(case_id)

    def obtener_variables_caso(
        self, case_id: str, *, page: int = 0, count: int = 50
    ) -> Iterable[ContractCaseVariable]:
        return self._repository.obtener_variables_caso(
            case_id, page=page, count=count
        )

    def obtener_caso_con_variables(
        self, case_id: str, *, include_variables: bool = True
    ) -> ContractCaseWithVariables:
        if include_variables:
            return self._repository.obtener_caso_con_variables(
                case_id, include_variables=True
            )
        case = self._repository.obtener_caso(case_id)
        return ContractCaseWithVariables(case=case, variables=[])


