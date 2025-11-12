from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, Iterable, Optional

from app.config import get_settings
from app.domain.contratos.entities import ContractProcess


class FlowNotDefinedError(KeyError):
    """Se lanza cuando no existe un flujo configurado con el slug solicitado."""


class FlowProcessResolutionError(RuntimeError):
    """Se lanza cuando no se pudo resolver el proceso de Bonita para un flujo."""


@dataclass(frozen=True)
class FlowDefinition:
    slug: str
    display_name: str
    process_id: Optional[str] = None
    process_name: Optional[str] = None
    process_version: Optional[str] = None
    metadata: Dict[str, object] | None = None

    def matches_process(self, process: ContractProcess) -> bool:
        """
        Determina si un proceso de Bonita coincide con la definición.
        """
        name_matches = True
        version_matches = True

        if self.process_name:
            name_matches = process.name == self.process_name or (
                process.display_name == self.process_name
            )
        if self.process_version:
            version_matches = process.version == self.process_version

        return name_matches and version_matches


@lru_cache
def get_defined_flows() -> Dict[str, FlowDefinition]:
    """
    Convierte la configuración cruda en objetos FlowDefinition reutilizables.
    """
    settings = get_settings()
    parsed: Dict[str, FlowDefinition] = {}
    for slug, raw_definition in settings.flow_definitions.items():
        if not isinstance(raw_definition, dict):
            raise RuntimeError(
                f"Configuración inválida para el flujo '{slug}': se esperaba un objeto."
            )
        display_name = str(
            raw_definition.get("display_name")
            or raw_definition.get("name")
            or raw_definition.get("title")
            or slug.replace("-", " ").title()
        )
        parsed[slug] = FlowDefinition(
            slug=slug,
            display_name=display_name,
            process_id=_cast_optional_str(raw_definition.get("process_id")),
            process_name=_cast_optional_str(raw_definition.get("process_name")),
            process_version=_cast_optional_str(raw_definition.get("process_version")),
            metadata=raw_definition.get("metadata")
            if isinstance(raw_definition.get("metadata"), dict)
            else None,
        )
    return parsed


def resolve_process_id_for_flow(
    flow_slug: str, processes: Iterable[ContractProcess]
) -> str:
    """
    Determina el process_id de Bonita que corresponde al flujo solicitado.
    """
    flow_definition = get_defined_flows().get(flow_slug)
    if flow_definition is None:
        raise FlowNotDefinedError(flow_slug)

    if flow_definition.process_id:
        return flow_definition.process_id

    # Se recorre la lista de procesos buscando coincidencias por nombre y versión.
    matching_processes = [
        process
        for process in processes
        if flow_definition.matches_process(process)
    ]

    if not matching_processes:
        raise FlowProcessResolutionError(
            f"No se encontró un proceso en Bonita asociado al flujo '{flow_slug}'."
        )

    if len(matching_processes) > 1:
        raise FlowProcessResolutionError(
            f"Se encontraron múltiples procesos para el flujo '{flow_slug}'. "
            "Especifica process_id o process_version en la configuración."
        )

    return matching_processes[0].id


def _cast_optional_str(value: object) -> Optional[str]:
    if value is None:
        return None
    value_str = str(value).strip()
    return value_str or None

