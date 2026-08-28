# Contributing to Relay

Thanks for your interest in Relay. The product is a modular FastAPI backend
with a React + Vite SPA, and the development loop is short.

## Local setup

```bash
git clone <your-fork> relay
cd relay
cp .env.example .env
docker compose up -d --build
```

The compose stack brings up the API on `:8000` and the Vite dev server on
`:5173`. SQLite is mounted at `./.data/relay.db`.

## Layout

- `backend/app/` — FastAPI app, services, routers, models, schemas, seed.
- `backend/alembic/` — schema migrations.
- `backend/tests/{unit,integration,e2e}/` — test pyramid.
- `frontend/src/` — React SPA (pages, components, styles).
- `frontend/public/embed.js` — built standalone embed widget.
- `api/index.py` — Vercel ASGI mount.
- `public/` — Vite build output for Vercel static hosting.
- `docs/` — operator guide, OpenAPI export, schemas, badges, gallery.

## Conventions

- Python: type hints everywhere; services separate from HTTP routers so core
  logic is unit-testable without a server.
- TypeScript: one page component per route, no duplicate variants.
- CSS: follow the tokens in `frontend/src/styles/tokens.css`; do not introduce
  utility-class frameworks unless the architecture already requires them.
- Tests: run the pyramid in order — `tests/unit` → `tests/integration` →
  Playwright. CI fails below 60% coverage on first-party code.
- Commits: imperative mood, ≤72-char subject (`fix: 404 on pending share`).

## Pull requests

- Open a draft PR early for visibility.
- Make sure `pytest tests/unit -q --cov=app --cov-fail-under=60` and
  `pytest tests/integration -q` are green before requesting review.
- Update `CHANGELOG.md` under `## [Unreleased]` for user-visible changes.
- Add or update tests for any new behavior — coverage is a gate, not a vanity
  metric.

## Code of conduct

Be kind. Assume good faith. Disagree on substance, not on people.
