from datetime import datetime

from pydantic import BaseModel


class ModelDefinitionResponse(BaseModel):
    name: str
    model_type: str
    features: list[str]
    target_features: list[str]


class TrainedInstanceResponse(BaseModel):
    filter_key: str
    trained_at: datetime
    metrics: dict[str, float]
    artifact_uri: str
    row_count: int
