# Auction Platform — API

A real-time online auction backend: create and schedule auctions, bid with race-safe
concurrency control, get live updates over WebSocket. Built as a **modular monolith** designed
so its module boundaries can become real service boundaries later without a rewrite — see
[`docs/architecture.md`](docs/architecture.md) for the reasoning.

## Stack

FastAPI · SQLAlchemy (async) + PostgreSQL · Redis (locks + Celery broker) · Celery (scheduled
tasks) · RabbitMQ (`aio-pika`, domain event bus) · JWT auth · Pydantic v2 · Alembic ·
Sentry · Prometheus/Grafana · pytest

## Architecture at a glance

- **Domain-driven, hexagonal-ish**: `domain/` (aggregates, rules, events) →
  `application/` (use cases, handlers) → `infrastructure/` (repositories, adapters) →
  `routers/` (HTTP/WebSocket), per module (`auction`, `bidding`, `users`, `auth`,
  `notifications`).
- **Event-driven between modules**: a change publishes a domain event; anything that needs to
  react (update a read model, send an e-mail, push a WebSocket message) subscribes to it —
  producer and consumer never import each other directly.
- **Two processes**: `api` (FastAPI) and `worker` (Celery, for time-based auction transitions),
  connected through a real message broker (RabbitMQ) — not just an in-memory pub/sub — so an
  event published by one is actually seen by the other.

Full write-up: [`docs/architecture.md`](docs/architecture.md) · business rules:
[`docs/business-rules.md`](docs/business-rules.md) · event catalog:
[`docs/domain-events.md`](docs/domain-events.md) · module boundaries:
[`docs/bounded-contexts.md`](docs/bounded-contexts.md) · API shape:
[`docs/api-contracts.md`](docs/api-contracts.md).

## Getting started

```bash
cp .env.example .env   # adjust SECRET_KEY/JWT_*_SECRET at least
docker compose up -d
```

That starts everything: `api` (`:8000`), `worker`, `postgres`, `redis`, `rabbitmq`, `mailpit`
(fake SMTP for dev), `prometheus`, `grafana`. The `api`/`worker` containers reconcile their own
dependencies against `pyproject.toml`/`uv.lock` on every start (`uv sync`), so a plain
`docker compose up -d` after adding a dependency is enough — no manual rebuild step.

Check it's alive: `curl http://localhost:8000/health`.

## Running locally without Docker (for the API process only)

Needs `uv`, plus Postgres/Redis reachable — either via `docker compose up -d postgres redis` (in
which case override `DATABASE_URL`/`REDIS_URL` to point at `localhost` and the published ports
below) or your own instances.

```bash
uv sync
uv run alembic upgrade head
uv run uvicorn main:app --reload
```

## Tests

```bash
uv run pytest
```

The suite forces `EVENT_BUS_PROVIDER=memory`, `SENTRY_DSN=""`, `EMAIL_PROVIDER=console` (see
`conftest.py`) — it never depends on RabbitMQ, Sentry, or a real SMTP server being up, only on
Postgres/Redis (`docker compose up -d postgres redis`, with `DATABASE_URL`/`REDIS_URL` pointed
at `localhost` if running outside Docker).

## Where things live once running

| Service | URL | Notes |
|---|---|---|
| API docs (Swagger) | http://localhost:8000/docs | also `/redoc` |
| Grafana | http://localhost:3010 | dashboards over `/metrics` |
| Prometheus | http://localhost:9090 | |
| RabbitMQ management | http://localhost:15672 | `guest`/`guest` locally |
| Mailpit | http://localhost:8025 | dev inbox, nothing ever really sent |

## Environment variables

See [`.env.example`](.env.example) — every variable is documented inline, including which ones
are optional (Sentry, e-mail provider, event bus provider) and what each value switches.

## Roadmap

Traces (OpenTelemetry + Jaeger) and a pluggable payment gateway (hexagonal, Stripe → Mercado
Pago) are next — ask the maintainer for the current priority order.
