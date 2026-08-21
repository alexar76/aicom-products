# Sentinel Documentation

Sentinel is an embeddable safety companion for weather, wildfire, and flood hazards. It uses no LLM; instead, it invokes ATLAS sensor-mesh capabilities via the AI-market protocol and applies deterministic thresholds.

## Architecture

- FastAPI backend (Python 3.11)
- SQLAlchemy + Alembic for persistence (SQLite/PostgreSQL)
- React + TypeScript + Vite frontend
- Optional Redis for caching
- Docker Compose for local development

## Environment Variables

- `DATABASE_URL` (default `sqlite:///./sentinel.db`)
- `ATLAS_BASE_URL` - AI-market hub URL
- `ATLAS_AGENT_KEY` - key for AI-market invokes
- `AICOM_REGISTRY_URL` - factory registry for heartbeat
- `SENTINEL_AGENT_KEY` - key for registry heartbeat
- `SANDBOX_DEMO_EMAIL` / `SANDBOX_DEMO_PASSWORD` - demo user seeds
- `SENTINEL_DAILY_INVOKE_BUDGET_USD`
- `WALLET_ENABLED`, `WALLET_ADDRESS`, `WALLET_CHAIN`

## Run

```bash
docker compose up -d --build
```

Access API at http://localhost:8000, frontend at http://localhost:3000.

## Tests

```bash
cd backend && pytest tests/unit -v --cov=app --cov-report=term-missing --cov-fail-under=60
cd backend && pytest tests/integration -v
cd frontend && npm run test:unit -- --coverage
cd frontend && npm run e2e
```

## Troubleshooting

- If ATLAS hub is unreachable, advisory returns UNKNOWN.
- Heartbeat failures are logged but do not affect UI.
