from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from ...dependencies import get_contratos_service
from ...domain.contratos.services import ContratosService
from ...infrastructure.bonita.client import BonitaClientError
from ..dto.contratos import (
    ContractCaseWithVariablesDTO,
    to_contract_case_with_variables_dto,
)


router = APIRouter(prefix="/casos", tags=["Casos"])


@router.get("/{case_id}", response_model=ContractCaseWithVariablesDTO)
async def get_case_details(
    case_id: str,
    include_variables: bool = Query(default=True),
    service: ContratosService = Depends(get_contratos_service),
) -> ContractCaseWithVariablesDTO:
    try:
        case = service.obtener_caso_con_variables(
            case_id=case_id,
            include_variables=include_variables,
        )
        return to_contract_case_with_variables_dto(case)
    except BonitaClientError as exc:
        raise _map_bonita_error(exc) from exc


def _map_bonita_error(exc: BonitaClientError):
    status_code = exc.details.get("status_code") if exc.details else None
    if isinstance(status_code, int) and 100 <= status_code < 600:
        detail = {
            "message": str(exc),
            "details": exc.details,
        }
        from fastapi import HTTPException

        raise HTTPException(status_code=status_code, detail=detail)
    from fastapi import HTTPException

    raise HTTPException(
        status_code=502,
        detail={
            "message": "Error al comunicarse con Bonita.",
            "details": exc.details,
        },
    )

