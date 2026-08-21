<!-- aicom-mirror-notice -->
> **🔄 Synced from a monorepo — but with a live history.** `aicom-products` mirrors the
> canonical AI-Factory monorepo. History here is append-only (no force-push).
> **Pull requests are welcome** — merged PRs are imported back into the monorepo
> and re-synced here, so your contribution becomes canonical.
> 💬 **[Issues](https://github.com/alexar76/aicom-products/issues)** · **[Pull requests](https://github.com/alexar76/aicom-products/pulls)** both welcome.

# aicom-products

Selective catalog of **full** products built by [AI-Factory](https://github.com/alexar76/aicom).

Each subdirectory under `products/` is one factory product id (`prod-…`), published on demand — not every pipeline run, and never the whole monorepo.

GitHub: [alexar76/aicom-products](https://github.com/alexar76/aicom-products)

## Layout

```
products/<product_id>/   # full product tree (source + docs; no node_modules / .venv)
```

## Publish (like other satellites)

Shell / docs (this folder → GitHub), preserving existing `products/`:

```bash
GH_PAT=… ./scripts/publish_all_repos.sh --satellite aicom-products
# or: ./scripts/mirror_satellites.sh --satellite aicom-products
```

Selective full product tree from the factory host:

```bash
GH_PAT=… ./scripts/publish_factory_product_catalog.sh \
  --product prod-XXXXXXXXXXXX --from-factory-host
```

Auth: `GH_PAT` for **alexar76**. Remote: `https://github.com/alexar76/aicom-products.git`.
Do not freestyle remotes.

## Gate

README badge row + `CONTRIBUTING.md` are required when the factory catalog gate is armed
(Settings → Product catalog + `GH_PAT` on the host). See `docs/product-catalog-github.md` in aicom.
