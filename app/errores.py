"""Manejo consistente de errores: todo sale como ProblemDetails (RFC 7807).

Equivale a ReglaNegocioException + ManejadorErroresGlobal del proyecto .NET.
Así Angular, React o cualquier cliente leen los errores igual sin importar el backend.
"""
import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

log = logging.getLogger("holamundo")
PROBLEM_JSON = "application/problem+json"


class ReglaNegocioError(Exception):
    """Error de negocio esperado (por ejemplo, dividir entre cero) -> HTTP 400."""


def registrar_manejadores(app: FastAPI) -> None:
    @app.exception_handler(ReglaNegocioError)
    async def regla_negocio(request: Request, exc: ReglaNegocioError) -> JSONResponse:
        return JSONResponse(
            status_code=400, media_type=PROBLEM_JSON,
            content={"title": "Regla de negocio", "status": 400, "detail": str(exc),
                     "instance": request.url.path},
        )

    @app.exception_handler(RequestValidationError)
    async def validacion(request: Request, exc: RequestValidationError) -> JSONResponse:
        # Mismo formato que .NET: errors = { "campo": ["mensaje", ...] }
        errores: dict[str, list[str]] = {}
        for e in exc.errors():
            campo = ".".join(str(p) for p in e["loc"] if p != "body") or "body"
            errores.setdefault(campo, []).append(e["msg"])
        return JSONResponse(
            status_code=400, media_type=PROBLEM_JSON,
            content={"title": "Uno o más errores de validación.", "status": 400,
                     "errors": errores, "instance": request.url.path},
        )

    @app.exception_handler(Exception)
    async def inesperado(request: Request, exc: Exception) -> JSONResponse:
        log.exception("Error no controlado en %s", request.url.path)
        # Nunca se expone el detalle interno al cliente.
        return JSONResponse(
            status_code=500, media_type=PROBLEM_JSON,
            content={"title": "Error interno", "status": 500, "instance": request.url.path},
        )
