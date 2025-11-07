import logging
from typing import Any, Dict, List, Optional, Sequence, Tuple

import requests
from requests import Session
from requests.exceptions import HTTPError, RequestException


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class BonitaClientError(Exception):
    """Error genérico de la integración con Bonita."""


class BonitaAuthenticationError(BonitaClientError):
    """Se lanza cuando la autenticación con Bonita falla."""


class BonitaClient:
    """
    Cliente ligero para interactuar con la API REST de Bonita.
    Maneja autenticación, token CSRF y operaciones comunes de BPM.
    """

    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
        session: Optional[Session] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.session = session or requests.Session()
        self.csrf_token: Optional[str] = None
        self._logged_in: bool = False

        # Cabeceras base para todas las peticiones
        self.session.headers.update(
            {
                "Accept": "application/json",
            }
        )

    @property
    def is_session_active(self) -> bool:
        return self._logged_in and "JSESSIONID" in self.session.cookies

    def login(self) -> None:
        """
        Autentica contra Bonita, almacena la cookie de sesión y el token CSRF.
        """
        login_url = f"{self.base_url}/loginservice"
        payload = {
            "username": self.username,
            "password": self.password,
            "redirect": "false",
        }

        try:
            response = self.session.post(login_url, data=payload, timeout=10)
            response.raise_for_status()
        except HTTPError as exc:
            logger.error("Error de autenticación en Bonita: %s", exc)
            raise BonitaAuthenticationError(
                "Credenciales inválidas o error de autenticación."
            ) from exc
        except RequestException as exc:
            logger.error("Fallo de red al autenticarse en Bonita: %s", exc)
            raise BonitaAuthenticationError(
                "No se pudo acceder al servicio de Bonita."
            ) from exc

        self._update_csrf_token()
        self._logged_in = True
        logger.info("Autenticación correcta en Bonita y token CSRF almacenado.")

    def logout(self) -> None:
        """
        Cierra la sesión activa en Bonita.
        """
        if not self.is_session_active:
            return

        logout_url = f"{self.base_url}/logoutservice"
        try:
            response = self.session.get(
                logout_url, timeout=10, params={"redirect": "false"}
            )
            response.raise_for_status()
            logger.info("Sesión cerrada en Bonita.")
        except RequestException as exc:
            logger.warning("No fue posible cerrar la sesión en Bonita: %s", exc)
        finally:
            self.session.cookies.clear()
            self._logged_in = False
            self.csrf_token = None

    def get_processes(
        self, page: int = 0, count: int = 10, sort: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        params: List[Tuple[str, Any]] = [("p", page), ("c", count)]
        if sort:
            params.append(("o", sort))
        return self._request("get", "/API/bpm/process", params=params)

    def start_process(
        self,
        process_id: str,
        contract_inputs: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        payload = contract_inputs or {}
        return self._request(
            "post",
            f"/API/bpm/process/{process_id}/instantiation",
            json=payload,
        )
    def get_tasks(
        self,
        state: Optional[str] = "ready",
        page: int = 0,
        count: int = 10,
        user_id: Optional[str] = None,
        process_id: Optional[str] = None,
        sort: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        params: List[Tuple[str, Any]] = [("p", page), ("c", count)]
        if sort:
            params.append(("o", sort))
        if state:
            params.append(("f", f"state={state}"))
        if user_id:
            params.append(("f", f"assigned_id={user_id}"))
        if process_id:
            params.append(("f", f"processId={process_id}"))
        return self._request("get", "/API/bpm/userTask", params=params)

    def assign_task(self, task_id: str, user_id: str) -> Dict[str, Any]:
        payload = {"assigned_id": user_id}
        return self._request("put", f"/API/bpm/userTask/{task_id}", json=payload)

    def complete_task(
        self,
        task_id: str,
        contract_inputs: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"state": "completed"}
        if contract_inputs:
            payload["contractInputs"] = contract_inputs
        return self._request(
            "post",
            f"/API/bpm/userTask/{task_id}/execution",
            json=payload,
        )

    def get_case(self, case_id: str) -> Dict[str, Any]:
        return self._request("get", f"/API/bpm/case/{case_id}")

    def get_case_variables(
        self, case_id: str, page: int = 0, count: int = 50
    ) -> List[Dict[str, Any]]:
        params: List[Tuple[str, Any]] = [
            ("p", page),
            ("c", count),
            ("f", f"case_id={case_id}"),
        ]
        return self._request("get", "/API/bpm/caseVariable", params=params)

    def _update_csrf_token(self) -> None:
        if "X-Bonita-API-Token" in self.session.cookies:
            self.csrf_token = self.session.cookies["X-Bonita-API-Token"]
            self.session.headers.update({"X-Bonita-API-Token": self.csrf_token})
        else:
            logger.warning(
                "Autenticación completada pero no se encontró el token CSRF. Las operaciones de escritura podrían fallar."
            )

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Sequence[Tuple[str, Any]]] = None,
        json: Optional[Dict[str, Any]] = None,
        *,
        _retry: bool = True,
    ) -> Any:
        if not self.is_session_active:
            logger.info(
                "Sesión de Bonita inactiva. Reintentando login antes de la petición %s %s",
                method.upper(),
                endpoint,
            )
            self.login()

        url = f"{self.base_url}{endpoint}"

        try:
            response = self.session.request(
                method=method.upper(),
                url=url,
                params=params,
                json=json,
                timeout=15,
            )
            response.raise_for_status()
            if response.content:
                return response.json()
            return {}
        except HTTPError as exc:
            if exc.response is not None and exc.response.status_code == 401 and _retry:
                logger.info(
                    "Sesión expirada. Reintentando autenticación y repitiendo la petición %s %s.",
                    method.upper(),
                    endpoint,
                )
                self.login()
                return self._request(
                    method=method,
                    endpoint=endpoint,
                    params=params,
                    json=json,
                    _retry=False,
                )
            status_code = exc.response.status_code if exc.response else "desconocido"
            message = exc.response.text if exc.response else str(exc)
            logger.error(
                "Bonita devolvió un error HTTP en %s %s [%s]: %s",
                method.upper(),
                endpoint,
                status_code,
                message,
            )
            raise BonitaClientError(
                f"Error al comunicarse con Bonita (HTTP {status_code})."
            ) from exc
        except RequestException as exc:
            logger.error(
                "Error de red en la petición %s %s: %s", method.upper(), endpoint, exc
            )
            raise BonitaClientError("Error de red al comunicarse con Bonita.") from exc

    @staticmethod
    def _format_variables_payload(variables: Dict[str, Any]) -> List[Dict[str, Any]]:
        formatted: List[Dict[str, Any]] = []
        for name, value in variables.items():
            formatted.append({"name": name, "value": value})
        return formatted
