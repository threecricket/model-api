# Model API

FastAPI service for cricket model training and inference.

## Setup

```bash
cp .env.example .env
# Edit .env with your DATABASE_URL and AWS credentials

uv sync
```

## Run

```bash
uv run uvicorn main:app --app-dir src --reload
```

## Health check

```bash
curl http://localhost:8000/health
```
