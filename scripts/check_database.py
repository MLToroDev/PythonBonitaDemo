"""
Script para verificar si la base de datos existe y crear el esquema.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from urllib.parse import urlparse
import psycopg2
from psycopg2 import sql
from app.config import get_settings

def check_and_setup():
    """Verifica la base de datos y crea el esquema si es necesario."""
    settings = get_settings()
    parsed = urlparse(settings.database_url)
    
    db_name = parsed.path.lstrip('/')
    schema_name = settings.database_schema
    
    print(f"Verificando conexión a PostgreSQL...")
    print(f"Base de datos: {db_name}")
    print(f"Esquema: {schema_name}")
    print()
    
    try:
        # Conectar a la base de datos 'postgres' por defecto primero
        print("1. Conectando al servidor PostgreSQL...")
        conn = psycopg2.connect(
            host=parsed.hostname or 'localhost',
            port=parsed.port or 5432,
            user=parsed.username or 'postgres',
            password=parsed.password or '',
            database='postgres',  # Conectar a postgres primero
            connect_timeout=5
        )
        print("   ✓ Conexión exitosa al servidor")
        
        # Verificar si la base de datos existe
        print(f"\n2. Verificando si la base de datos '{db_name}' existe...")
        cur = conn.cursor()
        cur.execute("""
            SELECT 1 FROM pg_database WHERE datname = %s
        """, (db_name,))
        
        if cur.fetchone():
            print(f"   ✓ La base de datos '{db_name}' existe")
            cur.close()
            conn.close()
            
            # Ahora conectar a la base de datos específica
            print(f"\n3. Conectando a la base de datos '{db_name}'...")
            conn = psycopg2.connect(
                host=parsed.hostname or 'localhost',
                port=parsed.port or 5432,
                user=parsed.username or 'postgres',
                password=parsed.password or '',
                database=db_name,
                connect_timeout=5,
                options='-c client_encoding=UTF8'
            )
            print("   ✓ Conexión exitosa")
            
        else:
            print(f"   ✗ La base de datos '{db_name}' NO existe")
            print(f"\n   Creando la base de datos '{db_name}'...")
            conn.rollback()  # Cerrar cualquier transacción
            conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
            cur.execute(sql.SQL("CREATE DATABASE {}").format(
                sql.Identifier(db_name)
            ))
            print(f"   ✓ Base de datos '{db_name}' creada")
            cur.close()
            conn.close()
            
            # Conectar a la nueva base de datos
            print(f"\n3. Conectando a la nueva base de datos '{db_name}'...")
            conn = psycopg2.connect(
                host=parsed.hostname or 'localhost',
                port=parsed.port or 5432,
                user=parsed.username or 'postgres',
                password=parsed.password or '',
                database=db_name,
                connect_timeout=5,
                options='-c client_encoding=UTF8'
            )
            print("   ✓ Conexión exitosa")
        
        # Crear el esquema si no existe
        print(f"\n4. Verificando si el esquema '{schema_name}' existe...")
        cur = conn.cursor()
        cur.execute("""
            SELECT 1 FROM information_schema.schemata WHERE schema_name = %s
        """, (schema_name,))
        
        if cur.fetchone():
            print(f"   ✓ El esquema '{schema_name}' ya existe")
        else:
            print(f"   Creando el esquema '{schema_name}'...")
            conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
            cur.execute(sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(
                sql.Identifier(schema_name)
            ))
            print(f"   ✓ Esquema '{schema_name}' creado")
        
        cur.close()
        conn.close()
        
        print(f"\n{'='*60}")
        print("✓ Configuración completada exitosamente")
        print(f"{'='*60}")
        print(f"\nAhora puedes ejecutar: python scripts/init_db.py")
        
    except psycopg2.OperationalError as e:
        error_msg = str(e)
        # Intentar decodificar si es necesario
        if hasattr(e, 'args') and e.args and isinstance(e.args[0], bytes):
            try:
                error_msg = e.args[0].decode('latin-1', errors='replace')
            except:
                error_msg = str(e)
        
        print(f"\n✗ Error de conexión: {error_msg}")
        print(f"\nPosibles soluciones:")
        print(f"1. Verifica que PostgreSQL esté ejecutándose")
        print(f"2. Verifica las credenciales en el archivo .env")
        print(f"3. Verifica que el usuario tenga permisos para crear bases de datos")
        
    except Exception as e:
        print(f"\n✗ Error inesperado: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_and_setup()

