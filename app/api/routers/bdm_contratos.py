"""
Routers REST para Contratos.
Endpoints que reemplazan el acceso al BDM de Bonita.
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.contrato_service import ContratoService
from app.schemas.bdm_schemas import (
    Contrato as ContratoSchema,
    ContratoCreate,
    ContratoUpdate,
    ContratoConRelaciones
)

router = APIRouter(
    prefix="/bdm/contratos",
    tags=["BDM - Contratos"],
    responses={404: {"description": "No encontrado"}},
)


def get_contrato_service(db: Session = Depends(get_db)) -> ContratoService:
    """Dependency para obtener el servicio de contratos."""
    return ContratoService(db)


@router.get("", response_model=List[ContratoSchema])
async def listar_contratos(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    numero_contrato: Optional[str] = Query(None, description="Filtrar por número de contrato"),
    service: ContratoService = Depends(get_contrato_service)
):
    """
    Listar contratos con paginación y filtros opcionales.
    
    Reemplaza el acceso directo al BDM de Bonita.
    """
    return service.get_contratos(
        skip=skip,
        limit=limit,
        estado=estado,
        numero_contrato=numero_contrato
    )


@router.get("/usuario/{id_usuario_bonita}", response_model=List[ContratoSchema])
async def listar_contratos_por_usuario(
    id_usuario_bonita: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: ContratoService = Depends(get_contrato_service)
):
    """
    Listar contratos por ID de usuario de Bonita.
    
    Equivalente a la query findByUsuarioBonita del BDM.
    """
    return service.get_contratos_by_usuario_bonita(
        id_usuario_bonita=id_usuario_bonita,
        skip=skip,
        limit=limit
    )


@router.get("/{contrato_id}", response_model=ContratoSchema)
async def obtener_contrato(
    contrato_id: UUID,
    service: ContratoService = Depends(get_contrato_service)
):
    """
    Obtener un contrato por ID.
    """
    contrato = service.get_contrato(contrato_id)
    if not contrato:
        raise HTTPException(status_code=404, detail="Contrato no encontrado")
    return contrato


@router.get("/{contrato_id}/completo", response_model=ContratoConRelaciones)
async def obtener_contrato_completo(
    contrato_id: UUID,
    service: ContratoService = Depends(get_contrato_service)
):
    """
    Obtener un contrato con todas sus relaciones (perfil, informes, obligaciones).
    """
    contrato = service.get_contrato_with_relations(contrato_id)
    if not contrato:
        raise HTTPException(status_code=404, detail="Contrato no encontrado")
    return contrato


@router.post("", response_model=ContratoSchema, status_code=201)
async def crear_contrato(
    contrato_in: ContratoCreate,
    service: ContratoService = Depends(get_contrato_service)
):
    """
    Crear un nuevo contrato.
    
    Valida que existan las relaciones requeridas (perfil contratista y contrato marco).
    """
    try:
        return service.create_contrato(contrato_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{contrato_id}", response_model=ContratoSchema)
async def actualizar_contrato(
    contrato_id: UUID,
    contrato_in: ContratoUpdate,
    service: ContratoService = Depends(get_contrato_service)
):
    """
    Actualizar un contrato existente.
    """
    try:
        contrato = service.update_contrato(contrato_id, contrato_in)
        if not contrato:
            raise HTTPException(status_code=404, detail="Contrato no encontrado")
        return contrato
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{contrato_id}", status_code=204)
async def eliminar_contrato(
    contrato_id: UUID,
    service: ContratoService = Depends(get_contrato_service)
):
    """
    Eliminar un contrato.
    """
    if not service.delete_contrato(contrato_id):
        raise HTTPException(status_code=404, detail="Contrato no encontrado")
    return None


@router.get("/count/total", response_model=dict)
async def contar_contratos(
    estado: Optional[str] = Query(None),
    numero_contrato: Optional[str] = Query(None),
    service: ContratoService = Depends(get_contrato_service)
):
    """
    Contar contratos con filtros opcionales.
    """
    total = service.count_contratos(estado=estado, numero_contrato=numero_contrato)
    return {"total": total}

