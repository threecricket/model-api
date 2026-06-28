from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol

from contexts.modeling.domain.models.trained_model_ref import TrainedModelRef


@dataclass(frozen=True)
class ArtifactMetadata:
    model_name: str
    filter_key: str
    filters: dict
    model_type: str
    features: list[str]
    metrics: dict[str, float]
    row_count: int
    trained_at: datetime
    extra: dict = field(default_factory=dict)


@dataclass(frozen=True)
class TrainedInstanceSummary:
    model_name: str
    filter_key: str
    trained_at: datetime
    metrics: dict[str, float]
    artifact_uri: str
    row_count: int


class ArtifactStore(Protocol):
    def save(self, ref: TrainedModelRef, data: bytes, metadata: ArtifactMetadata) -> str: ...

    def load(self, ref: TrainedModelRef) -> tuple[bytes, ArtifactMetadata]: ...

    def exists(self, ref: TrainedModelRef) -> bool: ...

    def list_instances(self, model_name: str | None = None) -> list[TrainedInstanceSummary]: ...

    def invalidate_cache(self, ref: TrainedModelRef) -> None: ...
