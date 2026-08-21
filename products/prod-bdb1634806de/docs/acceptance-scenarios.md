# Sentinel Acceptance Scenarios

This document defines end-to-end acceptance scenarios for Sentinel. Each scenario is named with a `##` heading and includes the steps a user takes. These scenarios are used by QA to validate the product against the specification.

## Onboarding

- A new operator navigates to the Sentinel operator console.
- The operator clicks "Sign in" and enters the seeded demo credentials (operator@sentinel.local / SentinelDemo123!).
- The system validates the credentials, hashes the password, and creates a secure session.
- The operator is redirected to the dashboard, which shows the audit log, spend summary, and allowance state.
- The operator can now access all authenticated endpoints (analytics, operator data, etc.).

## Core Action

- A visitor opens a web page that has the Sentinel embed script installed.
- The visitor either grants browser geolocation or manually enters a city / coordinates.
- The widget calls the public advisory endpoint with the rounded location.
- The Sentinel backend invokes ATLAS capabilities (atlas.situation.brief@v1, atlas.fire.weather@v1, atlas.nearest.read@v1).
- The deterministic rule engine computes hazard levels for weather, wildfire, and flood.
- The widget displays the overall status, three hazard cards with evidence receipts, and the "how this was decided" panel.

## Edge Case

- The visitor enters invalid coordinates (e.g., lat=999, lon=999).
- The widget displays an inline validation error and prompts re-entry.
- The visitor submits a location with no ATLAS coverage.
- The backend receives an `ok:false` refusal and the widget shows UNKNOWN with the refusal reason.
- The widget never shows CALM on missing data, and no error stack trace is visible.

## Recovery

- The visitor's session encounters an ATLAS mesh outage (unreachable host).
- The widget falls back to the last cached advisory for that rounded location.
- The UI labels the reading as "Cached reading — last read N minutes ago" and shows the timestamp.
- The widget also displays a plain sentence about the free allowance renewal, read from the 402 response body when applicable.
- Once connectivity is restored, the next manual refresh retries the ATLAS invocation and updates the widget to a live reading.

## Analytics/BI API Coverage

The following Analytics/BI endpoints must be implemented and covered by the scenarios above (at least one scenario exercises each):

- `POST /api/datasets`
- `POST /api/metrics`
- `POST /api/dashboards`
- `GET /api/dashboards/{id}/data`
- `GET /api/dashboards/{id}/export`

These endpoints are used by the operator console to create datasets, define metrics, build dashboards, fetch dashboard data, and export the dashboard view.