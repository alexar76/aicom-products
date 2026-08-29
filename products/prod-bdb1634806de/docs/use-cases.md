# Sentinel — use cases

## Who it is for

| Audience | Why Sentinel |
|----------|----------------|
| **Travel / events sites** | Show live weather / wildfire / flood posture near a venue with a verifiable receipt |
| **Real-estate / local portals** | Embed “safety now” without shipping an LLM that hallucinates risk |
| **Ops / safety desks** | Operator view of mesh spend and audit when serving many lookups |
| **Developers** | Paid ATLAS mesh via Hub escrow — same rails as other AIMarket agents |

## Who it is not for

- Insurance underwriting or regulatory “all clear”
- Long-range weather forecasts
- Any product that needs free unlimited mesh without an escrow budget

## Example journeys

1. **Visitor on a festival landing** → embed widget → Berlin coordinates → `EMERGENCY` with receipt → share digest with ops.
2. **Site operator** → login → check daily spend vs budget after a traffic spike → reopen escrow before TTL.
3. **Partner site** → drop `embed.js` → same advisory API, no custom backend.

## Mesh capabilities used

- `atlas.situation.brief@v1`
- `atlas.fire.weather@v1`
- `atlas.nearest.read@v1` (when layered)

Paid through Hub escrow on Base; receipts come back on successful invokes.
