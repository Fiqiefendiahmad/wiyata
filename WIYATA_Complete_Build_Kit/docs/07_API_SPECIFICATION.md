# API Specification

Base path: `/api/v1`

Use versioned Pydantic request/response models. All errors should use a consistent structure with a machine-readable code, safe message, and correlation ID.

## Query endpoints

- `POST /query/generate`
- `POST /query/convert`
- `POST /query/explain`
- `POST /query/validate`
- `POST /query/optimize`
- `POST /query/execute`

## Sandbox endpoints

- `POST /sandboxes`
- `GET /sandboxes`
- `GET /sandboxes/{sandbox_id}`
- `POST /sandboxes/{sandbox_id}/start`
- `POST /sandboxes/{sandbox_id}/reset`
- `POST /sandboxes/{sandbox_id}/execute`
- `POST /sandboxes/{sandbox_id}/export`
- `DELETE /sandboxes/{sandbox_id}`

## Connection and metadata endpoints

- `GET /connections`
- `POST /connections`
- `POST /connections/{connection_id}/test`
- `DELETE /connections/{connection_id}`
- `GET /connections/{connection_id}/schemas`
- `GET /connections/{connection_id}/tables`
- `GET /connections/{connection_id}/columns`

## Knowledge endpoints

- `GET /knowledge/categories`
- `GET /knowledge/articles`
- `GET /knowledge/articles/{slug}`
- `GET /knowledge/search`
- `GET /knowledge/engines`
- `GET /knowledge/references`

## Professional tools endpoints

- `GET /tools`
- `GET /tools/{slug}`
- `GET /tools/categories`
- `GET /tools/compare`

## Learning endpoints

- `GET /learning/roles`
- `GET /learning/paths`
- `GET /learning/paths/{slug}`
- `GET /learning/exercises/{slug}`
- `POST /learning/exercises/{slug}/submit`

## Library endpoints

- `GET /library/queries`
- `POST /library/queries`
- `PATCH /library/queries/{id}`
- `DELETE /library/queries/{id}`

## Example generation request

```json
{
  "engine": "postgres",
  "engine_version": "17",
  "schema_reference": "schema_opaque_id",
  "request": "Show the ten customers with the highest transaction total in the last 30 days",
  "options": {
    "include_explanation": true,
    "include_warnings": true,
    "include_comments": false
  },
  "language": "en"
}
```

## Example response

```json
{
  "status": "success",
  "engine": "postgres",
  "query": "SELECT ...",
  "explanation": [],
  "warnings": [],
  "validation": {
    "parser_valid": true,
    "database_validated": false
  },
  "execution": {
    "executed": false
  }
}
```

## API rules

- Never return connection secrets.
- Use opaque IDs, not internal paths.
- Enforce authorization at every resource boundary.
- Rate-limit expensive AI, sandbox, and execution endpoints.
- Use idempotency keys for environment creation where appropriate.
- Return explicit capability errors.
- Do not claim database validation if only parser validation occurred.
