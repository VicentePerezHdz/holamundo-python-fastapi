# Hola Mundo · Python + FastAPI

La misma API del proyecto .NET, hecha en Python con FastAPI y Pydantic, más una página HTML que la consume. Tiene tres funciones: saludo con input de texto, calculadora y combobox con mensaje.

## Qué demuestra
- Routers, servicios detrás de interfaces e inyección de dependencias con `Depends`.
- Validación con Pydantic.
- Errores con el mismo formato `ProblemDetails` que .NET.
- CORS y pruebas con `TestClient`.

## Cómo correrlo
```powershell
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000   # http://localhost:8000
python -m pytest -v                                   # 14 pruebas
```

La explicación completa está en [`docs/Documento_Transicion.md`](docs/Documento_Transicion.md).
