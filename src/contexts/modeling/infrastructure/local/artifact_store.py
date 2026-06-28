import json
from datetime import datetime, timezone
from pathlib import Path

from bootstrap.settings import Settings
from contexts.modeling.domain.errors import ArtifactNotFoundError
from contexts.modeling.domain.models.trained_model_ref import TrainedModelRef
from contexts.modeling.domain.ports.artifact_store import ArtifactMetadata, TrainedInstanceSummary


class LocalArtifactStore:
    def __init__(self, settings: Settings) -> None:
        self._base_dir = Path(settings.local_models_dir) / settings.s3_prefix.strip("/")
        self._base_dir.mkdir(parents=True, exist_ok=True)
        self._cache: dict[tuple[str, str], tuple[bytes, ArtifactMetadata]] = {}

    def save(self, ref: TrainedModelRef, data: bytes, metadata: ArtifactMetadata) -> str:
        instance_dir = self._instance_dir(ref)
        instance_dir.mkdir(parents=True, exist_ok=True)

        timestamp = metadata.trained_at.strftime("%Y%m%dT%H%M%SZ")
        versioned_path = instance_dir / f"{timestamp}.pkl"
        latest_path = instance_dir / "latest.pkl"
        metadata_path = instance_dir / "latest.metadata.json"

        versioned_path.write_bytes(data)
        latest_path.write_bytes(data)
        metadata_path.write_text(json.dumps(self._metadata_to_dict(metadata)))

        self.invalidate_cache(ref)
        return latest_path.resolve().as_uri()

    def load(self, ref: TrainedModelRef) -> tuple[bytes, ArtifactMetadata]:
        cache_key = (ref.model_name, ref.filter_key.value)
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        instance_dir = self._instance_dir(ref)
        latest_path = instance_dir / "latest.pkl"
        metadata_path = instance_dir / "latest.metadata.json"

        if not latest_path.exists() or not metadata_path.exists():
            raise ArtifactNotFoundError(ref.model_name, ref.filter_key.value)

        data = latest_path.read_bytes()
        metadata = self._metadata_from_dict(json.loads(metadata_path.read_text()))
        result = (data, metadata)
        self._cache[cache_key] = result
        return result

    def exists(self, ref: TrainedModelRef) -> bool:
        return (self._instance_dir(ref) / "latest.pkl").exists()

    def list_instances(self, model_name: str | None = None) -> list[TrainedInstanceSummary]:
        search_root = self._base_dir / model_name if model_name else self._base_dir
        if not search_root.exists():
            return []

        summaries: list[TrainedInstanceSummary] = []
        for metadata_path in search_root.rglob("latest.metadata.json"):
            metadata = self._metadata_from_dict(json.loads(metadata_path.read_text()))
            latest_path = metadata_path.parent / "latest.pkl"
            summaries.append(
                TrainedInstanceSummary(
                    model_name=metadata.model_name,
                    filter_key=metadata.filter_key,
                    trained_at=metadata.trained_at,
                    metrics=metadata.metrics,
                    artifact_uri=latest_path.resolve().as_uri(),
                    row_count=metadata.row_count,
                )
            )

        return sorted(summaries, key=lambda item: (item.model_name, item.filter_key))

    def invalidate_cache(self, ref: TrainedModelRef) -> None:
        self._cache.pop((ref.model_name, ref.filter_key.value), None)

    def _instance_dir(self, ref: TrainedModelRef) -> Path:
        return self._base_dir / ref.model_name / ref.filter_key.value

    @staticmethod
    def _metadata_to_dict(metadata: ArtifactMetadata) -> dict:
        return {
            "model_name": metadata.model_name,
            "filter_key": metadata.filter_key,
            "filters": metadata.filters,
            "model_type": metadata.model_type,
            "features": metadata.features,
            "metrics": metadata.metrics,
            "row_count": metadata.row_count,
            "trained_at": metadata.trained_at.isoformat(),
            "extra": metadata.extra,
        }

    @staticmethod
    def _metadata_from_dict(data: dict) -> ArtifactMetadata:
        trained_at = data["trained_at"]
        if isinstance(trained_at, str):
            trained_at = datetime.fromisoformat(trained_at)
            if trained_at.tzinfo is None:
                trained_at = trained_at.replace(tzinfo=timezone.utc)

        return ArtifactMetadata(
            model_name=data["model_name"],
            filter_key=data["filter_key"],
            filters=data.get("filters", {}),
            model_type=data["model_type"],
            features=list(data.get("features", [])),
            metrics={key: float(value) for key, value in data.get("metrics", {}).items()},
            row_count=int(data.get("row_count", 0)),
            trained_at=trained_at,
            extra=data.get("extra", {}),
        )
