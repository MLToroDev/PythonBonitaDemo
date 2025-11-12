import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    bonita_url: str
    secret_key: str
    jwt_algorithm: str
    access_token_expire_minutes: int


def _get_env_variable(key: str, *, default: str | None = None) -> str:
    value = os.getenv(key, default)
    if value is None or value.strip() == "":
        raise RuntimeError(f"Falta la variable de entorno requerida: {key}")
    return value


@lru_cache
def get_settings() -> Settings:
    """
    Lee la configuración necesaria para conectarse a Bonita desde variables
    de entorno y la retorna como un objeto inmutable.
    """
    access_token_expire_minutes_raw = _get_env_variable(
        "ACCESS_TOKEN_EXPIRE_MINUTES", default="30"
    )
    try:
        access_token_expire_minutes = int(access_token_expire_minutes_raw)
    except ValueError as exc:
        raise RuntimeError(
            "La variable ACCESS_TOKEN_EXPIRE_MINUTES debe ser un entero."
        ) from exc

    return Settings(
        bonita_url=_get_env_variable("BONITA_URL"),
        secret_key=_get_env_variable("SECRET_KEY"),
        jwt_algorithm=_get_env_variable("JWT_ALGORITHM", default="HS256"),
        access_token_expire_minutes=access_token_expire_minutes,
    )


