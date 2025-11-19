"""
Routers REST para Informes.
Endpoints que reemplazan el acceso al BDM de Bonita.
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.informe_service import InformeService
from app.schemas.bdm_schemas import (
    Informe as InformeSchema,
    InformeCreate,
    InformeUpdate,
    InformeConRelaciones
)

router = APIRouter(
    prefix="/bdm/informes",
    tags=["BDM - Informes"],
    responses={404: {"description": "No encontrado"}},
)


def get_informe_service(db: Session = Depends(get_db)) -> InformeService:
    """Dependency para obtener el servicio de informes."""
    return InformeService(db)


@router.get("", response_model=List[InformeSchema])
async def listar_informes(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    anio: Optional[int] = Query(None, description="Filtrar por año"),
    mes: Optional[int] = Query(None, ge=1, le=12, description="Filtrar por mes"),
    service: InformeService = Depends(get_informe_service)
):
    """
    Listar informes con paginación y filtros opcionales.
    
    Reemplaza el acceso directo al BDM de Bonita.
    """
    return service.get_informes(
        skip=skip,
        limit=limit,
        estado=estado,
        anio=anio,
        mes=mes
    )


@router.get("/contrato/{contrato_id}", response_model=List[InformeSchema])
async def listar_informes_por_contrato(
    contrato_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: InformeService = Depends(get_informe_service)
):
    """
    Listar informes por ID de contrato.
    
    Equivalente a la query findByContratoId del BDM.
    """
    return service.get_informes_by_contrato_id(
        contrato_id=contrato_id,
        skip=skip,
        limit=limit
    )


@router.get("/periodo/{anio}", response_model=List[InformeSchema])
async def listar_informes_por_periodo(
    anio: int,
    mes: Optional[int] = Query(None, ge=1, le=12, description="Filtrar por mes"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: InformeService = Depends(get_informe_service)
):
    """
    Listar informes por período (año y opcionalmente mes).
    """
    return service.get_informes_by_periodo(
        anio=anio,
        mes=mes,
        skip=skip,
        limit=limit
    )


@router.get("/{informe_id}", response_model=InformeSchema)
async def obtener_informe(
    informe_id: UUID,
    service: InformeService = Depends(get_informe_service)
):
    """
    Obtener un informe por ID.
    """
    informe = service.get_informe(informe_id)
    if not informe:
        raise HTTPException(status_code=404, detail="Informe no encontrado")
    return informe


@router.get("/{informe_id}/completo", response_model=InformeConRelaciones)
async def obtener_informe_completo(
    informe_id: UUID,
    service: InformeService = Depends(get_informe_service)
):
    """
    Obtener un informe con todas sus relaciones (contrato, ejecuciones, descripciones).
    """
    informe = service.get_informe_with_relations(informe_id)
    if not informe:
        raise HTTPException(status_code=404, detail="Informe no encontrado")
    return informe


@router.post("", response_model=InformeSchema, status_code=201)
async def crear_informe(
    informe_in: InformeCreate,
    service: InformeService = Depends(get_informe_service)
):
    """
    Crear un nuevo informe.
    
    Valida que exista el contrato asociado.
    """
    try:
        return service.create_informe(informe_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{informe_id}", response_model=InformeSchema)
async def actualizar_informe(
    informe_id: UUID,
    informe_in: InformeUpdate,
    service: InformeService = Depends(get_informe_service)
):
    """
    Actualizar un informe existente.
    """
    try:
        informe = service.update_informe(informe_id, informe_in)
        if not informe:
            raise HTTPException(status_code=404, detail="Informe no encontrado")
        return informe
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{informe_id}", status_code=204)
async def eliminar_informe(
    informe_id: UUID,
    service: InformeService = Depends(get_informe_service)
):
    """
    Eliminar un informe.
    """
    if not service.delete_informe(informe_id):
        raise HTTPException(status_code=404, detail="Informe no encontrado")
    return None


@router.get("/count/total", response_model=dict)
async def contar_informes(
    estado: Optional[str] = Query(None),
    anio: Optional[int] = Query(None),
    mes: Optional[int] = Query(None, ge=1, le=12),
    service: InformeService = Depends(get_informe_service)
):
    """
    Contar informes con filtros opcionales.
    """
    total = service.count_informes(estado=estado, anio=anio, mes=mes)
    return {"total": total}

