"""Implementaciones de negocio. No saben nada de HTTP: se prueban llamándolas directo."""
import asyncio
from collections.abc import Callable
from datetime import datetime, timezone
from decimal import ROUND_HALF_UP, Decimal

from app.contratos import (
    CalculoRequest, CalculoResponse, OpcionCatalogo, Operacion, SaludoResponse,
)
from app.errores import ReglaNegocioError


class SaludoService:
    # El reloj se inyecta (como TimeProvider en .NET) para poder fijar la hora en pruebas.
    def __init__(self, reloj: Callable[[], datetime] = lambda: datetime.now(timezone.utc)) -> None:
        self._reloj = reloj

    def saludar(self, nombre: str) -> SaludoResponse:
        limpio = nombre.strip()
        return SaludoResponse(mensaje=f"¡Hola, {limpio}! Saludo desde FastAPI.", fecha_utc=self._reloj())


SIMBOLOS = {
    Operacion.SUMA: "+", Operacion.RESTA: "−",
    Operacion.MULTIPLICACION: "×", Operacion.DIVISION: "÷",
}


class CalculadoraService:
    """Usa Decimal (como decimal en C#) para no perder precisión: 0.1 + 0.2 = 0.3 exacto."""

    def calcular(self, req: CalculoRequest) -> CalculoResponse:
        a, b = req.a, req.b
        match req.operacion:  # match/case: el "switch" de Python 3.10+
            case Operacion.SUMA:
                r = a + b
            case Operacion.RESTA:
                r = a - b
            case Operacion.MULTIPLICACION:
                r = a * b
            case Operacion.DIVISION:
                if b == 0:
                    raise ReglaNegocioError("No se puede dividir entre cero.")
                r = (a / b).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
        r = r.normalize() if r != 0 else Decimal(0)
        texto = lambda d: format(d.normalize(), "f")  # noqa: E731  sin notación científica
        return CalculoResponse(resultado=r, expresion=f"{texto(a)} {SIMBOLOS[req.operacion]} {texto(b)} = {texto(r)}")


class CatalogoService:
    _LENGUAJES = [
        OpcionCatalogo(clave="python", texto="Python / FastAPI", mensaje="APIs rápidas con tipado y validación automática."),
        OpcionCatalogo(clave="pyspark", texto="PySpark / Databricks", mensaje="Procesamiento de datos a gran escala sobre Delta Lake."),
        OpcionCatalogo(clave="csharp", texto="C# / .NET 8", mensaje="La misma API, en el proyecto 01."),
        OpcionCatalogo(clave="react", texto="React", mensaje="Frontend que puede consumir esta API o la de .NET."),
    ]

    async def obtener_lenguajes(self) -> list[OpcionCatalogo]:
        await asyncio.sleep(0.05)  # simula una consulta asíncrona a base de datos
        return list(self._LENGUAJES)
