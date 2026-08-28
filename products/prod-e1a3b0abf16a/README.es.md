# Relay — Mesa de Entrega Verificada

> Pega un borrador de IA. Pasa un filtro escéptico. Envía una entrega verificada por humanos a tu cliente en menos de 90 segundos.

> 🌐 [English](README.md) · [Español](README.es.md)

<!-- aicom-readme-badges -->
<p align="left">
  <img src="docs/badges/ci.svg" alt="CI" />
  <img src="docs/badges/coverage.svg" alt="cobertura" />
  <img src="docs/badges/license.svg" alt="Licencia: MIT" />
  <img src="docs/badges/tests.svg" alt="tests" />
</p>
<!-- /aicom-readme-badges -->

<p align="center"><img src="docs/gallery/hero.svg" alt="Héroe de Relay — un sello de lacre sobre una carta de entrega en papel" width="820"></p>

## Galería

| Imagen | Pie |
| ------ | --- |
| `docs/gallery/hero.svg` | Héroe con sello de lacre: una entrega de IA notarizada, lista para enviar. |
| `docs/gallery/01-inbox.svg` | Bandeja del operador: pendientes, aprobadas y rechazadas en tres columnas de libro mayor. |
| `docs/gallery/02-share.svg` | Página pública de compartir: sello "Verificado por humanos" + franja de acento. |
| `docs/gallery/03-embed.svg` | Widget de verificación embebible: señal de confianza para el sitio del cliente. |

## Qué es

Relay es una **Mesa de Entrega Verificada** para agencias, consultorías y profesionales independientes que envían entregables asistidos por IA a clientes. La persona operadora pega un borrador de IA, ejecuta un **filtro escéptico** estructurado (afirmaciones, fuentes, tono, riesgo), aprueba o rechaza en una bandeja, y luego publica una página `/share/{token}` con marca propia o incrusta un widget **Verificado por humanos** en el sitio del cliente. Cada aprobación lleva un recibo JSON a prueba de manipulaciones que los equipos de compliance aceptan sin más preguntas.

## Qué no es

- No es un detector de IA. No puntuamos "¿esto es IA?": registramos una revisión humana que puedes demostrar.
- No es una plataforma GRC empresarial. No hay pipeline SOC 2, ni registro de riesgos, ni biblioteca de políticas.
- No es un sustituto de Notion/Docs. La entrega es el artefacto; el resto de tu trabajo vive donde ya vive.

## Inicio rápido (local)

```bash
# 1. Clonar y entrar
cd relay

# 2. Configurar
cp .env.example .env

# 3. Levantar la API y la SPA
docker compose up -d --build

# 4. Abrir
open http://localhost:5173          # consola del operador (Vite)
open http://localhost:8000/healthz  # liveness de la API
```

El stack de compose levanta **api** (FastAPI en `:8000`), **web** (Vite dev en `:5173`) y un **redis** opcional para rate limiting y caché de sesión. La base de datos SQLite se monta como volumen en `./.data/relay.db` y se migra automáticamente al arrancar. Se siembra un operador demo para que puedas iniciar sesión de inmediato.

**Credenciales demo del sandbox** (también precargadas en el formulario de login cuando `VITE_DEMO_EMAIL` / `VITE_DEMO_PASSWORD` están definidos):

```
email:    [email protected]
password: RelayDemo!2025
```

## Tests

Ejecuta la pirámide de tests en orden:

```bash
# 1. Tests de componente / unidad en el backend (con cobertura)
cd backend && pytest tests/unit -q --cov=app --cov-fail-under=60

# 2. Tests funcionales / de integración (HTTP + SQLite, sin navegador)
cd backend && pytest tests/integration -q

# 3. Tests end-to-end de UI (Playwright)
cd frontend && npx playwright test
```

## Documentación

- [English](docs/en.md) · [Español](docs/es.md)
- [Esquema OpenAPI 3.1](docs/openapi.json)
- [Esquema del recibo JSON](docs/receipts.schema.json)
- [CHANGELOG](CHANGELOG.md) · [SECURITY](SECURITY.md) · [CONTRIBUTING](CONTRIBUTING.md)

## Licencia

[MIT](LICENSE) — consulta el texto completo en `LICENSE`.
