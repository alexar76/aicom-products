# Sentinel — admin guide

For operators who deploy and fund the live product.

## What you own

1. **Vercel (or equivalent) deploy** of backend + SPA.
2. **AIMarket escrow channel** on Base (≥ $1 USDC, ~24h TTL).
3. **Demo operator login** (seeded) for `/#/operator` and analytics.
4. **Budget / spend** visibility via `/api/operator/*`.

## Deploy checklist

1. Backend deps include `eth-account`, `eth-utils`, `PyJWT` (mesh signing + auth).
2. Inject mesh env at publish time (`AIMARKET_*` from `data/state/<pid>/aimarket_participant.env`).
3. After deploy, probe:

```bash
curl -sS 'https://<host>/api/health'
curl -sS 'https://<host>/api/advisory?lat=52.52&lon=13.4'
# expect overall.level ≠ UNKNOWN and overall.receipt set when channel is funded
```

4. Login as demo operator → Operator → confirm wallet truncated address and spend counters move after live advisories.

## Funding & channel lifecycle

| Symptom | Cause | Fix |
|---------|-------|-----|
| `UNKNOWN` / `insufficient balance` | Channel depleted or Hub balance too low | Reopen escrow with ≥ $1 USDC, republish |
| `escrow channel not open on chain` | Expired (~24h) or wrong channel id | `reopen_product_escrow_channel.py` |
| Soft mesh / trial fallback | Escrow closed; Hub trial visitor | Prefer paid channel; trial is not production |

**Never** commit wallet keys. Keep them only in factory `data/state/…/aimarket_participant.env` and the host secret store.

## Security notes

- Location is rounded (~1 decimal degree); do not log exact GPS.
- CORS must not combine `allow_origins=["*"]` with credentials in production.
- Rotate demo passwords before any customer-facing handoff.

## Audit

`GET /api/operator/audit` lists capability invokes. Empty audit with rising `advisories_served` usually means counters updated without persist — treat as a bug to fix, not as “mesh is off”.
