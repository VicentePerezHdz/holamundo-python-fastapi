# Documento de transición: Hola Mundo Python (FastAPI)

> Manual para entender qué se construyó y qué hace cada módulo, clase, función e interfaz.
> Fecha: 2026-11-23 · Ruta: `C:\HolaMundo\04-Python`
> Es **la misma API** del proyecto 01 (.NET 8), escrita en Python, con las mismas rutas, el mismo JSON y los mismos errores. Por eso Angular o React podrían usar cualquiera de las dos cambiando solo la URL.

## 1. Qué hace

| Pantalla (`http://localhost:8000/`) | Llamada | Qué hace Python |
|---|---|---|
| Saludo: input de texto | `POST /api/saludo` `{ "nombre": "Vicente" }` | Pydantic valida de 2 a 50 caracteres; el servicio arma el saludo |
| Calculadora: 2 números + select | `POST /api/calculadora` `{ "a": 10, "b": 5, "operacion": "suma" }` | calcula con `Decimal`; 400 si divides entre 0 |
| Combobox | `GET /api/catalogos/lenguajes` | lista de opciones (`async`) |

Swagger se genera solo en `http://localhost:8000/docs`.

## 2. Cómo correrlo

```powershell
cd C:\HolaMundo\04-Python
.venv\Scripts\activate                       # activa el entorno virtual (el prompt muestra "(.venv)")
pip install -r requirements.txt              # solo la primera vez o en otra máquina
python -m uvicorn app.main:app --reload --port 8000
python -m pytest -v                          # 14 pruebas
```

Si el `.venv` se daña o no existe: `python -m venv .venv` y vuelve a instalar los requisitos. (Eso pasó al crear este proyecto: el primer `.venv` quedó con archivos corruptos porque la sesión se cortó a la mitad.)

Versiones fijadas en `requirements.txt`: FastAPI 0.115, Pydantic **2.11** (la 2.12 o mayor saca avisos con esta versión de FastAPI), Uvicorn 0.32, pytest 8, httpx 0.28. Python 3.12.

## 3. Arquitectura

```
┌───────────── Navegador ─────────────┐
│ static/index.html (JS sin framework)│
└──────────────────┬──────────────────┘
                   │ fetch /api/...
┌──────────────────▼─────────────── Uvicorn (servidor ASGI) ──────────────────────────────┐
│ main.py: FastAPI() → CORSMiddleware → manejadores de errores → routers → StaticFiles     │
│                                                                                           │
│ routers/endpoints.py        dependencias.py (Depends + lru_cache)    services/            │
│  saludo_post ───────────────► obtener_saludo_service() ───────────► SaludoService         │
│  calcular ──────────────────► obtener_calculadora_service() ──────► CalculadoraService    │
│  lenguajes (async) ─────────► obtener_catalogo_service() ─────────► CatalogoService       │
│        ▲ valida con                                tipados contra services/interfaces.py  │
│ contratos.py (Pydantic, camelCase)                 (ISaludoService, … con Protocol)       │
│ errores.py: ReglaNegocioError / validación / inesperado ──► ProblemDetails (JSON)         │
└───────────────────────────────────────────────────────────────────────────────────────────┘
```

Equivalencias con .NET:

| .NET 8 (proyecto 01) | Python (este) |
|---|---|
| `Program.cs` | `app/main.py` |
| `Contracts/Contratos.cs` (records + DataAnnotations) | `app/contratos.py` (Pydantic `BaseModel` + `Field`) |
| `Interfaces/IServicios.cs` | `app/services/interfaces.py` (`typing.Protocol`) |
| `Services/*.cs` | `app/services/servicios.py` |
| `AddScoped<ISaludoService, SaludoService>()` | `app/dependencias.py` + `Depends(...)` |
| Controllers | `app/routers/endpoints.py` (`APIRouter`) |
| `ManejadorErroresGlobal` + `ReglaNegocioException` | `app/errores.py` |
| `TimeProvider` inyectado | parámetro `reloj` de `SaludoService` |
| xUnit `[Theory]` / `WebApplicationFactory` | `@pytest.mark.parametrize` / `TestClient` |
| Kestrel | Uvicorn |

## 4. Recorrido de una petición (Saludo con nombre inválido)

1. En la página escribes "V" y das clic en **Saludar**. El JS hace `fetch POST /api/saludo` con `{ "nombre": "V" }`.
2. Uvicorn recibe la petición y FastAPI la enruta a `saludo_post`.
3. Antes de ejecutar la función, FastAPI convierte el JSON en `SaludoRequest`. `Field(min_length=2)` falla y lanza `RequestValidationError`.
4. El manejador `validacion` de `errores.py` lo convierte en `400` con `{ "errors": { "nombre": ["String should have at least 2 characters"] } }` y `content-type: application/problem+json`.
5. El JS junta los mensajes de `errors` y los pinta en rojo.

Con un nombre válido: FastAPI llama `obtener_saludo_service()` (siempre la misma instancia gracias a `lru_cache`), se la pasa a `saludo_post`, el servicio devuelve `SaludoResponse` y FastAPI la serializa en camelCase (`fechaUtc`) por el `alias_generator`.

## 5. Inventario de módulos, clases y funciones

| Archivo | Miembros | Responsabilidad |
|---|---|---|
| `app/main.py` | `app` | Crea FastAPI, CORS (4200 y 5173), errores, routers y la página estática |
| `app/contratos.py` | `Contrato` (base camelCase), `SaludoRequest`, `SaludoResponse`, `Operacion` (Enum), `CalculoRequest`, `CalculoResponse`, `OpcionCatalogo` | Forma y validación del JSON |
| `app/errores.py` | `ReglaNegocioError`, `registrar_manejadores(app)` con `regla_negocio`, `validacion`, `inesperado` | Todo error sale como ProblemDetails; el 500 no expone detalles |
| `app/services/interfaces.py` | `ISaludoService.saludar`, `ICalculadoraService.calcular`, `ICatalogoService.obtener_lenguajes` | Contratos de negocio |
| `app/services/servicios.py` | `SaludoService(reloj)`, `CalculadoraService` (`match/case`, `Decimal`, `SIMBOLOS`), `CatalogoService` (`async`) | Reglas de negocio, sin HTTP |
| `app/dependencias.py` | `obtener_saludo_service`, `obtener_calculadora_service`, `obtener_catalogo_service` | Fábricas singleton para `Depends` |
| `app/routers/endpoints.py` | `saludo_get`, `saludo_post`, `calcular`, `lenguajes`; alias `SaludoDep`, `CalculadoraDep`, `CatalogoDep` | Endpoints HTTP |
| `app/static/index.html` | `pedir()`, `pintar()` | Página para probar sin Angular ni React |
| `tests/test_api.py` | 14 pruebas | 5 operaciones, división entre 0, reloj inyectado, camelCase, 400 de validación, catálogo, reemplazo de dependencia, CORS, página |
| `requirements.txt` | versiones fijas | Instalación repetible |

## 6. Conceptos clave

| Concepto | Dónde | En una frase |
|---|---|---|
| Entorno virtual | `.venv` | Dependencias aisladas por proyecto, como `node_modules` |
| Type hints | todo el código | Python sigue siendo dinámico, pero FastAPI y el editor usan los tipos para validar y autocompletar |
| Pydantic | `contratos.py` | Clases que validan y convierten datos al construirse |
| `Depends` | `endpoints.py` | Inyección de dependencias de FastAPI; se reemplaza con `dependency_overrides` en pruebas |
| `Protocol` | `interfaces.py` | Interfaz estructural: cumple quien tenga los métodos |
| `async def` / `await` | `lenguajes`, `CatalogoService` | Mientras espera IO, el servidor atiende otras peticiones (como async/await en C#) |
| `def` normal en FastAPI | `saludo_post`, `calcular` | FastAPI lo corre en un hilo aparte para no bloquear |
| `Decimal` vs `float` | `CalculadoraService` | `0.1 + 0.2` da `0.3` exacto (hay una prueba para eso) |
| `match/case` | `CalculadoraService` | El `switch` de Python 3.10+ |
| `lru_cache` | `dependencias.py` | Memoriza el resultado: singleton sencillo |
| ASGI / Uvicorn | `main.py` | El servidor que ejecuta la app (como Kestrel) |
| ProblemDetails | `errores.py` | Mismo formato de error que .NET para que el frontend no cambie |
| pytest | `tests/` | Funciones `test_*`, `assert` simple y `parametrize` |

Python también se usa mucho para **datos** (PySpark en notebooks de Databricks). Eso se practica en el proyecto `03-Portafolio-Pedidos`. Este proyecto cubre la base del lenguaje y las APIs.

## 7. Paso a paso para volver a hacer el proyecto

1. `mkdir C:\HolaMundo\04-Python; cd C:\HolaMundo\04-Python`
2. `python -m venv .venv` y `.venv\Scripts\activate`
3. `pip install "fastapi==0.115.*" "uvicorn[standard]==0.32.*" "pydantic==2.11.*" "pytest==8.*" "httpx==0.28.*"` y luego `pip freeze > requirements.txt`
4. Crea las carpetas `app`, `app/services`, `app/routers`, `app/static`, `tests`, cada paquete con su `__init__.py`.
5. Escribe, en este orden y probando cada uno: `contratos.py` → `errores.py` → `services/interfaces.py` → `services/servicios.py` → `dependencias.py` → `routers/endpoints.py` → `main.py`.
6. `python -m uvicorn app.main:app --reload` y prueba en `/docs`.
7. `static/index.html` y vuelve a abrir `/`.
8. `tests/test_api.py` → `python -m pytest -v`.

## 8. Plantilla para una HU nueva ("como usuario quiero despedirme")

1. `contratos.py`: `DespedidaResponse`.
2. `interfaces.py`: `despedir(self, nombre: str) -> DespedidaResponse` en `ISaludoService`.
3. `servicios.py`: impleméntalo en `SaludoService`.
4. `endpoints.py`: `@saludo_router.post("/despedida")`.
5. Prueba unitaria y de integración en `tests/`.
6. Documento de transición de la HU con las secciones 3, 4 y 5.

## 9. Problemas comunes

| Síntoma | Causa | Solución |
|---|---|---|
| `ModuleNotFoundError: No module named 'app'` | corres desde otra carpeta | ejecuta desde `C:\HolaMundo\04-Python` con `python -m ...` |
| `ModuleNotFoundError: fastapi` | no activaste el `.venv` | `.venv\Scripts\activate` o usa `.venv\Scripts\python` |
| `SyntaxError: source code string cannot contain null bytes` al usar pip | `.venv` corrupto | borra `.venv` y créalo de nuevo |
| Muchos `UnsupportedFieldAttributeWarning` | Pydantic 2.12+ con FastAPI 0.115 | usa Pydantic 2.11 (ya fijado) |
| Un `DeprecationWarning` de `anyio` en pytest | viene de Starlette, no del proyecto | se puede ignorar |
| 422 en lugar de 400 | se quitó el manejador `validacion` | FastAPI responde 422 por defecto; aquí se cambió a 400 para igualar a .NET |
| `Address already in use` | otro Uvicorn en el puerto 8000 | ciérralo o usa `--port 8001` |
