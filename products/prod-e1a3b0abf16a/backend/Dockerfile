FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps for argon2-cffi and healthcheck
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl gcc \
 && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
COPY backend ./backend
COPY api ./api
COPY alembic.ini ./

RUN pip install --upgrade pip \
 && pip install -e . \
 && pip install -e .[dev] || true

ENV RELAY_DB_PATH=/data/relay.db
EXPOSE 8000

# Run migrations then start uvicorn. `seed.py` is idempotent.
CMD ["sh", "-c", "alembic upgrade head || true; python -m app.seed || true; uvicorn app.main:app --host 0.0.0.0 --port 8000"]
