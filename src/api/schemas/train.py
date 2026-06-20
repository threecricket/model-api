from pydantic import BaseModel, Field


class TrainRequest(BaseModel):
    model: str
    options: dict = Field(default_factory=dict)


class TrainResponse(BaseModel):
    model: str
    filter_key: str
    filters: dict
    metrics: dict[str, float]
    rows_used: int
    artifact_uri: str
