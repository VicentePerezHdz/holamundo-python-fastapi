"""Routers (equivalen a los Controllers de .NET): traducen HTTP <-> objetos. Sin lógica de negocio."""
from typing import Annotated

from fastapi import APIRouter, Depends

from app.contratos import (
    CalculoRequest, CalculoResponse, OpcionCatalogo, SaludoRequest, SaludoResponse,
)
from app.dependencias import (
    obtener_calculadora_service, obtener_catalogo_service, obtener_saludo_service,
)
from app.services.interfaces import ICalculadoraService, ICatalogoService, ISaludoService

saludo_router = APIRouter(prefix="/api/saludo", tags=["Saludo"])
calculadora_router = APIRouter(prefix="/api/calculadora", tags=["Calculadora"])
catalogos_router = APIRouter(prefix="/api/catalogos", tags=["Catálogos"])

# Annotated + Depends: "este parámetro lo llena el contenedor de dependencias".
SaludoDep = Annotated[ISaludoService, Depends(obtener_saludo_service)]
CalculadoraDep = Annotated[ICalculadoraService, Depends(obtener_calculadora_service)]
CatalogoDep = Annotated[ICatalogoService, Depends(obtener_catalogo_service)]


@saludo_router.get("", response_model=SaludoResponse)
def saludo_get(servicio: SaludoDep) -> SaludoResponse:
    return servicio.saludar("Mundo")


@saludo_router.post("", response_model=SaludoResponse)
def saludo_post(req: SaludoRequest, servicio: SaludoDep) -> SaludoResponse:
    return servicio.saludar(req.nombre)


@calculadora_router.post("", response_model=CalculoResponse)
def calcular(req: CalculoRequest, servicio: CalculadoraDep) -> CalculoResponse:
    return servicio.calcular(req)


@catalogos_router.get("/lenguajes", response_model=list[OpcionCatalogo])
async def lenguajes(servicio: CatalogoDep) -> list[OpcionCatalogo]:
    # async def: mientras espera la "BD", el servidor atiende otras peticiones.
    return await servicio.obtener_lenguajes()
