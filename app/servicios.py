import asyncpg

from app.repositorio import obtener_usuario_por_identificacion
from app.modelos import UsuarioEnBD
from app.seguridad import DUMMY_HASH, verify_password
"""Revisar"""
from datetime import date, time
from decimal import ROUND_HALF_UP, Decimal
from fastapi import UploadFile
from starlette.concurrency import run_in_threadpool
from pathlib import Path
from uuid import uuid4
from app.config import DIRECTORIO_EVIDENCIAS
from app.repositorio import obtener_proyectos_del_estudiante, horas_acumuladas, insertar_horas, proyecto_inscrito_bloqueado, contar_inscritos, insertar_inscripcion, proyecto_para_inscripcion


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

MAX_BYTES = 10 * 1024 * 1024
FIRMAS = {
    ".jpg": b"\xff\xd8\xff",
    ".jpeg": b"\xff\xd8\xff",
    ".png": b"\x89PNG\r\n\x1a\n",
    ".pdf": b"%PDF",
}


class ErrorRegistroHoras(Exception):
    """Regla de negocio incumplida; el mensaje se puede mostrar al profesor."""


def calcular_horas(inicio: time, fin: time) -> Decimal:
    minutos = (fin.hour * 60 + fin.minute) - (inicio.hour * 60 + inicio.minute)
    if minutos <= 0:
        raise ErrorRegistroHoras(
            "La hora de finalización debe ser posterior a la de inicio."
        )
    return (Decimal(minutos) / 60).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


async def _leer_evidencia(evidencia: UploadFile | None) -> tuple[bytes, str] | None:
    if evidencia is None or not evidencia.filename:
        return None  # sin archivo: la evidencia es opcional

    ext = Path(evidencia.filename).suffix.lower()
    firma = FIRMAS.get(ext)
    if firma is None:
        raise ErrorRegistroHoras("La evidencia debe ser JPG, PNG o PDF.")

    contenido = await evidencia.read(MAX_BYTES + 1)
    if len(contenido) > MAX_BYTES:
        raise ErrorRegistroHoras("La evidencia supera los 10 MB.")
    if not contenido.startswith(firma):
        raise ErrorRegistroHoras("El contenido del archivo no coincide con su extensión.")
    return contenido, ext


async def registrar_horas_estudiante(
    conexion,
    *,
    profesor_id: int,
    estudiante_id: int,
    proyecto_id: int,
    fecha: date,
    hora_inicio: time,
    hora_fin: time,
    observaciones: str,
    evidencia: UploadFile | None,
) -> None:
    if fecha > date.today():
        raise ErrorRegistroHoras("La fecha no puede ser futura.")

    cantidad = calcular_horas(hora_inicio, hora_fin)
    archivo = await _leer_evidencia(evidencia)

    ruta_guardada: Path | None = None
    try:
        async with conexion.transaction():
            proyecto = await proyecto_inscrito_bloqueado(
                conexion, proyecto_id, profesor_id, estudiante_id
            )
            if proyecto is None:
                raise ErrorRegistroHoras(
                    "El estudiante no está inscrito en ese proyecto, "
                    "o el proyecto no es tuyo."
                )

            acumuladas = await horas_acumuladas(conexion, estudiante_id, proyecto_id)
            restantes = proyecto["horas_otorgadas"] - acumuladas
            if cantidad > restantes:
                raise ErrorRegistroHoras(
                    f"Excede las horas del proyecto: al estudiante le quedan "
                    f"{restantes:.2f} h y este registro es de {cantidad:.2f} h."
                )

            nombre_archivo = None
            if archivo is not None:
                contenido, ext = archivo
                nombre_archivo = f"{uuid4().hex}{ext}"
                ruta_guardada = DIRECTORIO_EVIDENCIAS / nombre_archivo
                DIRECTORIO_EVIDENCIAS.mkdir(parents=True, exist_ok=True)
                await run_in_threadpool(ruta_guardada.write_bytes, contenido)

            await insertar_horas(
                conexion, estudiante_id, profesor_id, proyecto_id,
                cantidad, fecha, hora_inicio, hora_fin,
                observaciones.strip() or None, nombre_archivo,
            )
    except Exception:

        if ruta_guardada is not None:
            ruta_guardada.unlink(missing_ok=True)
        raise

