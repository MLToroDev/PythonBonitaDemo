"""
Repositorios para acceso a datos.
"""
from app.repositories.base import BaseRepository
from app.repositories.contrato_repository import ContratoRepository
from app.repositories.informe_repository import InformeRepository

__all__ = [
    "BaseRepository",
    "ContratoRepository",
    "InformeRepository",
]

