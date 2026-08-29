# Sentinel — user guide

## Public widget

1. Open the site (or your embed).
2. Enter a city **or** lat/lon **or** use “Use my location”.
3. Click **Get safety report**.
4. Read **Overall status** (`CALM` / `WARNING` / `EMERGENCY`) and hazard cards.
5. Open **Evidence receipt** to see the digest tying the statement to mesh data.

Location is rounded for privacy. This is **not** a forecast or insurance trigger.

## Operator console

1. Go to **Login** (demo credentials are prefilled on factory demos).
2. Open **Operator** for spend, wallet, allowance, and audit.
3. Open **Analytics** for dashboards / metrics (workspace views).

If the widget shows **UNKNOWN**, the operator usually needs to fund or reopen the AIMarket escrow channel (see [admin.md](admin.md)).

## Embed on your site

```html
<script src="https://<your-sentinel-host>/api/embed.js"></script>
```

The embed uses the same `/api/advisory` path as the full app.
