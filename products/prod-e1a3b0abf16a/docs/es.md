# Relay — Guía de Operador y Desarrollador

Esta guía cubre cómo ejecutar, configurar, probar y depurar Relay en local y
en Vercel. El README es la página de aterrizaje; este documento es el manual
de operador.

## Arquitectura (1 minuto)

- **Backend** — monolito modular FastAPI en `backend/app/`. SQLite vía
  SQLAlchemy 2.x. Contraseñas con Argon2id, cookies de sesión firmadas,
  CSRF en rutas que cambian estado.
- **Frontend** — SPA React 18 + Vite en `frontend/src/`. Llama a la API en
  el mismo origen en `/api/*`.
- **Embed** — `/embed.js` independiente (≤15KB gzip) que consulta
  `/api/public/handoffs/{token}` y renderiza un sello "Verificado por
  humanos".
- **Migraciones** — Alembic; la primera revisión `0001_init` crea todo el
  esquema. La app también llama a `init_db()` al arrancar para el sandbox,
  de modo que un clone fresco arranca sin infraestructura externa.

## Variables de entorno

| Var | Por defecto | Propósito |
| --- | --- | --- |
| `RELAY_DB_PATH` | `./.data/relay.db` | Ruta del archivo SQLite (volumen en compose) |
| `SESSION_SECRET` | marcador de dev | Firma cookies y tokens CSRF (≥ 16 chars; ≥ 32 en prod) |
| `CORS_ORIGIN` | `http://localhost:5173` | Origen permitido para el dev server de Vite |
| `METIS_VERIFY_URL` | sin definir | Si está definida, `/verify` llama a Metis; si no, motor local |
| `REDIS_URL` | sin definir | Redis opcional para rate-limit y caché de sesión |
| `SANDBOX_DEMO_EMAIL` | `[email protected]` | Operador sembrado al primer arranque |
| `SANDBOX_DEMO_PASSWORD` | `RelayDemo!2025` | Contraseña sembrada al primer arranque |
| `VITE_DEMO_EMAIL` | sin definir | La SPA rellena el formulario si está definida |
| `VITE_DEMO_PASSWORD` | sin definir | La SPA rellena el formulario si está definida |
| `API_HOST_PORT` | `8000` | Puerto host de compose para la API |
| `WEB_HOST_PORT` | `5173` | Puerto host de compose para la web |
| `REDIS_HOST_PORT` | `6379` | Puerto host de compose para Redis |
| `SHARE_RATE_LIMIT_PER_MIN` | `60` | Tope por IP para `/share/*` y `/embed.js` |

## Ejecutar en local

```bash
cp .env.example .env
docker compose up -d --build
# API:      http://localhost:8000
# Web:      http://localhost:5173
# Health:   http://localhost:8000/healthz
# OpenAPI:  http://localhost:8000/openapi.json
```

El seed crea un operador + workspace + tres handoffs (pendiente, aprobado,
rechazado) para que la bandeja y la página pública nunca estén vacías.

### Backend sin Docker

```bash
cd backend
pip install -e .[dev]
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload --port 8000
```

### Frontend sin Docker

```bash
cd frontend
npm install
npm run dev
```

## Pirámide de tests

```bash
# 1. Componente / unidad (suelo de cobertura ≥60%)
cd backend && pytest tests/unit -q --cov=app --cov-fail-under=60

# 2. Funcional / integración (HTTP + SQLite)
cd backend && pytest tests/integration -q

# 3. UI e2e (Playwright)
cd frontend && npx playwright test
```

La superficie completa de la API se exporta a `docs/openapi.json` y se
valida contra `docs/receipts.schema.json` en el test e2e.

## Máquina de estados

`pending → (verify) → approved | rejected`

- `approve` es **siempre explícito** — no hay auto-aprobación implícita.
- Si algún ítem de verificación falla, el handoff queda en `pending` hasta
  que el operador apruebe (override) o rechace de forma explícita.
- `/share/{token}` devuelve **404** para cualquier handoff que no esté
  `approved`.

## Recibo

Los recibos JSON por handoff incluyen:

- `handoff_id`, `created_at`, `approved_at`
- `operator_email`, `workspace_name`
- `verification_items[]` (category, passed, notes, reviewer_email)
- `approval_state`
- `content_sha256` (sobre el texto **aprobado**)
- `share_url`
- `verification_source` (`local` | `metis` | `unavailable`)
- `audit[]` (timeline con actor y timestamp)

La forma se valida contra `docs/receipts.schema.json` en los tests.

## Widget embed

```html
<script src="https://relay.example/embed.js?token=ABC..." async></script>
<!-- iframe de respaldo para CSPs estrictos -->
<iframe src="https://relay.example/embed.html?token=ABC..."
        width="220" height="48" frameborder="0" loading="lazy"
        title="Verificado por humanos por {workspace}"></iframe>
```

- Hereda el color de acento del workspace.
- En 404 / 429 / error de red: renderiza "Verificación no disponible" y
  registra en consola — nunca lanza excepciones.

## Solución de problemas

- **La API devuelve 500 al primer arranque** — el directorio de SQLite no
  existe. Ejecuta `mkdir -p ./.data` y reintenta.
- **El formulario de login está vacío en el sandbox** — define
  `VITE_DEMO_EMAIL` y `VITE_DEMO_PASSWORD` en `.env` y reconstruye la SPA.
- **CSRF 403 al aprobar / rechazar** — la SPA obtiene `/api/auth/csrf` al
  arrancar y guarda el token en una etiqueta `<meta name="csrf-token">`. Si
  la etiqueta falta, la petición se rechaza; recarga la página.
- **El share público devuelve 404** — sólo los handoffs `approved` son
  visibles. Pendientes y rechazados devuelven 404 por diseño.
- **429 por rate-limit** — el límite por defecto es 60 req/min/IP. Sube
  `SHARE_RATE_LIMIT_PER_MIN` o espera un minuto.

## Versionado

Relay sigue [SemVer](https://semver.org/). v0.1.0 es el corte inicial del
MVP.
