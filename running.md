# Running CampaignOps Sentinel

This guide gets the application running from a fresh clone. The Docker route is recommended because it uses PostgreSQL, runs database migrations automatically, and matches the production-like environment.

## Requirements

- Git
- Docker Desktop (recommended), or Python 3.11+ with [`uv`](https://docs.astral.sh/uv/)

## Run with Docker

```bash
git clone https://github.com/AbhimanyuDhanwadia/campaign_ops_sentinel.git
cd campaign_ops_sentinel
cp .env.example .env
docker compose up --build -d
```

Open the interactive API documentation at [http://localhost:8000/docs](http://localhost:8000/docs).

Confirm the application is healthy:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/ready
```

Expected responses are `{"status":"ok","shadow_mode":true}` and `{"status":"ready"}`.

Stop the local stack when finished:

```bash
docker compose down
```

To remove the local PostgreSQL data as well, use `docker compose down -v`.

## Run without Docker

```bash
cp .env.example .env
uv sync --all-groups
uv run alembic upgrade head
uv run uvicorn campaign_ops_sentinel.main:app --reload
```

The local default database is `data/campaign_ops.db`; it is created automatically and ignored by Git.

## Test the project

```bash
uv run ruff check .
uv run pytest
```

## Try the workflow

Create a Shadow Mode recommendation. This only stores a local recommendation; it never creates an external ad campaign.

```bash
curl -X POST http://localhost:8000/v1/campaigns/recommendations \
  -H 'Content-Type: application/json' \
  -H 'X-Request-ID: local-demo-001' \
  -d '{
    "brand":"Pulse Energy",
    "budget_inr":500000,
    "markets":["IN"],
    "audience":"Mobile gamers aged 18 to 30",
    "objective":"attention",
    "start_date":"2026-09-01",
    "end_date":"2026-09-14",
    "formats":["video","playable"],
    "destination_url":"https://example.com/campaign"
  }'
```

Copy the `id` from the response to retrieve its recommendation, submit a human approval decision, or inspect its audit trail through `/docs`.

## Access controls

Development mode permits local requests without an API key. In production, set `APP_ENV=production` and a long, random `API_KEY`; send it with each `/v1` request as `X-API-Key`. The service refuses production startup when the key is missing.
