import asyncpg

from app.modelos import UsuarioEnBD


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