from fastapi import Depends, HTTPException, status

from .core.session_cache import get_session, remove_session
from .domain.contratos.services import ContratosService
from .infrastructure.bonita.client import (
    BonitaAuthenticationError,
    BonitaClient,
    BonitaClientError,
)
from .infrastructure.bonita.contratos_repository import BonitaContratosRepository
from .security import get_current_user


def _unauthorized_session_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Sesión de Bonita no encontrada o expirada. Vuelve a iniciar sesión.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_bonita_client(
    current_user: str = Depends(get_current_user),
) -> BonitaClient:
    """
    Devuelve un cliente autenticado en Bonita reutilizando la sesión almacenada.
    """
    client = get_session(current_user)
    if client is None:
        raise _unauthorized_session_exception()

    if not client.is_session_active:
        try:
            client.login()
        except BonitaAuthenticationError as exc:
            remove_session(current_user)
            raise _unauthorized_session_exception() from exc

    try:
        client.get_session_info()
    except BonitaAuthenticationError as exc:
        remove_session(current_user)
        raise _unauthorized_session_exception() from exc
    except BonitaClientError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "message": "Error al validar la sesión de Bonita.",
                "details": exc.details,
            },
        ) from exc

    return client


def get_contratos_service(
    client: BonitaClient = Depends(get_bonita_client),
) -> ContratosService:
    """
    Resuelve la implementación de ContratosService utilizando el repositorio de Bonita.
    """
    repository = BonitaContratosRepository(client=client)
    return ContratosService(repository=repository)

