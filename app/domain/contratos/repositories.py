from __future__ import annotations

from typing import Iterable, Protocol

from .entities import (
    ContractCase,
    ContractCaseVariable,
    ContractProcess,
    ContractTask,
    ContractCaseWithVariables,
    StartProcessResult,
)


class ContratosRepository(Protocol):
    """
    Define las operaciones que el dominio de contratos necesita sin depender de Bonita.
    """

    def listar_procesos(
        self, *, page: int = 0, count: int = 10, sort: str | None = None
    ) -> Iterable[ContractProcess]:
        ...

    def iniciar_proceso(
        self, process_id: str, *, contract_inputs: dict | None = None
    ) -> StartProcessResult:
        ...

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
        ...

    def asignar_tarea(self, task_id: str, user_id: str) -> None:
        ...

    def completar_tarea(
        self,
        task_id: str,
        *,
        contract_inputs: dict | None = None,
        variables: dict | None = None,
    ) -> None:
        ...

    def obtener_caso(self, case_id: str) -> ContractCase:
        ...

    def obtener_variables_caso(
        self, case_id: str, *, page: int = 0, count: int = 50
    ) -> Iterable[ContractCaseVariable]:
        ...

    def obtener_caso_con_variables(
        self, case_id: str, *, include_variables: bool = True
    ) -> ContractCaseWithVariables:
        ...


