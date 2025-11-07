# Integración Python con Bonita BPM

Este proyecto ofrece una demostración completa de cómo integrar una aplicación Python (FastAPI) con Bonita Studio Community empleando la API REST oficial. El objetivo es servir como **Prueba de Concepto (PoC)** para mostrar cómo un sistema externo puede autenticarse, descubrir procesos, instanciar casos y gestionar tareas humanas dentro de Bonita.

## 🧱 Arquitectura

```
.
├── app
│   ├── api
│   │   └── routes.py          # Endpoints expuestos por FastAPI
│   ├── models
│   │   └── schemas.py         # Modelos Pydantic (requests/responses)
│   ├── services
│   │   └── bonita_client.py   # Cliente HTTP con la lógica de negocio
│   ├── config.py              # Carga de variables de entorno
│   ├── dependencies.py        # Inyección simple de BonitaClient
│   └── main.py                # Punto de entrada FastAPI
├── templates
│   └── index.html             # UI mínima para probar la API
├── env.example                # Ejemplo de configuración (.env)
├── requirements.txt           # Dependencias del proyecto
└── Dockerfile                 # Contenedor opcional de despliegue
```

## ⚙️ Configuración Inicial

1. **Clona el repositorio y crea un entorno virtual**

   ```powershell
   cd C:\Users\Mateo\Documents\PythonBonitaDemo
   python -m venv venv
   .\venv\Scripts\activate
   ```

2. **Instala las dependencias**

   ```powershell
   pip install -r requirements.txt
   ```

3. **Configura las variables de entorno**

   Copia `env.example` a `.env` y ajusta los valores según tu instalación de Bonita:

   ```powershell
   Copy-Item env.example .env
   ```

   Variables disponibles:

   - `BONITA_URL`: URL base del portal (ej. `http://localhost:8080/bonita`)
   - `BONITA_USER`: Usuario con permisos para los procesos (ej. `walter.bates`)
   - `BONITA_PASSWORD`: Contraseña del usuario

## 🚀 Puesta en Marcha

1. **Inicia la aplicación FastAPI**

   ```powershell
   uvicorn app.main:app --reload
   ```

2. **Explora la documentación interactiva**

   - Swagger UI: http://localhost:8000/docs
   - Redoc: http://localhost:8000/redoc

3. **Usa la UI incluida (estilo Bonita)**

   - Visita http://localhost:8000 para acceder al panel HTML inspirado en la Bonita User Application.
   - Desde allí puedes:
     - Listar procesos desplegados.
     - Instanciar un proceso con variables.
     - Consultar y completar tareas humanas.
     - Revisar el estado y variables de un caso.

## 📡 Endpoints Principales

- `GET /api/bonita/processes` — Lista de definiciones de procesos disponibles.
- `POST /api/bonita/processes/{process_id}/start` — Instancia un nuevo caso.
- `GET /api/bonita/tasks` — Consulta tareas humanas según estado/usuario.
- `POST /api/bonita/tasks/{task_id}/assign` — Reclama una tarea indicando el `user_id`.
- `POST /api/bonita/tasks/{task_id}/complete` — Completa una tarea enviando variables del formulario.
- `GET /api/bonita/cases/{case_id}` — Obtiene el estado del caso y variables asociadas.

## 🧪 Flujo de Demo Sugerido

1. Autenticarse (automático en el arranque de la app).
2. Listar procesos (`GET /api/bonita/processes`).
3. Instanciar un proceso con datos de entrada (`POST /processes/{id}/start`).
4. Verificar el nuevo caso en el Portal de Bonita.
5. Obtener tareas humanas listas (`GET /api/bonita/tasks?state=ready`).
6. Reclamar y completar la tarea envíando el payload esperado.
7. Consultar el caso para validar la evolución del proceso.

## 🐳 Despliegue con Docker (Opcional)

```bash
docker build -t bonita-python-demo .
docker run --rm -p 8000:8000 --env-file .env bonita-python-demo
```

Asegúrate de que el contenedor pueda alcanzar la instancia de Bonita (ej. usando `host.docker.internal` en Windows/Mac).

## ✅ Requisitos Previos

- Bonita Studio Community 7.4+ en ejecución (o Bonita Runtime standalone).
- Python 3.10+ instalado.
- Acceso a un usuario de Bonita con permisos en los procesos del ejemplo.

## 📚 Recursos Adicionales

- [Documentación oficial de Bonita REST API](https://documentation.bonitasoft.com)
- [FastAPI](https://fastapi.tiangolo.com/) — Framework usado para la API Python.
- [requests](https://docs.python-requests.org/) — Cliente HTTP utilizado bajo el capó.

---

Con esta base puedes extender la PoC para integrar Bonita con microservicios, aplicaciones web o scripts de automatización, centralizando la lógica en `BonitaClient` y exponiendo las operaciones que necesites desde FastAPI.
