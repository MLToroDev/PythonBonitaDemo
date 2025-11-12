from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError

from .config import get_settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

_WWW_AUTHENTICATE_BEARER = {"WWW-Authenticate": "Bearer"}


def create_access_token(
    subject: str,
    *,
    expires_delta: timedelta | None = None,
    additional_claims: Dict[str, Any] | None = None,
) -> str:
    """
    Genera un JWT firmado con los parámetros configurados en la aplicación.
    """
    settings = get_settings()
    to_encode: Dict[str, Any] = {"sub": subject}
    if additional_claims:
        to_encode.update(additional_claims)

    expire_delta = expires_delta or timedelta(
        minutes=settings.access_token_expire_minutes
    )
    expire = datetime.now(timezone.utc) + expire_delta
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.jwt_algorithm)


def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    """
    Valida el JWT recibido y retorna el identificador del usuario (username).
    """
    settings = get_settings()
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales.",
        headers=_WWW_AUTHENTICATE_BEARER,
    )

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token ha expirado. Por favor, autentícate nuevamente.",
            headers=_WWW_AUTHENTICATE_BEARER,
        ) from None
    except JWTError:
        raise credentials_exception from None

    username: str | None = payload.get("sub")
    if username is None or not isinstance(username, str):
        raise credentials_exception
    return username

