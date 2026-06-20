from pydantic import BaseModel, Field, model_validator


class PredictRequest(BaseModel):
    model: str
    input: dict[str, list[float]]
    filters: dict | None = None
    filter_key: str | None = None

    @model_validator(mode="after")
    def require_filter_resolution(self) -> "PredictRequest":
        if not self.filter_key and self.filters is None:
            raise ValueError("Either filter_key or filters must be provided")
        return self


class PredictResponse(BaseModel):
    model: str
    filter_key: str
    predictions: list[float]
    probabilities: list[list[float]] | None = None
