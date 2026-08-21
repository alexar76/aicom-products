# Sentinel
> Every safety statement is proven with a signed evidence receipt.

> 🌐 [English](README.md) · [Русский](README.ru.md)

<!-- aicom-live-url -->
**Live:** [https://prod-bdb1634806de-7r46lsaff-1-b8ae.vercel.app](https://prod-bdb1634806de-7r46lsaff-1-b8ae.vercel.app)
<!-- /aicom-live-url -->

<!-- aicom-readme-badges -->
<p align="center">
  <img src="docs/badges/ci.svg" alt="CI" />
  <img src="docs/badges/coverage.svg" alt="coverage" />
  <img src="docs/badges/license.svg" alt="License: MIT" />
  <img src="docs/badges/tests.svg" alt="tests" />
</p>
<!-- /aicom-readme-badges -->

<p align="center"><img src="docs/gallery/hero.svg" alt="Sentinel hero" width="820"></p>

## Gallery
| Still | Caption |
| ----- | ------- |
| docs/gallery/01.svg | Public widget with location form and hazard cards |
| docs/gallery/02.svg | Operator dashboard with spend and audit |

## What it is
Sentinel is an LLM-free, embeddable safety companion that answers "is it safe here right now?" for weather, wildfire, and flood hazards. It uses ATLAS sensor-mesh capabilities via AI-market protocol and deterministic thresholds.

## What it is not
Not a forecast, not an LLM opinion, not a risk rating. Every statement is tied to a signed evidence receipt.

## Quick start
```bash
docker compose up -d --build
```
API at http://localhost:8000, frontend at http://localhost:3000.

## Tests
```bash
cd backend && pytest tests/unit -v --cov=app --cov-report=term-missing --cov-fail-under=60
cd backend && pytest tests/integration -v
cd frontend && npm run test:unit -- --coverage
cd frontend && npm run e2e
```

## Docs
- [English](docs/en.md) · [Русский](docs/ru.md)

## License
MIT
