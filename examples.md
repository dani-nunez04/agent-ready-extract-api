# Examples (real URLs)

These examples are meant to validate the API quickly in Vercel or locally.

## 1) Health

- `GET /api/v1/health`

## 2) Extract (good/simple HTML)

### example.com

```bash
curl -sS -X POST "https://<your-vercel-domain>/api/v1/extract" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com","options":{"include_text":true,"include_title":true,"include_links":true}}'
```

### httpbin.org/html

```bash
curl -sS -X POST "https://<your-vercel-domain>/api/v1/extract" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://httpbin.org/html","options":{"include_text":true,"include_title":true,"include_links":true}}'
```

## 3) Extract (docs)

### FastAPI docs

```bash
curl -sS -X POST "https://<your-vercel-domain>/api/v1/extract" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://fastapi.tiangolo.com/","options":{"include_text":true,"include_title":true,"include_links":false}}'
```

## 4) Known limitations / failure modes

- Some sites block automated requests or return non-HTML responses.
- Very large pages may hit serverless limits (timeout/response size).
- Extraction quality varies depending on page structure.

