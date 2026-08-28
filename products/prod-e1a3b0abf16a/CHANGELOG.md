# Changelog

All notable changes to Relay are documented in this file. The format is based
on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] — 2025-01-15

### Added
- Operator authentication (email + Argon2id password, HTTP-only session cookies, CSRF).
- Paste-AI-Draft intake with client / project / source-AI-tool metadata.
- Skeptic verification pass: claims, sources, tone, risk — local heuristics by default, optional Metis adapter.
- Operator inbox with pending / approved / rejected tabs and one-click approve & reject.
- Branded public share page at `/share/{token}` (404 for pending/rejected — no information disclosure).
- JSON receipt export validated against `docs/receipts.schema.json`.
- Embeddable verification widget (`<script>` + `<iframe>` fallback) for third-party sites.
- Workspace branding (name, logo URL, accent color) with HTTPS-only validation and free-tier gating.
- Per-handoff audit timeline written in the same transaction as every state transition.
- Rate limiting on `/share/*` and `/embed.js` (60 req/min/IP) with 429 + `Retry-After`.
- Health check `/healthz` with DB ping; OpenAPI at `/openapi.json`.
- Vite + React SPA, FastAPI modular monolith, Alembic migrations, Docker Compose for local dev.
- Bilingual docs (English + Español), local SVG badges, CI workflow with coverage floor.
