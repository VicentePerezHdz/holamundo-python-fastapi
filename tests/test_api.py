"""Pruebas con pytest. Correr:  .venv\\Scripts\\python -m pytest -v

- Unitarias: se llama al servicio directo, sin HTTP (como CalculadoraServiceTests.cs).
- Integración: TestClient levanta la API en memoria (como WebApplicationFactory en .NET).
"""
from datetime import datetime, timezone
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.contratos import CalculoRequest, Operacion
from app.dependencias import obtener_saludo_service
from app.errores import ReglaNegocioError
from app.main import app
from app.services.servicios import CalculadoraService, SaludoService

cliente = TestClient(app)


# ---------- Unitarias ----------

@pytest.mark.parametrize(  # equivale a [Theory] + [InlineData] de xUnit
    ("a", "b", "op", "esperado"),
    [
        ("10", "5", Operacion.SUMA, "15"),
        ("10", "5", Operacion.RESTA, "5"),
        ("10", "5", Operacion.MULTIPLICACION, "50"),
        ("10", "4", Operacion.DIVISION, "2.5"),
        ("0.1", "0.2", Operacion.SUMA, "0.3"),  # con float daría 0.30000000000000004
    ],
)
def test_calculadora_operaciones(a, b, op, esperado):
    r = CalculadoraService().calcular(CalculoRequest(a=Decimal(a), b=Decimal(b), operacion=op))
    assert r.resultado == Decimal(esperado)


def test_division_entre_cero_lanza_regla_de_negocio():
    with pytest.raises(ReglaNegocioError, match="dividir entre cero"):
        CalculadoraService().calcular(CalculoRequest(a=Decimal(1), b=Decimal(0), operacion=Operacion.DIVISION))


def test_saludo_usa_el_reloj_inyectado():
    fijo = datetime(2026, 11, 23, tzinfo=timezone.utc)
    r = SaludoService(reloj=lambda: fijo).saludar("  Vicente ")
    assert r.mensaje.startswith("¡Hola, Vicente!")
    assert r.fecha_utc == fijo


# ---------- Integración ----------

def test_post_saludo_responde_en_camel_case():
    resp = cliente.post("/api/saludo", json={"nombre": "Vicente"})
    assert resp.status_code == 200
    assert set(resp.json()) == {"mensaje", "fechaUtc"}


def test_nombre_corto_devuelve_400_con_problem_details():
    resp = cliente.post("/api/saludo", json={"nombre": "V"})
    assert resp.status_code == 400
    assert resp.headers["content-type"] == "application/problem+json"
    assert "nombre" in resp.json()["errors"]


def test_division_entre_cero_devuelve_400_con_detail():
    resp = cliente.post("/api/calculadora", json={"a": 1, "b": 0, "operacion": "division"})
    assert resp.status_code == 400
    assert resp.json()["detail"] == "No se puede dividir entre cero."


def test_catalogo_de_lenguajes():
    resp = cliente.get("/api/catalogos/lenguajes")
    assert resp.status_code == 200
    assert {"clave", "texto", "mensaje"} <= set(resp.json()[0])


def test_se_puede_reemplazar_un_servicio_en_pruebas():
    class SaludoFalso:
        def saludar(self, nombre):
            return SaludoService(reloj=lambda: datetime(2000, 1, 1, tzinfo=timezone.utc)).saludar("Falso")

    app.dependency_overrides[obtener_saludo_service] = lambda: SaludoFalso()
    try:
        assert "Falso" in cliente.get("/api/saludo").json()["mensaje"]
    finally:
        app.dependency_overrides.clear()


def test_cors_permite_react():
    resp = cliente.get("/api/catalogos/lenguajes", headers={"Origin": "http://localhost:5173"})
    assert resp.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_pagina_html_se_sirve_en_la_raiz():
    resp = cliente.get("/")
    assert resp.status_code == 200
    assert "Hola Mundo FastAPI" in resp.text
