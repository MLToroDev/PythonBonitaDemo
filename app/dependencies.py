from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from .config import get_settings
from .domain.contratos.services import ContratosService
from .infrastructure.bonita.client import BonitaClient
from .infrastructure.bonita.contratos_repository import BonitaContratosRepository

security = HTTPBasic(auto_error=False)


@dataclass(frozen=True)
class BonitaCredentials:
    username: str
    password: str


def get_bonita_credentials(
    credentials: HTTPBasicCredentials | None = Depends(security),
) -> BonitaCredentials:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Se requieren credenciales Basic de Bonita.",
            headers={"WWW-Authenticate": "Basic"},
        )
    if not credentials.username or not credentials.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales de Bonita inválidas.",
            headers={"WWW-Authenticate": "Basic"},
        )
    return BonitaCredentials(
        username=credentials.username,
        password=credentials.password,
    )


def get_bonita_client(
    bonita_credentials: BonitaCredentials = Depends(get_bonita_credentials),
) -> BonitaClient:
    """
    Devuelve un cliente autenticado en Bonita usando las credenciales
    recibidas en la cabecera HTTP Basic Auth.
    """
    settings = get_settings()
    client = BonitaClient(
        base_url=settings.bonita_url,
        username=bonita_credentials.username,
        password=bonita_credentials.password,
    )
    client.login()
    return client


def get_contratos_service(
    client: BonitaClient = Depends(get_bonita_client),
) -> ContratosService:
    """
    Resuelve la implementación de ContratosService utilizando el repositorio de Bonita.
    """
    repository = BonitaContratosRepository(client=client)
    return ContratosService(repository=repository)

