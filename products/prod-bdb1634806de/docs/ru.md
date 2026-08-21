# Sentinel Документация

Sentinel — встраиваемый безопасный компаньон для погодных, пожарных и наводнении опасностей. Не использует LLM; вместо этого вызывает возможности ATLAS sensor-mesh через протокол AI-market и применяет детерминированные пороги.

## Архитектура

- Backend FastAPI (Python 3.11)
- SQLAlchemy + Alembic для хранения (SQLite/PostgreSQL)
- Frontend React + TypeScript + Vite
- Опционально Redis для кэша
- Docker Compose для локальной разработки

## Переменные окружения
(аналогично английской версии)

## Запуск

```bash
docker compose up -d --build
```

API на http://localhost:8000, frontend на http://localhost:3000.

## Тесты

```bash
cd backend && pytest tests/unit -v --cov=app --cov-report=term-missing --cov-fail-under=60
cd backend && pytest tests/integration -v
cd frontend && npm run test:unit -- --coverage
cd frontend && npm run e2e
```

## Устранение неполадок

- Если ATLAS hub недоступен, advisory возвращает UNKNOWN.
- Ошибки heartbeat логируются, но не влияют на UI.
