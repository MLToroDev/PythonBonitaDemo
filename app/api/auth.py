from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.config import get_settings
from app.core.session_cache import set_session
from app.infrastructure.bonita.client import (
    BonitaAuthenticationError,
    BonitaClient,
)
from app.security import create_access_token

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    settings = get_settings()
    client = BonitaClient(
        base_url=settings.bonita_url,
        username=form_data.username,
        password=form_data.password,
    )

    try:
        client.login()
    except BonitaAuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales de Bonita inválidas.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    set_session(form_data.username, client)

    access_token = create_access_token(
        form_data.username,
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    return {"access_token": access_token, "token_type": "bearer"}

