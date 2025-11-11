from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, RootModel

from ...domain.contratos.entities import (
    ContractCase,
    ContractCaseVariable,
    ContractCaseWithVariables,
    ContractProcess,
    ContractTask,
    StartProcessResult,
)


class ContractProcessDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    display_name: str = Field(alias="displayName")
    version: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class StartProcessPayloadDTO(RootModel[Dict[str, Any]]):
    """
    Representa los datos arbitrarios del contrato que se enviarán a Bonita.
    """


class StartProcessResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    case_id: str = Field(alias="caseId")
    process_definition_id: str = Field(alias="processDefinitionId")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ContractTaskDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    display_name: str = Field(alias="displayName")
    state: str
    assigned_id: Optional[str] = Field(default=None, alias="assignedId")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AssignTaskPayloadDTO(BaseModel):
    user_id: str = Field(..., description="Identificador del usuario que reclama la tarea")


class CompleteTaskPayloadDTO(BaseModel):
    contract_inputs: Dict[str, Any] = Field(
        default_factory=dict,
        description="Payload del contrato esperado por el formulario",
    )
    variables: Dict[str, Any] = Field(
        default_factory=dict,
        description="Variables legacy en formato name/value",
    )


class ContractCaseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    process_definition_id: str = Field(alias="processDefinitionId")
    state: str
    started_by: Optional[str] = Field(default=None, alias="startedBy")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ContractCaseVariableDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    value: Any
    id: Optional[str] = None
    case_id: Optional[str] = Field(default=None, alias="caseId")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ContractCaseWithVariablesDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    case: ContractCaseDTO
    variables: List[ContractCaseVariableDTO] = Field(default_factory=list)


def to_contract_process_dto(entity: ContractProcess) -> ContractProcessDTO:
    return ContractProcessDTO.model_validate(
        {
            "id": entity.id,
            "name": entity.name,
            "displayName": entity.display_name,
            "version": entity.version,
            "metadata": entity.metadata,
        }
    )


def to_start_process_response_dto(entity: StartProcessResult) -> StartProcessResponseDTO:
    return StartProcessResponseDTO.model_validate(
        {
            "caseId": entity.case_id,
            "processDefinitionId": entity.process_definition_id,
            "metadata": entity.metadata,
        }
    )


def to_contract_task_dto(entity: ContractTask) -> ContractTaskDTO:
    return ContractTaskDTO.model_validate(
        {
            "id": entity.id,
            "name": entity.name,
            "displayName": entity.display_name,
            "state": entity.state,
            "assignedId": entity.assigned_id,
            "metadata": entity.metadata,
        }
    )


def to_contract_case_dto(entity: ContractCase) -> ContractCaseDTO:
    return ContractCaseDTO.model_validate(
        {
            "id": entity.id,
            "processDefinitionId": entity.process_definition_id,
            "state": entity.state,
            "startedBy": entity.started_by,
            "metadata": entity.metadata,
        }
    )


def to_contract_case_variable_dto(
    entity: ContractCaseVariable,
) -> ContractCaseVariableDTO:
    return ContractCaseVariableDTO.model_validate(
        {
            "id": entity.id,
            "caseId": entity.case_id,
            "name": entity.name,
            "value": entity.value,
            "metadata": entity.metadata,
        }
    )


def to_contract_case_with_variables_dto(
    entity: ContractCaseWithVariables,
) -> ContractCaseWithVariablesDTO:
    return ContractCaseWithVariablesDTO.model_validate(
        {
            "case": to_contract_case_dto(entity.case),
            "variables": [
                to_contract_case_variable_dto(variable) for variable in entity.variables
            ],
        }
    )


