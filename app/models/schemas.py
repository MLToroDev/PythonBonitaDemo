from typing import Any, Dict, List, Optional

from pydantic import AliasChoices, BaseModel, Field, RootModel


class ProcessDefinition(BaseModel):
    id: str
    name: str
    displayName: str
    version: str

    class Config:
        extra = "allow"


class StartProcessPayload(RootModel[Dict[str, Any]]):
    """
    Representa los datos de contrato que se enviarán a Bonita al instanciar
    un proceso. Se permite cualquier estructura JSON.
    """
    pass


class StartProcessResponse(BaseModel):
    caseId: str
    processDefinitionId: str

    class Config:
        extra = "allow"


class Task(BaseModel):
    id: str
    name: str
    displayName: str
    state: str
    assigned_id: Optional[str] = None

    class Config:
        extra = "allow"


class AssignTaskPayload(BaseModel):
    user_id: str = Field(..., description="Identificador numérico del usuario al que se asignará la tarea")


class CompleteTaskPayload(BaseModel):
    contract_inputs: Dict[str, Any] = Field(
        default_factory=dict,
        description="Datos del contrato a enviar al completar la tarea",
    )


class CaseDetails(BaseModel):
    id: str
    processDefinitionId: str
    state: str
    started_by: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("started_by", "startedBy"),
        serialization_alias="started_by",
    )

    class Config:
        extra = "allow"


class CaseVariable(BaseModel):
    id: Optional[str] = None
    case_id: Optional[str] = None
    name: str
    value: Any

    class Config:
        extra = "allow"


class CaseWithVariables(BaseModel):
    case: CaseDetails
    variables: List[CaseVariable] = Field(default_factory=list)

