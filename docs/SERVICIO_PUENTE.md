# Servicio Puente - Arquitectura Limpia con FastAPI

## 🎯 Objetivo

El Servicio Puente es un backend independiente basado en FastAPI que **reemplaza completamente** la capa de datos del BDM de Bonita, permitiendo desacoplar el frontend, el backend y el motor BPM.

## 🏗️ Arquitectura

```
Frontend (Vue/React/PHP)
        |
Servicio Puente (FastAPI)
        |------ PostgreSQL (Modelo Central)
        |
    Bonita BPM (Solo flujos, tareas y estados)
```

### Capas de la Arquitectura

1. **Modelos SQLAlchemy** (`app/models/bdm_models.py`)
   - Representación de las tablas en PostgreSQL
   - Basados en el BDM de Bonita original

2. **Schemas Pydantic** (`app/schemas/bdm_schemas.py`)
   - Contratos de entrada/salida
   - Validación y serialización automática

3. **Repositorios** (`app/repositories/`)
   - Acceso aislado a la base de datos
   - Consultas personalizadas (equivalente a queries del BDM)

4. **Servicios** (`app/services/`)
   - Lógica de negocio
   - Validación de reglas de dominio

5. **Routers** (`app/api/routers/bdm_*.py`)
   - Endpoints REST limpios
   - Documentación automática con OpenAPI

## 📦 Instalación

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar variables de entorno

Copiar `env.example` a `.env` y configurar:

```bash
cp env.example .env
```

Editar `.env` con tus credenciales:

```env
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/nombre_bd
DATABASE_SCHEMA=bdm
DEBUG=False
```

**Nota importante**: `DATABASE_URL` puede apuntar a una base de datos existente. Las tablas se crearán en el esquema especificado por `DATABASE_SCHEMA` (por defecto: `bdm`). El esquema se creará automáticamente si no existe.

### 3. Crear la base de datos (si no existe)

```bash
# Opción A: Crear una nueva base de datos
createdb bonita_bridge

# Opción B: Usar una base de datos existente
# Solo asegúrate de que el usuario tenga permisos para crear esquemas
```

### 4. Inicializar el esquema y las tablas

**Opción A: Usando el script de inicialización**

```bash
python scripts/init_db.py
```

Este script:
- Crea el esquema especificado en `DATABASE_SCHEMA` si no existe
- Crea todas las tablas dentro del esquema

**Opción B: Usando Alembic (recomendado para producción)**

```bash
# Crear migración inicial
alembic revision --autogenerate -m "Initial migration"

# Aplicar migraciones
alembic upgrade head
```

**Nota**: Alembic también creará el esquema automáticamente si está configurado correctamente.

## 🚀 Uso

### Iniciar el servidor

```bash
uvicorn app.main:app --reload
```

El servidor estará disponible en `http://localhost:8000`

### Documentación automática

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📡 Endpoints Disponibles

### Contratos

- `GET /api/bdm/contratos` - Listar contratos
- `GET /api/bdm/contratos/{id}` - Obtener contrato por ID
- `GET /api/bdm/contratos/{id}/completo` - Obtener contrato con relaciones
- `GET /api/bdm/contratos/usuario/{id_usuario_bonita}` - Contratos por usuario Bonita
- `POST /api/bdm/contratos` - Crear contrato
- `PUT /api/bdm/contratos/{id}` - Actualizar contrato
- `DELETE /api/bdm/contratos/{id}` - Eliminar contrato
- `GET /api/bdm/contratos/count/total` - Contar contratos

### Informes

- `GET /api/bdm/informes` - Listar informes
- `GET /api/bdm/informes/{id}` - Obtener informe por ID
- `GET /api/bdm/informes/{id}/completo` - Obtener informe con relaciones
- `GET /api/bdm/informes/contrato/{contrato_id}` - Informes por contrato
- `GET /api/bdm/informes/periodo/{anio}` - Informes por período
- `POST /api/bdm/informes` - Crear informe
- `PUT /api/bdm/informes/{id}` - Actualizar informe
- `DELETE /api/bdm/informes/{id}` - Eliminar informe
- `GET /api/bdm/informes/count/total` - Contar informes

## 🔄 Migraciones

### Crear una nueva migración

```bash
alembic revision --autogenerate -m "Descripción del cambio"
```

### Aplicar migraciones

```bash
alembic upgrade head
```

### Revertir migración

```bash
alembic downgrade -1
```

## 📊 Modelo de Datos

El modelo está basado en el BDM de Bonita original:

- **PerfilContratista** - Perfil del contratista
- **ContratoInterAdministrativo** - Contratos marco
- **Componente** - Componentes de contratos marco
- **ObjetivoContrato** - Objetivos de componentes
- **EvidenciaContrato** - Evidencias
- **Contrato** - Contratos específicos
- **Obligacion** - Obligaciones de contratos
- **Informe** - Informes de ejecución
- **Ejecucion** - Ejecuciones de obligaciones
- **DescripcionEjecucion** - Descripciones de ejecuciones

## 🔐 Seguridad

El servicio incluye:

- Validación automática con Pydantic
- Manejo de errores estructurado
- Validación de relaciones (foreign keys)
- Paginación en todas las listas

**Nota**: Para producción, agregar:
- Autenticación JWT
- Autorización por roles
- Rate limiting
- CORS configurado
- HTTPS

## 🧪 Pruebas

### Ejemplo de uso con curl

```bash
# Listar contratos
curl http://localhost:8000/api/bdm/contratos

# Crear contrato
curl -X POST http://localhost:8000/api/bdm/contratos \
  -H "Content-Type: application/json" \
  -d '{
    "numero_contrato": "CT-001",
    "perfil_contratista_id": "uuid-del-perfil",
    "padre_id": "uuid-del-contrato-marco"
  }'

# Obtener contratos por usuario Bonita
curl http://localhost:8000/api/bdm/contratos/usuario/USER-123
```

## 🔗 Integración con Bonita

Bonita puede consumir estos endpoints en lugar del BDM:

1. **En procesos BPM**: Usar REST API calls para consultar/crear datos
2. **En formularios**: Consumir endpoints desde JavaScript
3. **En conectores**: Usar HTTP connectors para sincronizar datos

### Ejemplo: Consultar contratos desde Bonita

```groovy
// En un script de Bonita
def response = new URL("http://servicio-puente:8000/api/bdm/contratos/usuario/${apiAccessor.identityAPI.getCurrentUser().id}").text
def contratos = new groovy.json.JsonSlurper().parseText(response)
```

## 📝 Notas Importantes

1. **UUIDs**: Todos los IDs son UUIDs (no Long como en Bonita BDM)
2. **Relaciones**: Se validan automáticamente al crear/actualizar
3. **Cascadas**: Las eliminaciones respetan las relaciones (CASCADE, RESTRICT)
4. **Índices**: Se crean automáticamente para campos comunes (estado, número_contrato, etc.)

## 🛠️ Extensión

Para agregar nuevas entidades:

1. Crear modelo en `app/models/bdm_models.py`
2. Crear schemas en `app/schemas/bdm_schemas.py`
3. Crear repositorio en `app/repositories/` (opcional, si necesita queries personalizadas)
4. Crear servicio en `app/services/`
5. Crear router en `app/api/routers/bdm_*.py`
6. Registrar router en `app/main.py`

## 📚 Referencias

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)

