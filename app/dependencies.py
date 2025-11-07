from functools import lru_cache

from .config import get_settings
from .services.bonita_client import BonitaClient


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


