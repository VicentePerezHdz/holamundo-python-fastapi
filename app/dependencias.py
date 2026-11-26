"""Registro de dependencias (equivale a builder.Services.AddScoped<...> en Program.cs).

FastAPI inyecta con Depends(funcion): llama a la función y pasa el resultado al endpoint.
lru_cache convierte la función en "singleton": siempre devuelve la misma instancia.
En pruebas se reemplaza con app.dependency_overrides[obtener_x] = lambda: falso.
"""
from functools import lru_cache

from app.services.interfaces import ICalculadoraService, ICatalogoService, ISaludoService
from app.services.servicios import CalculadoraService, CatalogoService, SaludoService


@lru_cache
def obtener_saludo_service() -> ISaludoService:
    return SaludoService()


@lru_cache
def obtener_calculadora_service() -> ICalculadoraService:
    return CalculadoraService()


@lru_cache
def obtener_catalogo_service() -> ICatalogoService:
    return CatalogoService()
