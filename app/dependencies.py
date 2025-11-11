from functools import lru_cache

from .config import get_settings
from .domain.contratos.services import ContratosService
from .infrastructure.bonita.client import BonitaClient
from .infrastructure.bonita.contratos_repository import BonitaContratosRepository


@lru_cache
def _get_bonita_client_singleton() -> BonitaClient:
    settings = get_settings()
    client = BonitaClient(
        base_url=settings.bonita_url,
        username=settings.bonita_user,
        password=settings.bonita_password,
    )
    client.login()
    return client


def get_bonita_client() -> BonitaClient:
    """
    Devuelve una instancia única de BonitaClient ya autenticada.
    En caso de que se haya invalidado la sesión, intenta autenticarse nuevamente.
    """
    client = _get_bonita_client_singleton()
    if not client.is_session_active:
        client.login()
    return client


@lru_cache
def get_contratos_service() -> ContratosService:
    """
    Resuelve la implementación de ContratosService utilizando el repositorio de Bonita.
    """
    client = get_bonita_client()
    repository = BonitaContratosRepository(client=client)
    return ContratosService(repository=repository)

