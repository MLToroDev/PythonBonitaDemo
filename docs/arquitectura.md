# Arquitectura de la Integración FastAPI ↔ Bonita BPM

Este documento resume la organización del proyecto tras la refactorización hacia una arquitectura inspirada en DDD y el patrón repositorio. El objetivo es mantener una separación clara entre la lógica de negocio, la infraestructura Bonita y la capa de aplicación (FastAPI).

## Capas principales

- **Aplicación (`app/api`)**  
  Expone endpoints HTTP con FastAPI. Cada router depende de servicios de dominio y traduce las entidades del dominio a DTO Pydantic.

- **Dominio (`app/domain`)**  
  Contiene entidades puras, servicios de negocio y contratos de repositorios. No conoce detalles de Bonita ni de FastAPI.

- **Infraestructura (`app/infrastructure`)**  
  Implementa los repositorios concretos que hablan con la API REST de Bonita usando `BonitaClient`.

- **Configuración (`app/config.py`, `app/dependencies.py`, `app/main.py`)**  
  Resuelve las dependencias y centraliza la obtención de credenciales vía HTTP Basic por petición.

## Flujo de una petición típica

1. **Router HTTP** (`app/api/routers/contratos.py`) recibe la solicitud y valida DTOs de entrada.
2. **Servicio de dominio** (`app/domain/contratos/services.py`) ejecuta la lógica principal y coordina repositorios.
3. **Repositorio Bonita** (`app/infrastructure/bonita/contratos_repository.py`) se comunica con Bonita a través de `BonitaClient`, autenticado con las credenciales recibidas.
4. **Entidades de dominio** se transforman en DTOs de salida.
5. **FastAPI** responde con JSON consistente para los consumidores externos (p.ej., frontends Laravel).

## Directorios clave

- `app/api/dto/contratos.py`: DTOs Pydantic y funciones de mapeo desde entidades de dominio.
- `app/api/routers/contratos.py`: Endpoints HTTP para procesos, tareas y casos.
- `app/domain/contratos/entities.py`: Modelos ricos del dominio (contratos, tareas, casos).
- `app/domain/contratos/repositories.py`: Contratos que definen qué necesita el dominio.
- `app/domain/contratos/services.py`: Lógica de negocio reutilizable y testeable.
- `app/infrastructure/bonita/client.py`: Cliente HTTP reutilizable para autenticación y llamadas a Bonita.
- `app/infrastructure/bonita/contratos_repository.py`: Implementación del repositorio usando `BonitaClient`.
- `app/dependencies.py`: Resolución de `ContratosService` y `BonitaClient` por petición según las credenciales HTTP Basic.
- `app/main.py`: Registro de router y plantilla inicial.

## Beneficios obtenidos

- **Aislamiento** de la lógica de negocio respecto a Bonita. Se pueden crear repositorios alternativos (memoria, mocks, otras fuentes).
- **Testabilidad**: los servicios de dominio aceptan un repositorio que implementa el protocolo `ContratosRepository`, facilitando pruebas unitarias sin tocar Bonita.
- **Escalabilidad**: nuevos dominios se implementan duplicando la estructura `app/domain/<dominio>` y `app/infrastructure/bonita/<dominio>`.
- **DTOs explícitos**: FastAPI documenta contratos HTTP sin exponer estructuras crudas de Bonita.
- **Credenciales dinámicas**: cada petición puede autenticarse con un usuario distinto de Bonita vía HTTP Basic, evitando credenciales “quemadas” en `.env`.

## Próximos pasos sugeridos

- Añadir tests unitarios para `ContratosService` usando repositorios falsos.
- Documentar casos de uso específicos (p.ej., payloads por proceso) en subcarpetas de `docs/`.
- Extender la estructura a otros dominios (ej. `domain/solicitudes`) reutilizando el mismo patrón.


