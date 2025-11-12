import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    bonita_url: str


def _get_env_variable(key: str) -> str:
    value = os.getenv(key)
    if value is None or value.strip() == "":
        raise RuntimeError(f"Falta la variable de entorno requerida: {key}")
    return value


@lru_cache
def get_settings() -> Settings:
    """
    Lee la configuración necesaria para conectarse a Bonita desde variables
    de entorno y la retorna como un objeto inmutable.
    """
    return Settings(bonita_url=_get_env_variable("BONITA_URL"))


