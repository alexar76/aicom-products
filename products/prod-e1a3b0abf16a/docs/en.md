# Relay — Operator & Developer Guide

This guide covers how to run, configure, test, and troubleshoot Relay locally
and on Vercel. The README is the landing page; this document is the
operator manual.

## Architecture (1 minute)

- **Backend** — FastAPI modular monolith under `backend/app/`. SQLite via
  SQLAlchemy 2.x. Argon2id passwords, signed session cookies, CSRF on
  state-changing routes.
- **Frontend** — React 18 + Vite SPA under `frontend/src/`. Calls the API on
  the same origin at `/api/*`.
- **Embed** — standalone `/embed.js` (≤15KB gzipped) that fetches
  `/api/public/handoffs/{token}` and renders a "Human-verified" badge.
- **Migrations** — Alembic; first revision `0001_init` creates the full
  schema. The app also calls `init_db()` on boot for the sandbox so a fresh
  clone boots with zero external infrastructure.

```
relay/
├── api/index.py            Vercel ASGI mount at /api/*
├── backend/app/            FastAPI app (auth, handoffs, public, workspace)
├── backend/alembic/        Migrations
├── backend/tests/          unit / integration / e2e
├── frontend/src/           React SPA
├── frontend/embed/         Standalone embed widget (built to public/embed.js)
├── public/                 Vite build output for Vercel static hosting
├── docs/                   Bilingual guides, OpenAPI, schemas, gallery
└── .github/workflows/      CI + release
```

## Environment variables

| Var | Default | Purpose |
| --- | --- | --- |
| `RELAY_DB_PATH` | `./.data/relay.db` | SQLite file path (volume-mounted in compose) |
| `SESSION_SECRET` | dev placeholder | Signs session cookies + CSRF tokens (≥ 16 chars; ≥ 32 in prod) |
| `CORS_ORIGIN` | `http://localhost:5173` | Allowed origin for the Vite dev server |
| `METIS_VERIFY_URL` | unset | When set, `/verify` calls Metis; otherwise local rule engine |
| `REDIS_URL` | unset | Optional Redis for rate-limit + session cache |
| `SANDBOX_DEMO_EMAIL` | `[email protected]` | Seeded on first boot |
| `SANDBOX_DEMO_PASSWORD` | `RelayDemo!2025` | Seeded on first boot |
| `VITE_DEMO_EMAIL` | unset | SPA prefills the login form when set |
| `VITE_DEMO_PASSWORD` | unset | SPA prefills the login form when set |
| `API_HOST_PORT` | `8000` | Compose host port for the API |
| `WEB_HOST_PORT` | `5173` | Compose host port for the web |
| `REDIS_HOST_PORT` | `6379` | Compose host port for Redis |
| `SHARE_RATE_LIMIT_PER_MIN` | `60` | Per-IP cap on `/share/*` and `/embed.js` |

## Run locally

```bash
cp .env.example .env
docker compose up -d --build
# API:      http://localhost:8000
# Web:      http://localhost:5173
# Health:   http://localhost:8000/healthz
# OpenAPI:  http://localhost:8000/openapi.json
```

The seed step creates one operator + workspace + three handoffs
(pending/approved/rejected) so the inbox and share page are non-empty on
first boot.

### Run the backend without Docker

```bash
cd backend
pip install -e .[dev]
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload --port 8000
```

### Run the frontend without Docker

```bash
cd frontend
npm install
npm run dev
```

## Test pyramid

```bash
# 1. Component / unit tests (≥60% coverage floor)
cd backend && pytest tests/unit -q --cov=app --cov-fail-under=60

# 2. Functional / integration tests (HTTP + SQLite)
cd backend && pytest tests/integration -q

# 3. UI e2e (Playwright)
cd frontend && npx playwright test
```

The full API surface is also exported to `docs/openapi.json` and validated
against `docs/receipts.schema.json` in the e2e test.

## State machine

`pending → (verify) → approved | rejected`

- `approve` is **always explicit** — there is no implicit auto-approve.
- If any verification item fails, the handoff is left in `pending` until the
  operator explicitly approves (override) or rejects.
- `/share/{token}` returns **404** for any handoff that is not `approved`.

## Receipt

Per-handoff JSON receipts include:

- `handoff_id`, `created_at`, `approved_at`
- `operator_email`, `workspace_name`
- `verification_items[]` (category, passed, notes, reviewer_email)
- `approval_state`
- `content_sha256` (over the **approved** text)
- `share_url`
- `verification_source` (`local` | `metis` | `unavailable`)
- `audit[]` (full timeline entries with actor + timestamp)

The shape is validated against `docs/receipts.schema.json` in tests.

## Embed widget

```html
<script src="https://relay.example/embed.js?token=ABC..." async></script>
<!-- iframe fallback for strict CSPs -->
<iframe src="https://relay.example/embed.html?token=ABC..."
        width="220" height="48" frameborder="0" loading="lazy"
        title="Human-verified by {workspace}"></iframe>
```

- Inherits the workspace accent color via a CSS custom property fallback.
- On 404 / 429 / network error: renders neutral "Verification unavailable"
  and logs to the console — never throws.

## Troubleshooting

- **API returns 500 on first boot** — the SQLite directory does not exist.
  `mkdir -p ./.data` and re-run.
- **Login form is empty in the sandbox** — set `VITE_DEMO_EMAIL` and
  `VITE_DEMO_PASSWORD` in `.env` and rebuild the SPA.
- **CSRF 403 on approve / reject** — the SPA fetches `/api/auth/csrf` on
  bootstrap and stores the token in a `<meta name="csrf-token">` tag. If
  the tag is missing the request is rejected; reload the page.
- **Public share 404s unexpectedly** — only `approved` handoffs are visible.
  Pending and rejected return 404 by design (no information disclosure).
- **Rate-limit 429** — default is 60 req/min/IP. Bump
  `SHARE_RATE_LIMIT_PER_MIN` or wait one minute.

## Versioning

Relay follows [SemVer](https://semver.org/). v0.1.0 is the initial MVP cut.
