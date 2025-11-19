# Integración Python con Bonita BPM

Este proyecto ofrece una demostración completa de cómo integrar una aplicación Python (FastAPI) con Bonita Studio Community empleando la API REST oficial. El objetivo es servir como **Prueba de Concepto (PoC)** para mostrar cómo un sistema externo puede autenticarse, descubrir procesos, instanciar casos y gestionar tareas humanas dentro de Bonita.

## 🧱 Arquitectura

```
.
├── app
│   ├── api
│   │   ├── dto                # DTOs Pydantic
│   │   └── routers            # Endpoints FastAPI
│   │       ├── bdm_contratos.py    # Servicio Puente - Contratos
│   │       └── bdm_informes.py     # Servicio Puente - Informes
│   ├── domain                 # Lógica de negocio por dominios
│   ├── infrastructure         # Integraciones concretas (Bonita)
│   ├── models                 # Modelos SQLAlchemy (BDM)
│   ├── schemas                # Schemas Pydantic (validación)
│   ├── repositories           # Repositorios de acceso a datos
│   ├── services               # Servicios de lógica de negocio
│   ├── config.py              # Carga de variables de entorno
│   ├── database.py            # Configuración PostgreSQL
│   ├── dependencies.py        # Inyección de servicios/repositorios
│   └── main.py                # Punto de entrada FastAPI
├── alembic                    # Migraciones de base de datos
├── scripts                    # Scripts de utilidad
├── docs                       # Documentación del proyecto
│   └── SERVICIO_PUENTE.md     # Documentación del Servicio Puente
├── templates                  # UI mínima para probar la API
├── env.example                # Ejemplo de configuración (.env)
├── requirements.txt           # Dependencias del proyecto
└── Dockerfile                 # Contenedor opcional de despliegue
```

### 🎯 Servicio Puente (Nuevo)

El proyecto ahora incluye un **Servicio Puente** que reemplaza completamente el BDM de Bonita:

- ✅ **Modelos SQLAlchemy** - Representación de tablas en PostgreSQL
- ✅ **Schemas Pydantic** - Validación y serialización
- ✅ **Repositorios** - Acceso aislado a datos
- ✅ **Servicios** - Lógica de negocio
- ✅ **Routers REST** - Endpoints limpios y documentados

**Ver documentación completa**: [docs/SERVICIO_PUENTE.md](docs/SERVICIO_PUENTE.md)

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

   Copia `env.example` a `.env` y ajusta los valores según tu instalación:

   ```powershell
   Copy-Item env.example .env
   ```

   Variables disponibles:

   - `BONITA_URL`: URL base del portal (ej. `http://localhost:8080/bonita`)
   - `DATABASE_URL`: URL de conexión a PostgreSQL (ej. `postgresql://user:pass@localhost:5432/nombre_bd`)
   - `DATABASE_SCHEMA`: Nombre del esquema donde se crearán las tablas (por defecto: `bdm`)
   - `DEBUG`: Modo debug (True/False)

4. **Configura PostgreSQL (para el Servicio Puente)**

   ```powershell
   # Opción A: Crear una nueva base de datos
   createdb bonita_bridge
   
   # Opción B: Usar una base de datos existente
   # Las tablas se crearán en un esquema (por defecto: 'bdm')
   ```

5. **Inicializa el esquema y las tablas**

   ```powershell
   # Opción A: Script directo (crea el esquema automáticamente)
   python scripts/init_db.py
   
   # Opción B: Usando Alembic (recomendado para producción)
   alembic revision --autogenerate -m "Initial migration"
   alembic upgrade head
   ```

   **Nota**: El script creará automáticamente el esquema especificado en `DATABASE_SCHEMA` (por defecto: `bdm`) si no existe. Puedes usar una base de datos existente y las tablas se crearán en el esquema configurado.

## 🚀 Puesta en Marcha

1. **Inicia la aplicación FastAPI**

   ```powershell
   uvicorn app.main:app --reload
   ```

2. **Explora la documentación interactiva**

   - Swagger UI: http://localhost:8000/docs
   - Redoc: http://localhost:8000/redoc

3. **Autenticación por solicitud (HTTP Basic)**

   Cada petición a `/api/bonita/*` debe incluir credenciales válidas de Bonita usando **HTTP Basic Auth**. La aplicación no almacena usuarios en `.env`; toma el usuario/contraseña de los encabezados de la petición. Así puedes probar con distintos perfiles:

   - Usuario: `walter.bates`
   - Contraseña: `bpm`

4. **Usa la UI incluida (estilo Bonita)**

   - Visita http://localhost:8000 para acceder al panel HTML inspirado en la Bonita User Application.
   - Desde allí puedes:
     - Listar procesos desplegados.
     - Instanciar un proceso con variables.
     - Consultar y completar tareas humanas.
     - Revisar el estado y variables de un caso.

## 📡 Endpoints Principales

### Integración con Bonita BPM

- `GET /api/bonita/processes` — Lista de definiciones de procesos disponibles.
- `POST /api/bonita/processes/{process_id}/start` — Instancia un nuevo caso.
- `GET /api/bonita/tasks` — Consulta tareas humanas según estado/usuario.
- `POST /api/bonita/tasks/{task_id}/assign` — Reclama una tarea indicando el `user_id`.
- `POST /api/bonita/tasks/{task_id}/complete` — Completa una tarea enviando variables del formulario.
- `GET /api/bonita/cases/{case_id}` — Obtiene el estado del caso y variables asociadas.

### Servicio Puente (Reemplazo del BDM)

- `GET /api/bdm/contratos` — Listar contratos
- `GET /api/bdm/contratos/{id}` — Obtener contrato
- `GET /api/bdm/contratos/usuario/{id_usuario_bonita}` — Contratos por usuario Bonita
- `POST /api/bdm/contratos` — Crear contrato
- `PUT /api/bdm/contratos/{id}` — Actualizar contrato
- `DELETE /api/bdm/contratos/{id}` — Eliminar contrato
- `GET /api/bdm/informes` — Listar informes
- `GET /api/bdm/informes/contrato/{contrato_id}` — Informes por contrato
- `POST /api/bdm/informes` — Crear informe

**Ver todos los endpoints en**: http://localhost:8000/docs

## 🧪 Flujo de Demo Sugerido

1. Autenticarse enviando credenciales HTTP Basic por petición.
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
