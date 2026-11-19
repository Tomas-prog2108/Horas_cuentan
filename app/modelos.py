from datetime import datetime
from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class Usuario(BaseModel):

    id: int
    identificacion: str
    rol: str


class UsuarioEnBD(Usuario):
    
    contrasena_hasheada: str
    creado_en: datetime | None = None

class ProyectoForm(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    descripcion: str = ""
    horas: Decimal = Field(gt=0, max_digits=5, decimal_places=2)
    fecha_inicio: date
    lugar: str = Field(min_length=1, max_length=100)
    cupos: int = Field(ge=0)
    estado: Literal["activo", "inactivo"] = "activo"