from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from .api.auth import router as auth_router
from .api.routers.casos import router as casos_router
from .api.routers.flujos import router as flujos_router
from .api.routers.procesos import router as procesos_router
from .api.routers.tareas import router as tareas_router
from .api.routers.bdm_contratos import router as bdm_contratos_router
from .api.routers.bdm_informes import router as bdm_informes_router


app = FastAPI(
    title="Integración Python-Bonita",
    description="API de referencia para interactuar con Bonita BPM desde una aplicación FastAPI.",
    version="0.1.0",
)

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})


app.include_router(auth_router, prefix="/api")
app.include_router(procesos_router, prefix="/api")
app.include_router(flujos_router, prefix="/api")
app.include_router(tareas_router, prefix="/api")
app.include_router(casos_router, prefix="/api")
# Servicio Puente - Endpoints que reemplazan el BDM
app.include_router(bdm_contratos_router, prefix="/api")
app.include_router(bdm_informes_router, prefix="/api")


