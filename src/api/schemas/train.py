from pydantic import BaseModel, Field


class TrainRequest(BaseModel):
    model: str
    options: dict = Field(default_factory=dict)


class TrainResponse(BaseModel):
    model: str
    filter_key: str
    filters: dict
    trained: bool
    rows_used: int
    metrics: dict[str, float] = Field(default_factory=dict)
    artifact_uri: str | None = None
    message: str | None = None
