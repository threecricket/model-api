# Model API

FastAPI service for cricket model training and inference. Reads match data from the ingestion Postgres schema, computes delivery-level features on demand for training, and serves batch predictions from S3-stored model artifacts.

## Setup

```bash
cp .env.example .env
# Edit .env with your DATABASE_URL and AWS credentials (or AWS_ROLE_ARN for STS assume-role)

uv sync --group dev
```

## Run

```bash
uv run uvicorn main:app --app-dir src --reload
```

## Tests

```bash
uv run pytest
```

## API

### Health check

```bash
curl http://localhost:8000/health
```

### List model definitions

Returns registered algorithm templates (features, model type, targets):

```bash
curl http://localhost:8000/models
```

### List trained instances

Shows artifacts saved for a model, keyed by `filter_key`:

```bash
curl http://localhost:8000/models/batting_team_win_probability/trained
```

### Train

Train separate instances per filter scope. T20 and ODI are saved under different `filter_key` values even though they share the same model name.

**T20:**

```bash
curl -X POST http://localhost:8000/train \
  -H "Content-Type: application/json" \
  -d '{
    "model": "batting_team_win_probability",
    "options": {
      "filters": { "format": ["t20"] },
      "hyperparams": { "C": 1.0, "class_weight": "balanced" },
      "test_size": 0.2
    }
  }'
```

**ODI:**

```bash
curl -X POST http://localhost:8000/train \
  -H "Content-Type: application/json" \
  -d '{
    "model": "batting_team_win_probability",
    "options": {
      "filters": { "format": ["odi"] },
      "hyperparams": { "C": 1.0, "class_weight": "balanced" },
      "test_size": 0.2
    }
  }'
```

Example response:

```json
{
  "model": "batting_team_win_probability",
  "filter_key": "format:t20",
  "filters": { "format": ["t20"] },
  "metrics": { "accuracy": 0.81, "log_loss": 0.42 },
  "rows_used": 125000,
  "artifact_uri": "s3://threecricket-models/models/batting_team_win_probability/format:t20/latest.pkl"
}
```

Re-training with identical filters overwrites the artifact at that `filter_key`.

> **Note:** Test matches have no fixed ball limit (`current_innings_legal_balls_remaining` is 0). Exclude `test` format unless you explicitly want it.

### Predict

Identify the trained instance via `filters` (canonicalized to `filter_key`) or pass `filter_key` from a prior train response. Input features must be batch-aligned lists — index `i` across all features is sample `i`.

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "model": "batting_team_win_probability",
    "filters": { "format": ["t20"] },
    "input": {
      "current_innings_runs": [45, 120],
      "current_innings_wickets": [1, 4],
      "current_innings_legal_ball_no": [30, 100],
      "current_innings_legal_balls_remaining": [91, 21],
      "current_innings_target": [160, 180],
      "current_innings_runs_required": [115, 60],
      "striker_current_runs": [22, 45],
      "striker_current_balls_faced": [18, 30],
      "bowler_current_runs": [28, 55],
      "bowler_current_balls_bowled": [30, 100],
      "bowler_current_wickets": [1, 3]
    }
  }'
```

Example response:

```json
{
  "model": "batting_team_win_probability",
  "filter_key": "format:t20",
  "predictions": [0.72, 0.31],
  "probabilities": [[0.28, 0.72], [0.69, 0.31]]
}
```

Returns 404 if no artifact exists for the `(model, filter_key)` pair — use `GET /models/{name}/trained` to see available instances.

## Models

| Name | Type | Target |
|------|------|--------|
| `batting_team_win_probability` | `sklearn.logistic_regression` | `batting_team_won` |

Features are computed from pre-delivery cumulative ball state (runs, wickets, batter/bowler stats, innings target). The `batting_team_won` label is `1.0` when the batting team is the match winner; ties and no-results are `0.0`.
