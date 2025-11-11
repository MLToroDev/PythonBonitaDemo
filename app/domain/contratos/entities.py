from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(slots=True)
class ContractProcess:
    id: str
    name: str
    display_name: str
    version: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class StartProcessResult:
    case_id: str
    process_definition_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ContractTask:
    id: str
    name: str
    display_name: str
    state: str
    assigned_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ContractCase:
    id: str
    process_definition_id: str
    state: str
    started_by: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ContractCaseVariable:
    name: str
    value: Any
    id: Optional[str] = None
    case_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ContractCaseWithVariables:
    case: ContractCase
    variables: List[ContractCaseVariable] = field(default_factory=list)


