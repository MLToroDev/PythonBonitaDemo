"""
Script de prueba para diagnosticar problemas de conexión a PostgreSQL.
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from urllib.parse import urlparse
from app.config import get_settings

def test_connection():
    """Prueba la configuración y conexión a la base de datos."""
    try:
        settings = get_settings()
        
        print("=" * 60)
        print("DIAGNÓSTICO DE CONFIGURACIÓN")
        print("=" * 60)
        
        print(f"\n1. URL de conexión (raw):")
        print(f"   {settings.database_url}")
        
        print(f"\n2. Esquema configurado:")
        print(f"   {settings.database_schema}")
        
        print(f"\n3. Análisis de la URL:")
        parsed = urlparse(settings.database_url)
        print(f"   Esquema: {parsed.scheme}")
        print(f"   Usuario: {parsed.username}")
        print(f"   Contraseña: {'***' if parsed.password else '(no configurada)'}")
        print(f"   Host: {parsed.hostname}")
        print(f"   Puerto: {parsed.port}")
        print(f"   Base de datos: {parsed.path.lstrip('/')}")
        
        print(f"\n4. Verificación de codificación:")
        url_bytes = settings.database_url.encode('utf-8')
        print(f"   URL en bytes (longitud): {len(url_bytes)}")
        print(f"   Puede decodificar UTF-8: ✓")
        
        print(f"\n5. Intentando importar psycopg2...")
        try:
            import psycopg2
            print(f"   psycopg2 versión: {psycopg2.__version__}")
        except ImportError as e:
            print(f"   ✗ Error al importar psycopg2: {e}")
            return
        
        print(f"\n6. Intentando conectar...")
        try:
            # Intentar conexión directa con psycopg2
            # Usar connect_timeout para evitar esperas largas
            conn = psycopg2.connect(
                host=parsed.hostname or 'localhost',
                port=parsed.port or 5432,
                user=parsed.username or 'postgres',
                password=parsed.password or '',
                database=parsed.path.lstrip('/') or 'postgres',
                connect_timeout=5,
                options='-c client_encoding=UTF8'
            )
            print(f"   ✓ Conexión exitosa!")
            
            # Verificar la codificación del servidor
            cur = conn.cursor()
            cur.execute("SHOW client_encoding;")
            encoding = cur.fetchone()[0]
            print(f"   Codificación del servidor: {encoding}")
            cur.close()
            conn.close()
        except UnicodeDecodeError as e:
            print(f"   ✗ Error de codificación Unicode: {e}")
            print(f"\n   Este error generalmente ocurre cuando:")
            print(f"   - El servidor PostgreSQL devuelve mensajes en codificación no UTF-8")
            print(f"   - Hay un problema con la configuración de locale del servidor")
            print(f"\n   Soluciones:")
            print(f"   1. Verificar que PostgreSQL esté configurado para UTF-8")
            print(f"   2. Intentar conectar usando psql para ver el mensaje de error real")
            print(f"   3. Revisar la configuración de locale en PostgreSQL")
        except psycopg2.OperationalError as e:
            error_msg = str(e)
            # Intentar decodificar el mensaje de error con diferentes codificaciones
            if isinstance(e.args[0], bytes):
                try:
                    error_msg = e.args[0].decode('utf-8', errors='replace')
                except:
                    try:
                        error_msg = e.args[0].decode('latin-1', errors='replace')
                    except:
                        error_msg = str(e.args[0])
            print(f"   ✗ Error operacional: {error_msg}")
            print(f"\n   Posibles causas:")
            print(f"   - PostgreSQL no está ejecutándose")
            print(f"   - Credenciales incorrectas")
            print(f"   - La base de datos '{parsed.path.lstrip('/')}' no existe")
            print(f"   - Problema de red/firewall")
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            print(f"   ✗ Error de conexión ({error_type}): {error_msg}")
            
            # Si es un error de bytes, intentar mostrar información útil
            if hasattr(e, 'args') and e.args:
                if isinstance(e.args[0], bytes):
                    print(f"\n   Información del error (bytes):")
                    print(f"   Longitud: {len(e.args[0])}")
                    print(f"   Primeros bytes: {e.args[0][:100]}")
                    try:
                        decoded = e.args[0].decode('latin-1', errors='replace')
                        print(f"   Decodificado (latin-1): {decoded[:200]}")
                    except:
                        pass
        
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error al leer configuración: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_connection()

