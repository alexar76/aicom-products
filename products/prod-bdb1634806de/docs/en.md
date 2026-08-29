# Sentinel — operator & developer guide

Sentinel is an LLM-free safety companion. A visitor (or embed) asks “is it safe here right now?” for weather / wildfire / flood. The answer comes from **paid ATLAS capabilities** on AIMarket (Hub escrow on Base) and is shaped by **deterministic thresholds**. Every statement can carry a **signed evidence receipt**.

## Architecture (short)

```
Browser / embed.js
    → FastAPI /api/advisory
        → AimarketParticipant.invoke (escrow channel)
            → Hub → ATLAS (atlas.situation.brief@v1, fire.weather@v1, nearest.read@v1)
        → RuleEngine → hazard levels + receipt digest
```

## Environment

| Variable | Role |
|----------|------|
| `AIMARKET_HUB_URL` | Hub base (e.g. `https://modelmarket.dev`) |
| `AIMARKET_WALLET_ADDRESS` / `AIMARKET_WALLET_KEY` | Base wallet that opens escrow |
| `AIMARKET_ESCROW_CHANNEL` | On-chain channel id (`bytes32`) |
| `AIMARKET_PAYMENT_CHANNEL` / `_SECRET` | Hub payment channel binding |
| `AIMARKET_ESCROW_CONTRACT` | Escrow contract on Base |
| `AIMARKET_ESCROW_HUB_ADDRESS` | Hub address allowed to settle |

Escrow **MIN_DEPOSIT is $1 USDC**. Channels expire (~24h). When the channel is closed or underfunded, advisory returns `UNKNOWN` / `insufficient balance`.

## Run locally

```bash
# backend
cd backend && pip install -e ".[dev]" && uvicorn app.main:app --reload --port 8000

# frontend
cd frontend && npm install && npm run dev
```

Or `docker compose up -d --build`.

## Tests

```bash
cd backend && pytest tests/unit -v --cov=app --cov-fail-under=60
cd backend && pytest tests/integration -v
cd frontend && npm run test:unit
cd frontend && npm run e2e
```

## Ops: escrow reopen

On the factory host:

```bash
python3 scripts/reopen_product_escrow_channel.py prod-bdb1634806de --deposit 1.0
# then republish so Vercel mesh_env picks up the new channel
python3 scripts/publish_product_now.py prod-bdb1634806de
```

Wallet must hold ≥ $1 USDC + a little ETH for gas on Base.

## Related docs

- [Admin guide](admin.md) — deploy, keys, budgets, audit
- [User guide](user-guide.md) — widget & operator UI
- [Use cases](use-cases.md) — who this is for
