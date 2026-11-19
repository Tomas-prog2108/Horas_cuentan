import asyncpg
from datetime import date, time
from decimal import Decimal

from app.modelos import UsuarioEnBD, ProyectoForm 

def _a_usuario(fila: asyncpg.Record | None) -> UsuarioEnBD | None:
    if fila is None:
        return None
    return UsuarioEnBD.model_validate(dict(fila))


async def obtener_usuario_por_identificacion(
    conexion: asyncpg.Connection, identificacion: str
) -> UsuarioEnBD | None:
    fila = await conexion.fetchrow(
        """SELECT id, identificacion, contrasena_hasheada, rol FROM usuarios WHERE identificacion = $1""", identificacion
    )
    return _a_usuario(fila)


async def crear_usuario(
    conexion: asyncpg.Connection,
    identificacion: str,
    contrasena_hasheada: str,
    rol: str,
) -> UsuarioEnBD:
    fila = await conexion.fetchrow(
        """INSERT INTO usuarios (identificacion, contrasena_hasheada, rol)
           VALUES ($1, $2, $3)
           RETURNING id, identificacion, contrasena_hasheada, creado_en, rol""",
        identificacion,
        contrasena_hasheada,
        rol,
    )
    usuario = _a_usuario(fila)
    if usuario is None:
        raise RuntimeError("La inserción del usuario no devolvió ninguna fila")
    return usuario

async def obtener_estudiante_por_usuario_id(
    conexion: asyncpg.Connection,
    usuario_id: int,
) -> dict | None:
    fila = await conexion.fetchrow(
        """SELECT id_estudiante, nombre, grupo, id_usuario, horas_meta
           FROM estudiantes
           WHERE id_usuario = $1""",
        usuario_id,
    )
    return dict(fila) if fila else None

async def horas_obtenidas(conexion: asyncpg.Connection, id_estudiante: int,) -> dict | None:
    fila = await conexion.fetchrow(
        """SELECT COALESCE(SUM(h.cantidad), 0) AS horas_obtenidas FROM horas h WHERE id_estudiante = $1""", id_estudiante,
    )
    return dict(fila) if fila else None

async def obtener_proyectos(conexion: asyncpg.Connection) -> list[dict]:
    filas = await conexion.fetch(
        """SELECT p.id_proyecto,
                  p.nombre,
                  p.descripcion,
                  p.fecha_inicio,
                  p.lugar,
                  pr.nombre AS profesor
            FROM proyectos p
            JOIN profesores pr ON pr.id_profesor = p.id_profesor
            WHERE p.estado = 'activo'
            ORDER BY p.fecha_inicio"""
    )
    return [dict(fila) for fila in filas]

async def obtener_proyectos_del_estudiante(
    conexion: asyncpg.Connection,
    estudiante_id: int,
) -> list[dict]:
    filas = await conexion.fetch(
        """SELECT p.id_proyecto,
                  p.nombre,
                  p.descripcion,
                  p.fecha_inicio,
                  p.horas_otorgadas AS horas_totales,
                  COALESCE(SUM(h.cantidad), 0) AS horas_obtenidas
           FROM inscripciones i
           JOIN proyectos p ON p.id_proyecto = i.id_proyecto
           LEFT JOIN horas h
                  ON h.id_proyecto = p.id_proyecto
                 AND h.id_estudiante = i.id_estudiante
           WHERE i.id_estudiante = $1
           GROUP BY p.id_proyecto
           ORDER BY p.fecha_inicio""",
        estudiante_id,
    )
    return [dict(fila) for fila in filas]

async def seguimiento_horas_del_estudiante(
    conexion: asyncpg.Connection,
    estudiante_id: int,
) -> list[dict]:
    filas = await conexion.fetch(
        """SELECT 
                p.id_proyecto,
                p.nombre,
                h.fecha,
                h.cantidad AS horas_individuales,
                COALESCE(SUM(h.cantidad) OVER(PARTITION BY p.id_proyecto), 0) AS total_horas_proyecto
           FROM inscripciones i
           JOIN proyectos p ON p.id_proyecto = i.id_proyecto
           JOIN horas h
                   ON h.id_proyecto = p.id_proyecto
                  AND h.id_estudiante = i.id_estudiante
           WHERE i.id_estudiante = $1
           ORDER BY h.fecha""",
        estudiante_id,
    )
    return [dict(fila) for fila in filas]

async def obtener_estudiantes(
    conexion: asyncpg.Connection,
) -> list[dict] | None:
    filas = await conexion.fetch(
        """SELECT 
                id_estudiante, 
                e.nombre, 
                e.grupo,
                u.identificacion
           FROM estudiantes e 
           JOIN usuarios u ON u.id = e.id_usuario
           ORDER BY e.nombre""",
    )
    return [dict(fila) for fila in filas]

"""-"""

async def obtener_profesor_por_usuario_id(
    conexion: asyncpg.Connection, usuario_id: int
) -> dict | None:
    fila = await conexion.fetchrow(
        """SELECT id_profesor, id_usuario, nombre
           FROM profesores WHERE id_usuario = $1""",
        usuario_id,
    )
    return dict(fila) if fila else None


async def listar_proyectos_del_profesor(
    conexion: asyncpg.Connection, profesor_id: int
) -> list[dict]:
    filas = await conexion.fetch(
        """SELECT p.id_proyecto, p.nombre, p.descripcion, p.fecha_inicio,
                  p.lugar, p.cupos, p.horas_otorgadas, p.estado,
                  COUNT(i.id_inscripcion) AS inscritos
           FROM proyectos p
           LEFT JOIN inscripciones i ON i.id_proyecto = p.id_proyecto
           WHERE p.id_profesor = $1
           GROUP BY p.id_proyecto
           ORDER BY p.fecha_inicio DESC""",
        profesor_id,
    )
    return [dict(f) for f in filas]


async def obtener_proyecto_del_profesor(
    conexion: asyncpg.Connection, proyecto_id: int, profesor_id: int
) -> dict | None:
    fila = await conexion.fetchrow(
        """SELECT p.id_proyecto, p.nombre, p.descripcion, p.fecha_inicio,
                  p.lugar, p.cupos, p.horas_otorgadas, p.estado,
                  pr.nombre AS profesor
           FROM proyectos p
           JOIN profesores pr ON pr.id_profesor = p.id_profesor
           WHERE p.id_proyecto = $1 AND p.id_profesor = $2""",
        proyecto_id,
        profesor_id,
    )
    return dict(fila) if fila else None


async def listar_inscritos(
    conexion: asyncpg.Connection, proyecto_id: int
) -> list[dict]:
    filas = await conexion.fetch(
        """SELECT e.id_estudiante, e.nombre, e.grupo,
                  u.identificacion AS documento,
                  i.fecha_inscripcion
           FROM inscripciones i
           JOIN estudiantes e ON e.id_estudiante = i.id_estudiante
           JOIN usuarios u ON u.id = e.id_usuario
           WHERE i.id_proyecto = $1
           ORDER BY e.nombre""",
        proyecto_id,
    )
    return [dict(f) for f in filas]


async def crear_proyecto(
    conexion: asyncpg.Connection, profesor_id: int, datos: ProyectoForm
) -> int:
    return await conexion.fetchval(
        """INSERT INTO proyectos
               (id_profesor, nombre, descripcion, fecha_inicio,
                lugar, cupos, horas_otorgadas, estado)
           VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
           RETURNING id_proyecto""",
        profesor_id,
        datos.nombre,
        datos.descripcion or None,
        datos.fecha_inicio,
        datos.lugar,
        datos.cupos,
        datos.horas,
        datos.estado,
    )


async def actualizar_proyecto(
    conexion: asyncpg.Connection,
    proyecto_id: int,
    profesor_id: int,
    datos: ProyectoForm,
) -> bool:
    resultado = await conexion.execute(
        """UPDATE proyectos
           SET nombre = $3, descripcion = $4, fecha_inicio = $5,
               lugar = $6, cupos = $7, horas_otorgadas = $8, estado = $9
           WHERE id_proyecto = $1 AND id_profesor = $2""",
        proyecto_id,
        profesor_id,
        datos.nombre,
        datos.descripcion or None,
        datos.fecha_inicio,
        datos.lugar,
        datos.cupos,
        datos.horas,
        datos.estado,
    )
    return resultado == "UPDATE 1"


async def eliminar_proyecto(
    conexion: asyncpg.Connection, proyecto_id: int, profesor_id: int
) -> bool:
    resultado = await conexion.execute(
        "DELETE FROM proyectos WHERE id_proyecto = $1 AND id_profesor = $2",
        proyecto_id,
        profesor_id,
    )
    return resultado == "DELETE 1"

async def obtener_estudiantes_del_profesor(
    conexion: asyncpg.Connection, profesor_id: int
) -> list[dict]:
    filas = await conexion.fetch(
        """SELECT DISTINCT e.id_estudiante, e.nombre, e.grupo,
                  u.identificacion
           FROM inscripciones i
           JOIN proyectos p   ON p.id_proyecto = i.id_proyecto
           JOIN estudiantes e ON e.id_estudiante = i.id_estudiante
           JOIN usuarios u    ON u.id = e.id_usuario
           WHERE p.id_profesor = $1
           ORDER BY e.nombre""",
        profesor_id,
    )
    return [dict(f) for f in filas]


async def obtener_estudiante_por_identificacion(
    conexion: asyncpg.Connection, identificacion: str
) -> dict | None:
    fila = await conexion.fetchrow(
        """SELECT e.id_estudiante, e.nombre, e.grupo, u.identificacion
           FROM estudiantes e
           JOIN usuarios u ON u.id = e.id_usuario
           WHERE u.identificacion = $1""",
        identificacion,
    )
    return dict(fila) if fila else None


async def proyectos_para_registrar(
    conexion: asyncpg.Connection, estudiante_id: int, profesor_id: int
) -> list[dict]:
    filas = await conexion.fetch(
        """SELECT p.id_proyecto, p.nombre
           FROM proyectos p
           JOIN inscripciones i ON i.id_proyecto = p.id_proyecto
           WHERE i.id_estudiante = $1 AND p.id_profesor = $2
           ORDER BY p.nombre""",
        estudiante_id,
        profesor_id,
    )
    return [dict(f) for f in filas]


async def proyecto_inscrito_bloqueado(
    conexion: asyncpg.Connection,
    proyecto_id: int, profesor_id: int, estudiante_id: int,
) -> dict | None:
    """Verifica propiedad e inscripción, y bloquea el proyecto hasta el commit."""
    fila = await conexion.fetchrow(
        """SELECT p.id_proyecto, p.horas_otorgadas
           FROM proyectos p
           JOIN inscripciones i ON i.id_proyecto = p.id_proyecto
           WHERE p.id_proyecto = $1 AND p.id_profesor = $2
             AND i.id_estudiante = $3
           FOR UPDATE OF p""",
        proyecto_id, profesor_id, estudiante_id,
    )
    return dict(fila) if fila else None


async def horas_acumuladas(
    conexion: asyncpg.Connection, estudiante_id: int, proyecto_id: int
) -> Decimal:
    return await conexion.fetchval(
        """SELECT COALESCE(SUM(cantidad), 0) FROM horas
           WHERE id_estudiante = $1 AND id_proyecto = $2""",
        estudiante_id, proyecto_id,
    )


async def insertar_horas(
    conexion: asyncpg.Connection,
    estudiante_id: int, profesor_id: int, proyecto_id: int,
    cantidad: Decimal, fecha: date, hora_inicio: time, hora_fin: time,
    observaciones: str | None, evidencia: str | None,
) -> int:
    return await conexion.fetchval(
        """INSERT INTO horas
               (id_estudiante, id_profesor, id_proyecto, cantidad, fecha,
                hora_inicio, hora_fin, observaciones, evidencia)
           VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
           RETURNING id_horas""",
        estudiante_id, profesor_id, proyecto_id, cantidad, fecha,
        hora_inicio, hora_fin, observaciones, evidencia,
    )

async def proyecto_para_inscripcion(
    conexion: asyncpg.Connection, proyecto_id: int
) -> dict | None:
    fila = await conexion.fetchrow(
        """SELECT id_proyecto, cupos, estado
           FROM proyectos
           WHERE id_proyecto = $1
           FOR UPDATE""",
        proyecto_id,
    )
    return dict(fila) if fila else None


async def contar_inscritos(
    conexion: asyncpg.Connection, proyecto_id: int
) -> int:
    return await conexion.fetchval(
        "SELECT COUNT(*) FROM inscripciones WHERE id_proyecto = $1",
        proyecto_id,
    )


async def insertar_inscripcion(
    conexion: asyncpg.Connection, estudiante_id: int, proyecto_id: int
) -> int | None:
    """Devuelve el id nuevo, o None si ya estaba inscrito."""
    return await conexion.fetchval(
        """INSERT INTO inscripciones (id_estudiante, id_proyecto)
           VALUES ($1, $2)
           ON CONFLICT (id_estudiante, id_proyecto) DO NOTHING
           RETURNING id_inscripcion""",
        estudiante_id,
        proyecto_id,
    )