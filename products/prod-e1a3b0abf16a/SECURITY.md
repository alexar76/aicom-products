# Security

## Reporting a vulnerability

Please **do not** open a public issue for suspected vulnerabilities. Email
**[email protected]** (or your usual Relay security contact) with a
description, reproduction steps, and impact. We aim to acknowledge reports
within 3 business days.

We follow responsible disclosure: we will work with you on a fix timeline
before any public write-up, and we credit reporters in the CHANGELOG unless
you prefer to remain anonymous.

## Threat model summary

- **Authentication**: Argon2id password hashing; HTTP-only, `Secure`,
  `SameSite=Lax` session cookies with 7-day expiry; CSRF tokens on
  state-changing requests.
- **Authorization**: every query is scoped to the operator's workspace; tenant
  isolation is enforced in services, not just routes.
- **Information disclosure**: `/share/{token}` returns **404** for pending or
  rejected handoffs — no draft text leaks.
- **Rate limiting**: 60 req/min/IP on public share and embed endpoints; 429
  with `Retry-After`.
- **Content integrity**: each handoff carries a `content_sha256` over the
  approved text; receipts include the hash for tamper evidence.
- **Secrets**: no credentials are committed; `.env.example` documents env
  vars; sessions are signed with `SESSION_SECRET`.

## Supported versions

Only the latest minor release receives security fixes.
