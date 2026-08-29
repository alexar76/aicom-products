# Acceptance Scenarios

## Onboarding

1. **Operator navigates to login page** – The operator opens the Sentinel operator console URL and sees a login form with email and password fields.
2. **Operator enters demo credentials** – The form is prefilled with the sandbox demo email and password (from `VITE_SANDBOX_DEMO_*` env vars). The operator clicks "Sign in".
3. **Successful authentication** – The backend validates the credentials, issues a JWT stored in an HttpOnly cookie, and redirects to the operator dashboard.
4. **Dashboard loads** – The operator sees the spend summary, allowance state, wallet mode, and a paginated audit log. All sections are populated with real data (or empty states if no data exists).

## Core Action

1. **Visitor opens a page with the Sentinel embed script** – The widget renders a location form (manual entry or geolocation).
2. **Visitor enters a location** – After entering coordinates (e.g., 55.7, 37.6) and clicking "Check safety", the widget calls `GET /api/advisory?lat=55.7&lon=37.6`.
3. **Backend invokes ATLAS capabilities** – The backend calls `atlas.situation.brief@v1`, `atlas.fire.weather@v1`, and `atlas.nearest.read@v1` via the AI-market protocol, applies deterministic thresholds, and returns an advisory with hazard levels, receipts, and threshold explanations.
4. **Widget displays results** – Three hazard cards (weather, wildfire, flood) appear with level badges, measurements, distances, and evidence links. The overall status ring shows the highest level.
5. **Visitor inspects evidence** – Clicking an evidence link opens a modal with the receipt digest and timestamp, matching the audit log.

## Edge Case

1. **Invalid location input** – The visitor enters coordinates outside valid ranges (e.g., lat=200). The widget shows an inline validation error and does not submit the request.
2. **Mesh returns empty coverage** – When ATLAS responds with `ok: false` and a `refuse_reason`, the advisory shows `UNKNOWN` for each hazard with the refusal reason, and the audit log records a no-charge refusal.
3. **Rate limit exceeded** – If the same IP sends too many advisory requests, the API returns HTTP 429. The widget displays a "Too many requests – please wait" message and retries after the `Retry-After` header.

## Recovery

1. **Mesh becomes unreachable** – While the mesh is down, the advisory endpoint returns the last cached reading (if fresh) with `is_cached: true`. The widget displays "Cached reading – last read N minutes ago at HH:MM" and the status ring becomes dashed.
2. **Mesh recovers** – On the next request after the mesh is reachable again, the backend fetches fresh data, stores a new cached reading, and returns a live advisory. The widget updates automatically, the ring becomes solid, and the cached label disappears.
3. **402 payment required** – When the free allowance is exhausted, the mesh returns 402 with `quota_window` and `renews`. The widget shows the last cached advisory with a message: "Free allowance renews in {quota_window} ({renews})". The operator dashboard reflects the allowance state. No error screen is shown.
