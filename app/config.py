import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")


if os.environ.get("VERCEL"):          
    DIRECTORIO_EVIDENCIAS = Path("/tmp") / "evidencias"
else:
    DIRECTORIO_EVIDENCIAS = Path(__file__).resolve().parent.parent / "uploads" / "evidencias"

def _obligatoria(nombre: str) -> str:
    valor = os.environ.get(nombre)
    if not valor:
        raise RuntimeError(
            f"Falta la variable de entorno {nombre}. "

        )
    return valor

URL_DATABASE = _obligatoria("URL_DATABASE")

SECRET_KEY = _obligatoria("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
)

COOKIE_SESSION = "COOKIE_SESSION"
