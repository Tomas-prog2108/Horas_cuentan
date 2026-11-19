from collections.abc import AsyncIterator
from typing import Annotated

import asyncpg
from fastapi import Depends, HTTPException, Request

from app.config import COOKIE_SESSION
from app.database import db
from app.repositorio import obtener_usuario_por_identificacion, obtener_profesor_por_usuario_id
from app.modelos import Usuario
from app.seguridad import decode_access_token


async def obtener_conexion() -> AsyncIterator[asyncpg.Connection]:
    """Toma una conexión del pool y la libera al terminar la petición.

    FastAPI la ejecuta una vez por petición y reutiliza el resultado en
    todas las dependencias que la necesiten (use_cache).
    """
    async with db.pool.acquire() as conexion:
        yield conexion


ConexionDepend = Annotated[asyncpg.Connection, Depends(obtener_conexion)]


async def usuario_actual(request: Request, conexion: ConexionDepend) -> Usuario:

    token = request.cookies.get(COOKIE_SESSION)
    if token is None:
        raise HTTPException(status_code=303, headers={"Location": "/login"})

    # Payload del JWT: {'sub': 'prueba@example.com', 'exp': 1789745617}
    payload = decode_access_token(token)

    identificacion = payload.get("sub") if payload else None

    if not isinstance(identificacion, str):
        raise HTTPException(status_code=303, headers={"Location": "/login"})

    usuario_bd = await obtener_usuario_por_identificacion(conexion, identificacion)
    if usuario_bd is None:
        raise HTTPException(status_code=303, headers={"Location": "/login"})

    # Se devuelve el modelo público: el hash de la contraseña no circula
    # por la aplicación más allá de este punto.
    return Usuario.model_validate(usuario_bd)

UserDepend = Annotated[Usuario, Depends(usuario_actual)]

async def estudiante_actual(
        usuario: UserDepend,
) -> Usuario:

    if usuario.rol != "estudiante":
        raise HTTPException(status_code=403)
    return usuario  

async def profesor_actual(
        usuario: UserDepend,
) -> Usuario:

    if usuario.rol != "profesor":
        raise HTTPException(status_code=403)
    return usuario


async def administrador_actual(
        usuario: UserDepend,
) -> Usuario:

    if usuario.rol != "administrador":
        raise HTTPException(status_code=403)
    return usuario

Estudiante_Depend = Annotated[Usuario, Depends(estudiante_actual)]
Profesor_Depend = Annotated[Usuario, Depends(profesor_actual)]
Administrador_Depend = Annotated[Usuario, Depends(administrador_actual)]

async def perfil_profesor_actual(
    usuario: Profesor_Depend, conexion: ConexionDepend
) -> dict:
    perfil = await obtener_profesor_por_usuario_id(conexion, usuario.id)
    if perfil is None:
        raise HTTPException(
            status_code=403, detail="Tu usuario no tiene perfil de profesor."
        )
    return perfil

PerfilProfesorDepend = Annotated[dict, Depends(perfil_profesor_actual)]

