from datetime import datetime

from pydantic import BaseModel


class Usuario(BaseModel):

    id: int
    identificacion: str
    rol: str


class UsuarioEnBD(Usuario):
    
    contrasena_hasheada: str
    creado_en: datetime | None = None