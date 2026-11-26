"""Interfaces de negocio con typing.Protocol (equivalen a Interfaces/IServicios.cs).

Protocol es "duck typing" verificado por el analizador de tipos: cualquier clase con
esos métodos cumple la interfaz, sin heredar de ella. Los routers dependen de estas
interfaces, no de las clases concretas, para poder cambiarlas en pruebas.
"""
from typing import Protocol

from app.contratos import CalculoRequest, CalculoResponse, OpcionCatalogo, SaludoResponse


class ISaludoService(Protocol):
    def saludar(self, nombre: str) -> SaludoResponse: ...


class ICalculadoraService(Protocol):
    def calcular(self, req: CalculoRequest) -> CalculoResponse: ...


class ICatalogoService(Protocol):
    async def obtener_lenguajes(self) -> list[OpcionCatalogo]: ...
