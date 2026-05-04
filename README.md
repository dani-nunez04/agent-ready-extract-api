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

