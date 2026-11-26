"""DTO (contratos) con Pydantic. Equivalen a los records de Contracts/Contratos.cs.

Pydantic valida al recibir el JSON: si falta un campo o el tipo es incorrecto,
FastAPI responde 422 antes de entrar al endpoint (como [ApiController] en .NET).
alias_generator=to_camel hace que el JSON viaje en camelCase (fechaUtc), igual que .NET.
"""
from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class Contrato(BaseModel):
    """Base común: JSON en camelCase y se acepta también el nombre Python."""
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class SaludoRequest(Contrato):
    nombre: str = Field(min_length=2, max_length=50, description="Nombre de quien saluda")


class SaludoResponse(Contrato):
    mensaje: str
    fecha_utc: datetime


class Operacion(str, Enum):
    SUMA = "suma"
    RESTA = "resta"
    MULTIPLICACION = "multiplicacion"
    DIVISION = "division"


class CalculoRequest(Contrato):
    a: Decimal
    b: Decimal
    operacion: Operacion


class CalculoResponse(Contrato):
    resultado: Decimal
    expresion: str


class OpcionCatalogo(Contrato):
    clave: str
    texto: str
    mensaje: str
