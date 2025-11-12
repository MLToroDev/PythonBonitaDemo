from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from .api.routers.contratos import router as contratos_router


app = FastAPI(
    title="Integración Python-Bonita",
    description="API de referencia para interactuar con Bonita BPM desde una aplicación FastAPI.",
    version="0.1.0",
)

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})


app.include_router(contratos_router, prefix="/api")


