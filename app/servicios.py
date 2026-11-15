import asyncpg

from app.repositorio import obtener_usuario_por_identificacion
from app.modelos import UsuarioEnBD
from app.seguridad import DUMMY_HASH, verify_password
"""Revisar"""
from datetime import date
from app.repositorio import obtener_proyectos_del_estudiante


async def autenticar_usuario(
    conexion: asyncpg.Connection, identificacion: str, contrasena: str
) -> UsuarioEnBD | None:

    usuario = await obtener_usuario_por_identificacion(conexion, identificacion)

    hash_verificar = (
        usuario.contrasena_hasheada
        if usuario is not None
        else DUMMY_HASH
    )

    valido = verify_password(contrasena, hash_verificar)

    if usuario is None or not valido:
        return None 

    return usuario

"""Revisar"""


def _estado(obtenidas: float, totales: float, fecha_inicio: date) -> tuple[str, str]:
    """Devuelve (texto del badge, clase CSS)."""
    if obtenidas >= totales:
        return "Completado", "badge-done"
    if fecha_inicio > date.today():
        return "Pendiente", "badge-pending"
    return "En proceso", "badge-process"


async def resumen_mis_proyectos(conexion, estudiante_id: int) -> dict:
    filas = await obtener_proyectos_del_estudiante(conexion, estudiante_id)

    proyectos = []
    total_horas = 0.0
    total_obtenidas = 0.0
    completados = 0

    for f in filas:
        totales = float(f["horas_totales"])      # NUMERIC llega como Decimal
        obtenidas = float(f["horas_obtenidas"])
        estado, clase = _estado(obtenidas, totales, f["fecha_inicio"])

        proyectos.append({
            **f,
            "horas_totales": totales,
            "horas_obtenidas": obtenidas,
            "porcentaje": min(100, round(obtenidas / totales * 100)),
            "estado": estado,
            "estado_clase": clase,
        })

        total_horas += totales
        total_obtenidas += min(obtenidas, totales)   # no cuenta horas de más
        if estado == "Completado":
            completados += 1

    return {
        "proyectos": proyectos,
        "stats": {
            "inscritos": len(proyectos),
            "obtenidas": total_obtenidas,
            "totales": total_horas,
            "pendientes": total_horas - total_obtenidas,
            "completados": completados,
        },
    }