from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from .api.routers.contratos import router as contratos_router
from .dependencies import get_bonita_client


app = FastAPI(
    title="Integración Python-Bonita",
    description="API de referencia para interactuar con Bonita BPM desde una aplicación FastAPI.",
    version="0.1.0",
)

templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
async def startup_event() -> None:
    client = get_bonita_client()
    if not client.is_session_active:
        client.login()


@app.on_event("shutdown")
async def shutdown_event() -> None:
    client = get_bonita_client()
    client.logout()


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})


app.include_router(contratos_router, prefix="/api")


