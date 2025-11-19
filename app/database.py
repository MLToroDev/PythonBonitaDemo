from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from urllib.parse import urlparse
import psycopg2
from app.config import get_settings

settings = get_settings()

parsed = urlparse(settings.database_url)

def create_connection():
    return psycopg2.connect(
        host=parsed.hostname,
        port=parsed.port,
        user=parsed.username,
        password=parsed.password,
        database=parsed.path.lstrip('/'),
        options='-c client_encoding=UTF8',
        connect_timeout=10
    )

engine = create_engine(
    "postgresql+psycopg2://",   # NO necesita usuario ni contraseña
    creator=create_connection,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=settings.debug,
)

@event.listens_for(engine, "connect")
def set_search_path(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute(f"SET search_path TO {settings.database_schema}, public")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_schema():
    """Obtiene el nombre del esquema desde la configuración."""
    return settings.database_schema

def get_db():
    """
    Dependency para obtener una sesión de base de datos.
    Usar con: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
