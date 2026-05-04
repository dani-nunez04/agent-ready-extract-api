# agent-ready-extract-api

API para **extraer contenido limpio y metadatos** de páginas web públicas en JSON (FastAPI en Vercel).

## What this API does

- Fetches a **public URL** and returns: **title**, **description**, **headings**, **clean text**, and **normalized links**
- No logins, no CAPTCHAs, no proxies, no evasion

## Use cases

- **RAG / indexing**: convert HTML into clean text + headings
- **Monitoring**: hash extracted text to detect meaningful changes
- **Research**: quickly capture title/description/links from docs/blogs

## Requisitos

- Python **3.12**

## Deploy en Vercel (Python + FastAPI)

- **Entrypoint para Vercel**: `api/index.py` (exporta `app` importada desde `app/main.py`)
- **Rutas**: `vercel.json` enruta todo a la Function, por lo que siguen funcionando:
  - `GET /api/v1/health`
  - `POST /api/v1/extract`

### Paso a paso (primer deploy)

1. **Sube el repo a GitHub**
   - Crea un repositorio y sube este proyecto.

2. **Importa el proyecto en Vercel**
   - En Vercel, “Add New…” → “Project” → selecciona el repo.
   - Vercel detectará `vercel.json` y usará `api/index.py` como Function.

3. **Configura variables de entorno (si hace falta)**
   - En el proyecto de Vercel → “Settings” → “Environment Variables”.
   - Variables soportadas (todas opcionales porque tienen defaults):
     - `API_TITLE`
     - `API_DESCRIPTION`
     - `API_VERSION`
     - `LOG_LEVEL`
     - `CORS_ALLOW_ORIGINS` (lista separada por comas, o vacío para desactivar CORS)

4. **Despliega**
   - Pulsa “Deploy” (o mergea a la rama configurada para Production).

5. **Prueba `GET /api/v1/health`**
   - Abre tu dominio de Vercel y visita:
     - `/api/v1/health`

6. **Prueba `POST /api/v1/extract`**
   - En Vercel (o local) envía un JSON como:

```json
{
  "url": "https://example.com",
  "options": { "include_text": true, "include_title": true, "include_links": true }
}
```

Respuesta (ejemplo de forma):

```json
{
  "url": "https://example.com",
  "fetch": {
    "fetched_at": "2026-01-01T00:00:00Z",
    "final_url": "https://example.com",
    "status_code": 200,
    "content_type": "text/html; charset=UTF-8"
  },
  "result": {
    "title": "Example Domain",
    "description": null,
    "headings": ["Example Domain"],
    "text": "Example Domain ...",
    "links": [{ "href": "https://www.iana.org/domains/example", "text": "More information..." }]
  }
}
```

Limitaciones (serverless) y notas:

- No usamos Docker, workers ni tareas en background.
- La API es request/response y está pensada para correr como Function.
- **Timeouts**: si la web objetivo es lenta, `/extract` puede fallar por timeout en entorno serverless.
- **Cold starts**: la primera petición puede ser más lenta.
- **Dependencias nativas**: `lxml` puede fallar si no hay wheel compatible en el entorno (es el riesgo principal).
- **CORS**: configúralo vía `CORS_ALLOW_ORIGINS` (evita `*` con credenciales).

## Endpoints

- `GET /api/v1/health`
- `POST /api/v1/extract`

### Checklist “antes de hacer deploy”

- [ ] Existe `api/index.py` y exporta `app`.
- [ ] `vercel.json` existe y enruta `/(.*)` a `api/index.py`.
- [ ] `requirements.txt` contiene solo dependencias necesarias (sin Docker/Playwright/DB).
- [ ] `CORS_ALLOW_ORIGINS` está vacío (desactivado) o configurado con orígenes concretos.
- [ ] Has probado `/api/v1/health` (local o tras deploy).
- [ ] Para `/api/v1/extract`, usas URLs públicas y asumes límites serverless (timeouts/tamaño).

## Setup (Windows / PowerShell)

Crear y activar un entorno virtual:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instalar dependencias:

```powershell
pip install -r requirements.txt
```

Configurar variables de entorno (opcional):

```powershell
copy .env.example .env
```

## Ejecutar el servidor

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Probar el healthcheck

En el navegador o con `curl`:

- `GET http://127.0.0.1:8000/api/v1/health`

Ejemplo con PowerShell:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/v1/health
```

Respuesta esperada:

```json
{"status":"ok","version":"0.1.0"}
```

