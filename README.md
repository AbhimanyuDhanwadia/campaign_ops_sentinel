# CampaignOps Sentinel

A portfolio-grade, safety-first agentic workflow for gaming-ad operations. It transforms a validated campaign brief into a policy-reviewed inventory recommendation while operating in **Shadow Mode**: the application never creates or changes an external campaign.

## What works now

- FastAPI API with typed campaign brief and approval contracts.
- Durable PostgreSQL/SQLite persistence for recommendations and append-only audit events.
- Alembic database migrations plus health and readiness endpoints.
- API-key protection for all `/v1` endpoints when `API_KEY` is configured; production startup refuses to run without one.
- Shadow-mode recommendation flow with explicit human approval; live campaign mutations are deliberately not implemented.
- Agent instruction files (`agents/*/SKILL.md`) defining boundaries for future LLM-backed agents.
- Automated tests for normal, invalid, policy-blocked, persistent, audit, and approval paths.

## Local setup

```bash
cp .env.example .env
uv sync --all-groups
uv run uvicorn campaign_ops_sentinel.main:app --reload
```

Open `http://127.0.0.1:8000/docs` to try the API.

Run checks:

```bash
uv run ruff check .
uv run pytest
```

## Docker environment

```bash
cp .env.example .env
docker compose up --build
```

This starts the API and a local PostgreSQL instance. Docker Compose overrides the development SQLite URL with the PostgreSQL service URL. The OpenAPI interface is available at `http://127.0.0.1:8000/docs`.

## Production configuration

Set these values in your secret manager or deployment environment, never in Git:

```text
APP_ENV=production
API_KEY=<long-random-service-key>
DATABASE_URL=postgresql+psycopg://<user>:<password>@<host>:5432/<database>
SHADOW_MODE=true
```

Run the migration before serving traffic:

```bash
alembic upgrade head
```

`/health` is a liveness check; `/ready` verifies database connectivity. All live integration credentials and mutation endpoints remain intentionally absent until a source-of-truth campaign API and explicit operational approval policy are available.

## Example request

```bash
curl -X POST http://127.0.0.1:8000/v1/campaigns/recommendations \
  -H 'Content-Type: application/json' \
  -d '{"brand":"Pulse Energy","budget_inr":500000,"markets":["IN"],"audience":"Mobile gamers aged 18 to 30","objective":"attention","start_date":"2026-09-01","end_date":"2026-09-14","formats":["video","playable"],"destination_url":"https://example.com/campaign"}'
```

## Deliberate next additions

1. Replace the synthetic inventory service with an authenticated MCP/REST connector.
2. Add an LLM-backed intake agent behind a provider interface; retain schema validation and policy checks in deterministic code.
3. Add trace export, evaluation datasets, and trace grading before enabling an LLM provider for production traffic.
4. Integrate enterprise identity/role management instead of the service-level API key used by this baseline.

## Safety invariants

- Shadow Mode is enabled by default.
- Policy gates are deterministic and run before planning.
- Every external mutation remains unimplemented pending explicit approval, credentials, and integration testing.
- Uploaded brief content must be treated as untrusted data.
