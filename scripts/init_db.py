"""
Script para inicializar la base de datos:
- Crea el esquema si no existe
- Crea todas las tablas registradas en los modelos SQLAlchemy
"""

import sys
import os
from sqlalchemy import text, inspect

# Asegurar import del proyecto
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import engine, Base
from app.config import get_settings
from app.models import bdm_models  # Import explícito recomendado


def init_db():
    settings = get_settings()
    schema_name = settings.database_schema

    print(f"\n=== Inicializando base de datos en el schema '{schema_name}' ===")

    # 1. Validar conexión
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✓ Conexión exitosa a la base de datos")
    except Exception as e:
        print(f"✗ Error conectando a la base de datos: {e}")
        return

    # 2. Crear schema si no existe
    try:
        with engine.begin() as conn:
            conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"'))
        print(f"✓ Schema '{schema_name}' verificado/creado")
    except Exception as e:
        print(f"✗ Error creando schema: {e}")
        return

    # 3. Crear tablas
    try:
        Base.metadata.create_all(bind=engine)
        print("✓ Tablas creadas correctamente")
    except Exception as e:
        print(f"✗ Error creando tablas: {e}")
        return

    # 4. Listar tablas creadas
    inspector = inspect(engine)
    tablas = inspector.get_table_names(schema=schema_name)
    print(f"Tablas en '{schema_name}': {tablas}")

    print("\n=== Inicialización completa ===")


if __name__ == "__main__":
    init_db()
