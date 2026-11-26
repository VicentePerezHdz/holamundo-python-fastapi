"""Punto de entrada (equivale a Program.cs): crea la app, registra middlewares, errores y routers.

Correr:  .venv\\Scripts\\python -m uvicorn app.main:app --reload --port 8000
Swagger: http://localhost:8000/docs     Página: http://localhost:8000/
"""
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.errores import registrar_manejadores
from app.routers.endpoints import calculadora_router, catalogos_router, saludo_router

app = FastAPI(title="Hola Mundo FastAPI", version="1.0.0")

# CORS: permite que Angular (4200) y React (5173) llamen a esta API desde el navegador.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

registrar_manejadores(app)
app.include_router(saludo_router)
app.include_router(calculadora_router)
app.include_router(catalogos_router)

# La página HTML se sirve al final para que no tape las rutas /api.
app.mount("/", StaticFiles(directory=Path(__file__).parent / "static", html=True), name="static")
