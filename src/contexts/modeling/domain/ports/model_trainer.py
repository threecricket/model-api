from dataclasses import dataclass, field
from typing import Any, Protocol

import numpy as np


@dataclass(frozen=True)
class FitResult:
    artifact: Any
    metrics: dict[str, float]
    extra: dict = field(default_factory=dict)


@dataclass(frozen=True)
class PredictResult:
    predictions: list[float]
    probabilities: list[list[float]] | None = None


class ModelTrainer(Protocol):
    @property
    def model_type(self) -> str: ...

    def fit(self, X: np.ndarray, y: np.ndarray, options: dict) -> FitResult: ...

    def predict(self, artifact: Any, X: np.ndarray) -> PredictResult: ...

    def serialize(self, artifact: Any) -> bytes: ...

    def deserialize(self, data: bytes) -> Any: ...
