"""Da de alta un usuario en la tabla `usuarios` con argon2.

Uso:
    uv run python scripts/crear_usuario.py "Nombre Apellido" correo@ejemplo.com contraseña
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import db  # noqa: E402
from app.repositorio import obtener_usuario_por_identificacion, crear_usuario  # noqa: E402
from app.seguridad import get_password_hash  # noqa: E402
from app.config import URL_DATABASE


async def main() -> None:
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)

    identificacion, rol, contrasena = sys.argv[1:4]

    await db.connect(URL_DATABASE)
    try:
        # El script gestiona su propia conexión (aquí no hay dependencias)
        async with db.pool.acquire() as conexion:
            if await obtener_usuario_por_identificacion(conexion, identificacion) is not None:
                print(f"Ya existe un usuario con el correo {identificacion!r}.")
                sys.exit(1)

            usuario = await crear_usuario(
                conexion,
                identificacion=identificacion,
                rol=rol,
                contrasena_hasheada=get_password_hash(contrasena),
            )
            print(
                f"Usuario creado: id={usuario.id} "
                f"identificacion={usuario.identificacion!r} rol={usuario.rol!r}"
            )
    finally:
        await db.close()


asyncio.run(main())