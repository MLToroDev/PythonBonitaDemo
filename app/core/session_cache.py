from __future__ import annotations

from threading import Lock
from typing import Dict, Optional

from app.infrastructure.bonita.client import BonitaClient

_lock = Lock()
_active_bonita_sessions: Dict[str, BonitaClient] = {}


def set_session(username: str, client: BonitaClient) -> None:
    """
    Almacena o reemplaza la sesión activa de Bonita asociada a un usuario.
    """
    with _lock:
        _active_bonita_sessions[username] = client


def get_session(username: str) -> Optional[BonitaClient]:
    """
    Recupera la sesión activa de Bonita asociada a un usuario.
    """
    with _lock:
        return _active_bonita_sessions.get(username)


def remove_session(username: str) -> Optional[BonitaClient]:
    """
    Elimina y retorna la sesión activa asociada a un usuario, si existe.
    """
    with _lock:
        return _active_bonita_sessions.pop(username, None)

