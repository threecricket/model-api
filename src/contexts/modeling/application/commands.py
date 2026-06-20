from dataclasses import dataclass


@dataclass(frozen=True)
class TrainModelCommand:
    model_name: str
    options: dict


@dataclass(frozen=True)
class TrainModelResult:
    model: str
    filter_key: str
    filters: dict
    metrics: dict[str, float]
    rows_used: int
    artifact_uri: str


@dataclass(frozen=True)
class RunModelCommand:
    model_name: str
    input_features: dict[str, list[float]]
    filters: dict | None = None
    filter_key: str | None = None


@dataclass(frozen=True)
class RunModelResult:
    model: str
    filter_key: str
    predictions: list[float]
    probabilities: list[list[float]] | None = None


@dataclass(frozen=True)
class ListTrainedModelsCommand:
    model_name: str | None = None
