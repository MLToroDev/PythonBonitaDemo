# 📊 Contexto Completo: Integración con PostgreSQL

## 🎯 Objetivo General

Reemplazar completamente el BDM (Business Data Model) de Bonita con un **Servicio Puente** basado en FastAPI que utiliza PostgreSQL como base de datos central, permitiendo:

- ✅ Desacoplar el frontend y backend del motor BPM de Bonita
- ✅ Usar PostgreSQL en lugar de H2 (limitado en Bonita Studio)
- ✅ Implementar arquitectura limpia y escalable
- ✅ Centralizar los datos de la organización en una base de datos real

---

## 🏗️ Arquitectura de la Integración

```
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE PRESENTACIÓN                      │
│  Frontend (Vue/React/PHP) → API REST (FastAPI)             │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE APLICACIÓN                       │
│  Routers (FastAPI) → Services → Repositories               │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE DOMINIO                          │
│  Schemas (Pydantic) → Models (SQLAlchemy)                   │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                  CAPA DE INFRAESTRUCTURA                    │
│  SQLAlchemy Engine → psycopg2 → PostgreSQL                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Estructura de Archivos

```
PythonBonitaDemo/
├── app/
│   ├── config.py              # Configuración centralizada
│   ├── database.py            # Configuración de SQLAlchemy y conexión
│   ├── models/
│   │   └── bdm_models.py      # Modelos SQLAlchemy (10 entidades)
│   ├── schemas/
│   │   └── bdm_schemas.py     # Schemas Pydantic (validación)
│   ├── repositories/
│   │   ├── base.py            # Repositorio base genérico
│   │   ├── contrato_repository.py
│   │   └── informe_repository.py
│   ├── services/
│   │   ├── contrato_service.py
│   │   └── informe_service.py
│   └── api/routers/
│       ├── bdm_contratos.py   # Endpoints REST para Contratos
│       └── bdm_informes.py    # Endpoints REST para Informes
├── alembic/                   # Sistema de migraciones
│   ├── env.py
│   └── versions/
├── scripts/
│   ├── init_db.py             # Script de inicialización
│   └── test_connection.py     # Script de diagnóstico
└── .env                       # Variables de entorno
```

---

## ⚙️ Componentes Principales

### 1. **Configuración (`app/config.py`)**

**Responsabilidad**: Cargar y validar variables de entorno.

```python
@dataclass(frozen=True)
class Settings:
    database_url: str          # URL de conexión PostgreSQL
    database_schema: str       # Nombre del esquema (default: "SeguimientoDAP")
    debug: bool                # Modo debug
    # ... otras configuraciones
```

**Variables de entorno requeridas**:
- `DATABASE_URL`: `postgresql://usuario:contraseña@host:puerto/nombre_bd`
- `DATABASE_SCHEMA`: Nombre del esquema (default: `SeguimientoDAP`)
- `DEBUG`: `True`/`False` para logging SQL

**Características**:
- ✅ Carga con codificación UTF-8 explícita (`load_dotenv(encoding='utf-8')`)
- ✅ Validación de tipos
- ✅ Valores por defecto sensatos
- ✅ Cache con `@lru_cache` para mejor rendimiento

---

### 2. **Conexión a Base de Datos (`app/database.py`)**

**Responsabilidad**: Configurar SQLAlchemy y gestionar conexiones.

#### **Estrategia de Conexión**

Usamos un **`creator` personalizado** en lugar de parsear URLs directamente. Esto evita problemas de codificación en Windows:

```python
def create_connection():
    """Factory function que crea conexiones usando parámetros individuales."""
    return psycopg2.connect(
        host=parsed.hostname,
        port=parsed.port,
        user=parsed.username,
        password=parsed.password,
        database=parsed.path.lstrip('/'),
        options='-c client_encoding=UTF8',  # Forzar UTF-8
        connect_timeout=10
    )

engine = create_engine(
    "postgresql+psycopg2://",
    creator=create_connection,  # Usa nuestro factory
    pool_pre_ping=True,          # Verifica conexiones antes de usar
    pool_size=10,                # Pool de conexiones
    max_overflow=20,
    echo=settings.debug,
)
```

#### **Configuración Automática del Esquema**

Cada conexión establece automáticamente el `search_path` al esquema configurado:

```python
@event.listens_for(engine, "connect")
def set_search_path(dbapi_conn, connection_record):
    """Establece el search_path para usar el esquema configurado."""
    cursor = dbapi_conn.cursor()
    cursor.execute(f"SET search_path TO {settings.database_schema}, public")
    cursor.close()
```

**Ventajas**:
- ✅ No necesitas especificar el esquema en cada query
- ✅ Las tablas se crean automáticamente en el esquema correcto
- ✅ Compatible con múltiples esquemas en la misma BD

---

### 3. **Modelos SQLAlchemy (`app/models/bdm_models.py`)**

**Responsabilidad**: Definir la estructura de las tablas en PostgreSQL.

#### **Entidades Implementadas** (10 modelos):

1. **PerfilContratista** - Perfil del contratista
2. **ContratoInterAdministrativo** - Contratos marco
3. **Componente** - Componentes de contratos marco
4. **ObjetivoContrato** - Objetivos de componentes
5. **EvidenciaContrato** - Evidencias
6. **Contrato** - Contratos específicos
7. **Obligacion** - Obligaciones de contratos
8. **Informe** - Informes de ejecución
9. **Ejecucion** - Ejecuciones de obligaciones
10. **DescripcionEjecucion** - Descripciones de ejecuciones

#### **Características de los Modelos**:

```python
class Contrato(Base):
    __tablename__ = "contrato"
    __table_args__ = (
        Index("idx_contrato_perfil_estado", "perfil_contratista_id", "estado"),
        {"schema": get_schema()},  # Especifica el esquema
    )
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, ...)
    # ... campos ...
    
    # Relaciones
    perfil_contratista: Mapped["PerfilContratista"] = relationship(...)
    informes: Mapped[List["Informe"]] = relationship(...)
```

**Características**:
- ✅ Uso de UUIDs como IDs primarios (no Long como en Bonita)
- ✅ Relaciones bien definidas (Foreign Keys, CASCADE, RESTRICT)
- ✅ Índices para optimizar consultas comunes
- ✅ Todos los modelos especifican el esquema automáticamente

---

### 4. **Schemas Pydantic (`app/schemas/bdm_schemas.py`)**

**Responsabilidad**: Validación y serialización de datos.

Para cada entidad hay 3 tipos de schemas:

```python
# Schema base (campos comunes)
class ContratoBase(BaseModel):
    numero_contrato: Optional[str] = None
    estado: Optional[str] = None
    # ...

# Schema para crear (incluye relaciones requeridas)
class ContratoCreate(ContratoBase):
    perfil_contratista_id: UUID
    padre_id: UUID

# Schema para actualizar (todos opcionales)
class ContratoUpdate(BaseModel):
    numero_contrato: Optional[str] = None
    # ...

# Schema de respuesta (incluye ID)
class Contrato(ContratoBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)
```

**Ventajas**:
- ✅ Validación automática de tipos
- ✅ Serialización/deserialización JSON
- ✅ Documentación automática en OpenAPI
- ✅ Schemas con relaciones para respuestas completas

---

### 5. **Repositorios (`app/repositories/`)**

**Responsabilidad**: Acceso aislado a la base de datos.

#### **Repositorio Base Genérico**:

```python
class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def get(self, id: UUID) -> Optional[ModelType]
    def get_all(self, skip, limit, filters, order_by) -> List[ModelType]
    def create(self, obj_in: CreateSchemaType) -> ModelType
    def update(self, id: UUID, obj_in: UpdateSchemaType) -> Optional[ModelType]
    def delete(self, id: UUID) -> bool
    def count(self, filters) -> int
```

#### **Repositorios Especializados**:

```python
class ContratoRepository(BaseRepository):
    def get_by_usuario_bonita(self, id_usuario_bonita: str) -> List[Contrato]:
        """Equivalente a findByUsuarioBonita del BDM."""
        return (
            self.db.query(Contrato)
            .join(PerfilContratista)
            .filter(PerfilContratista.id_usuario_bonita == id_usuario_bonita)
            .all()
        )
```

**Ventajas**:
- ✅ Consultas personalizadas equivalentes al BDM
- ✅ Reutilización de código base
- ✅ Fácil de testear
- ✅ Aislamiento de la lógica de acceso a datos

---

### 6. **Servicios (`app/services/`)**

**Responsabilidad**: Lógica de negocio y validación.

```python
class ContratoService:
    def __init__(self, db: Session):
        self.contrato_repo = ContratoRepository(Contrato, db)
        self.perfil_repo = BaseRepository(PerfilContratista, db)
    
    def create_contrato(self, contrato_in: ContratoCreate) -> ContratoSchema:
        # Validar que existan las relaciones
        if not self.perfil_repo.exists(contrato_in.perfil_contratista_id):
            raise ValueError("PerfilContratista no existe")
        
        return self.contrato_repo.create(contrato_in)
```

**Características**:
- ✅ Validación de reglas de negocio
- ✅ Validación de relaciones (Foreign Keys)
- ✅ Transformación entre modelos y schemas
- ✅ Manejo de errores estructurado

---

### 7. **Routers REST (`app/api/routers/bdm_*.py`)**

**Responsabilidad**: Endpoints HTTP para la API.

```python
@router.get("/api/bdm/contratos", response_model=List[ContratoSchema])
async def listar_contratos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    estado: Optional[str] = None,
    service: ContratoService = Depends(get_contrato_service)
):
    """Listar contratos con paginación y filtros."""
    return service.get_contratos(skip=skip, limit=limit, estado=estado)
```

**Endpoints Disponibles**:

**Contratos**:
- `GET /api/bdm/contratos` - Listar
- `GET /api/bdm/contratos/{id}` - Obtener por ID
- `GET /api/bdm/contratos/usuario/{id_usuario_bonita}` - Por usuario Bonita
- `POST /api/bdm/contratos` - Crear
- `PUT /api/bdm/contratos/{id}` - Actualizar
- `DELETE /api/bdm/contratos/{id}` - Eliminar

**Informes**:
- `GET /api/bdm/informes` - Listar
- `GET /api/bdm/informes/contrato/{contrato_id}` - Por contrato
- `POST /api/bdm/informes` - Crear
- `PUT /api/bdm/informes/{id}` - Actualizar
- `DELETE /api/bdm/informes/{id}` - Eliminar

**Características**:
- ✅ Documentación automática (Swagger/ReDoc)
- ✅ Validación automática con Pydantic
- ✅ Paginación en todas las listas
- ✅ Filtros opcionales
- ✅ Manejo de errores HTTP estándar

---

## 🔄 Flujo de Datos Completo

### **Crear un Contrato**:

```
1. Cliente HTTP → POST /api/bdm/contratos
   {
     "numero_contrato": "CT-001",
     "perfil_contratista_id": "uuid-123",
     "padre_id": "uuid-456"
   }

2. Router (bdm_contratos.py)
   ↓
   Valida con Pydantic (ContratoCreate schema)
   ↓
   Llama a ContratoService.create_contrato()

3. Service (contrato_service.py)
   ↓
   Valida que existan las relaciones
   ↓
   Llama a ContratoRepository.create()

4. Repository (contrato_repository.py)
   ↓
   Ejecuta: INSERT INTO seguimientodap.contrato ...
   ↓
   Retorna modelo SQLAlchemy

5. Service
   ↓
   Convierte a ContratoSchema (Pydantic)
   ↓
   Retorna al Router

6. Router
   ↓
   Serializa a JSON
   ↓
   Retorna HTTP 201 con el contrato creado
```

### **Consultar Contratos por Usuario Bonita**:

```
1. Cliente HTTP → GET /api/bdm/contratos/usuario/USER-123

2. Router
   ↓
   Llama a ContratoService.get_contratos_by_usuario_bonita()

3. Service
   ↓
   Llama a ContratoRepository.get_by_usuario_bonita()

4. Repository
   ↓
   Ejecuta: SELECT c.* FROM seguimientodap.contrato c
           JOIN seguimientodap.perfil_contratista p
           WHERE p.id_usuario_bonita = 'USER-123'
   ↓
   Retorna List[Contrato]

5. Service → Router → Cliente
   ↓
   JSON: [{ "id": "...", "numero_contrato": "...", ... }]
```

---

## 🗄️ Estructura de la Base de Datos

### **Esquema: `SeguimientoDAP`**

```
seguimientodap/
├── perfil_contratista
├── contrato_inter_administrativo
├── componente
├── objetivo_contrato
├── evidencia_contrato
├── contrato
├── obligacion
├── informe
├── ejecucion
└── descripcion_ejecucion
```

### **Relaciones Principales**:

```
ContratoInterAdministrativo (Contrato Marco)
    ├── Componente (1:N)
    │   └── ObjetivoContrato (1:N)
    │       └── EvidenciaContrato (1:N)
    └── Contrato (1:N)
        ├── PerfilContratista (N:1)
        ├── Obligacion (1:N)
        │   └── EvidenciaContrato (1:N)
        └── Informe (1:N)
            └── Ejecucion (1:N)
                ├── Obligacion (N:1)
                └── DescripcionEjecucion (1:N)
```

---

## 🚀 Inicialización y Migraciones

### **Opción 1: Script Directo** (Desarrollo)

```bash
python scripts/init_db.py
```

**Qué hace**:
1. Crea el esquema `SeguimientoDAP` si no existe
2. Crea todas las tablas basadas en los modelos SQLAlchemy
3. Establece índices y constraints

### **Opción 2: Alembic** (Producción)

```bash
# Crear migración inicial
alembic revision --autogenerate -m "Initial migration"

# Aplicar migraciones
alembic upgrade head

# Revertir última migración
alembic downgrade -1
```

**Ventajas de Alembic**:
- ✅ Versionado de cambios en la BD
- ✅ Migraciones reversibles
- ✅ Historial de cambios
- ✅ Aplicable en múltiples entornos

---

## 🔧 Configuración y Variables de Entorno

### **Archivo `.env`**:

```env
# Base de datos PostgreSQL
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/doc360
DATABASE_SCHEMA=SeguimientoDAP
DEBUG=False
```

### **Configuración del Engine**:

- **Pool de conexiones**: 10 conexiones base, 20 máximo
- **Pool pre-ping**: Verifica conexiones antes de usar
- **Timeout**: 10 segundos
- **Codificación**: UTF-8 forzado
- **Esquema automático**: Se establece en cada conexión

---

## 🛡️ Manejo de Errores y Validaciones

### **Niveles de Validación**:

1. **Pydantic** (Schemas): Valida tipos y formato
2. **Servicios**: Valida reglas de negocio y relaciones
3. **Repositorios**: Valida existencia de registros
4. **PostgreSQL**: Valida constraints y Foreign Keys

### **Errores Comunes**:

- **404**: Recurso no encontrado
- **400**: Validación fallida (Pydantic)
- **500**: Error del servidor (loggeado)

---

## 📊 Ventajas de esta Arquitectura

### **vs. BDM de Bonita**:

| Característica | BDM Bonita | Servicio Puente |
|---------------|------------|-----------------|
| Base de datos | H2 (limitado) | PostgreSQL (completo) |
| Consultas SQL | Limitadas | SQL completo |
| Escalabilidad | Baja | Alta |
| Desacoplamiento | Acoplado a Bonita | Independiente |
| Testing | Difícil | Fácil (unit tests) |
| Migraciones | Manual | Alembic automático |

### **Beneficios**:

1. ✅ **Independencia**: El servicio puede usarse sin Bonita
2. ✅ **Escalabilidad**: PostgreSQL maneja grandes volúmenes
3. ✅ **Mantenibilidad**: Código organizado en capas
4. ✅ **Testabilidad**: Cada capa es testeable independientemente
5. ✅ **Flexibilidad**: Fácil agregar nuevas entidades/endpoints
6. ✅ **Performance**: Pool de conexiones, índices optimizados

---

## 🔗 Integración con Bonita

Bonita puede consumir estos endpoints en lugar del BDM:

```groovy
// En un script de Bonita
def response = new URL("http://servicio-puente:8000/api/bdm/contratos/usuario/${apiAccessor.identityAPI.getCurrentUser().id}").text
def contratos = new groovy.json.JsonSlurper().parseText(response)
```

**Ventajas**:
- Bonita solo orquesta procesos
- Los datos viven en PostgreSQL
- El frontend consume FastAPI directamente
- Separación clara de responsabilidades

---

## 📝 Próximos Pasos Recomendados

1. **Agregar autenticación JWT** a los endpoints
2. **Implementar logging** estructurado
3. **Agregar tests unitarios** para servicios y repositorios
4. **Configurar CORS** para el frontend
5. **Agregar rate limiting** para protección
6. **Implementar cache** (Redis) para consultas frecuentes
7. **Agregar más entidades** del modelo BDM si es necesario

---

## 📚 Referencias

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

**Última actualización**: Diciembre 2024

