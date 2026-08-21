# aicom-products

Selective catalog of **full** products built by [AI-Factory](https://github.com/alexar76/aicom).

Each subdirectory under `products/` is one factory product id (`prod-…`), published on demand — not every pipeline run, and never the whole monorepo.

## Layout

```
products/<product_id>/   # full product tree (source + docs; no node_modules / .venv)
```

## Publish

From the factory monorepo:

```bash
GH_PAT=… ./scripts/publish_factory_product_catalog.sh \
  --product prod-XXXXXXXXXXXX --from-factory-host
```

Auth: `GH_PAT` for **alexar76**. Remote: `https://github.com/alexar76/aicom-products.git`.
