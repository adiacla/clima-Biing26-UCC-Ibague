import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings


# Cargar variables del entorno desde el archivo .env
load_dotenv()



mcp = FastMCP(
    "CCD Server",
    host="0.0.0.0",
    port=9000,
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=["mlflowunab.duckdns.org:9000", "localhost:9000", "127.0.0.1:9000"],
        allowed_origins=["http://mlflowunab.duckdns.org:9000", "http://localhost:9000"],
    ),
)
def get_db_connection():
    """Establece una conexión segura con PostgreSQL (Supabase)."""
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT", "6543"),
        sslmode="require"
    )

@mcp.tool()
def identificar_estudiante(id_estudiante: str) -> str:
    """
    Busca un estudiante en el sistema por su documento de identidad o código UNAB.
    Retorna información general del estudiante y su programa académico.
    """
    query = """
    SELECT e.id_estudiante, e.nombre, e.apellido, e.email, e.semestre_actual, p.nombre AS programa
    FROM ccd.estudiantes e
    LEFT JOIN ccd.programas p ON e.id_programa = p.id_programa
    WHERE e.id_estudiante = %s;
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (id_estudiante,))
                result = cur.fetchone()
                if result:
                    return json.dumps(result, default=str)
                return json.dumps({"status": "no_encontrado", "mensaje": "Estudiante no registrado"})
    except Exception as e:
        return json.dumps({"status": "error", "detalle": str(e)})

@mcp.tool()
def obtener_progreso_estudiante(id_estudiante: str) -> str:
    """
    Obtiene el estado de la Ruta de Competencias Digitales de un estudiante.
    Retorna los cursos completados, en curso y aquellos que aún están pendientes.
    """
    # Consulta optimizada que llama a las vistas y retorna datos estructurados
    query = """
    SELECT 
        ve.id_estudiante,
        ve.nombre_completo,
        ve.programa,
        ve.semestre_actual,
        ve.cursos_tomados,
        ve.cursos_aprobados,
        ve.cursos_en_curso,
        ve.estado_ruta,
        COALESCE(
            (SELECT json_agg(json_build_object(
                'codigo', c.codigo_curso,
                'nombre', c.nombre,
                'pilar', c.pilar,
                'estado', ct.estado,
                'nota', ct.nota
             ))
             FROM ccd.cursos_tomados ct
             JOIN ccd.cursos c ON ct.id_curso = c.id_curso
             WHERE ct.id_estudiante = ve.id_estudiante),
            '[]'::json
        ) AS detalle_cursos_tomados,
        COALESCE(
            (SELECT json_agg(json_build_object(
                'codigo', cp.codigo_curso,
                'nombre', cp.curso_pendiente,
                'pilar', cp.pilar,
                'obligatorio', cp.obligatorio
             ))
             FROM ccd.v_cursos_pendientes cp
             WHERE cp.id_estudiante = ve.id_estudiante),
            '[]'::json
        ) AS detalle_cursos_pendientes
    FROM ccd.v_estado_estudiante ve
    WHERE ve.id_estudiante = %s;
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (id_estudiante,))
                result = cur.fetchone()
                if result:
                    return json.dumps(result, default=str)
                return json.dumps({"status": "error", "mensaje": "No se encontraron registros de progreso"})
    except Exception as e:
        return json.dumps({"status": "error", "detalle": str(e)})

@mcp.tool()
def registrar_solicitud(id_estudiante: str, nombre_estudiante: str, tipo_solicitud: str, descripcion: str) -> str:
    """
    Crea una nueva solicitud o caso de soporte en la base de datos.
    Esta solicitud quedará marcada para sincronizarse automáticamente con n8n/Google Sheets.
    """
    query = """
    INSERT INTO ccd.solicitudes (id_estudiante, nombre_estudiante, tipo_solicitud, descripcion, estado, enviado_sheets)
    VALUES (%s, %s, %s, %s, 'pendiente', FALSE)
    RETURNING id, fecha, estado;
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Si el id_estudiante es nulo o vacío se guarda como None
                estudiante_val = id_estudiante if id_estudiante and id_estudiante.strip() != "" else None
                cur.execute(query, (estudiante_val, nombre_estudiante, tipo_solicitud, descripcion))
                result = cur.fetchone()
                conn.commit()
                return json.dumps({"status": "exito", "solicitud": result}, default=str)
    except Exception as e:
        return json.dumps({"status": "error", "detalle": str(e)})

@mcp.tool()
def registrar_conversacion(telegram_id: str, id_estudiante: str, pregunta: str, respuesta: str, tipo: str) -> str:
    """
    Guarda la interacción en el historial de conversaciones para auditorías de calidad.
    """
    query = """
    INSERT INTO ccd.conversaciones (telegram_id, id_estudiante, pregunta, respuesta, tipo)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING id;
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                estudiante_val = id_estudiante if id_estudiante and id_estudiante.strip() != "" else None
                cur.execute(query, (telegram_id, estudiante_val, pregunta, respuesta, tipo))
                result = cur.fetchone()
                conn.commit()
                return json.dumps({"status": "registrado", "id_conversacion": result["id"]})
    except Exception as e:
        return json.dumps({"status": "error", "detalle": str(e)})

if __name__ == "__main__":
    # Ejecutar el servidor MCP
    mcp.run()