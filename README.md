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
- Dependencias: ver `requirements.txt`

## Endpoints

- `GET /api/v1/health`
- `POST /api/v1/extract`

## RapidAPI protection (block direct Vercel calls)

If you monetize this API via **RapidAPI**, you typically want to prevent users from calling your **Vercel deployment directly** (bypassing RapidAPI billing/quotas).

This project supports a simple **shared-secret** check that allows **only RapidAPI's gateway/proxy** to call the monetized endpoint.

### What is protected

- Protected (requires header): `POST /api/v1/extract`
- Not protected: `GET /api/v1/health`
- Not protected: `GET /docs`
- Not protected: `GET /openapi.json`

### How it works

- Set an environment variable: `RAPIDAPI_PROXY_SECRET`
- Requests to `POST /api/v1/extract` must include the header `X-RapidAPI-Proxy-Secret`
- If the header is missing or does not match, the API returns **403 Forbidden**

Secure-by-default behavior:

- If `RAPIDAPI_PROXY_SECRET` is **not configured**, `POST /api/v1/extract` is **blocked** (returns **403 Forbidden**). This is intentional to avoid accidentally exposing the monetized endpoint.

### Configure in Vercel

1. Open your project in Vercel
2. Go to **Settings → Environment Variables**
3. Add:
   - Name: `RAPIDAPI_PROXY_SECRET`
   - Value: a long random secret (store it securely)
   - Environments: at least **Production** (and also Preview/Development if you use them)
4. Redeploy the project so the function picks up the new env var

On RapidAPI, configure your proxy/gateway to send:

- Header: `X-RapidAPI-Proxy-Secret: <same value as RAPIDAPI_PROXY_SECRET>`

### Test the blocking

Direct call (should be blocked):

```bash
curl -i -X POST "https://<your-vercel-domain>/api/v1/extract" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com","options":{"include_text":true}}'
```

Expected: `403 Forbidden`.

Call with header (should work):

```bash
curl -i -X POST "https://<your-vercel-domain>/api/v1/extract" \
  -H "Content-Type: application/json" \
  -H "X-RapidAPI-Proxy-Secret: <your-secret>" \
  -d '{"url":"https://example.com","options":{"include_text":true}}'
```

Health/docs remain public:

```bash
curl -i "https://<your-vercel-domain>/api/v1/health"
curl -i "https://<your-vercel-domain>/docs"
curl -i "https://<your-vercel-domain>/openapi.json"
```

## Example request

```bash
curl -sS -X POST "https://<your-domain>/api/v1/extract" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com","options":{"include_text":true,"include_title":true,"include_links":true}}'
```

## Example response (shape)

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

## Limitations

- Only **public pages**. Some sites block automated requests.
- Extraction quality depends on HTML structure.
- Serverless constraints: timeouts, cold starts, response size limits.

