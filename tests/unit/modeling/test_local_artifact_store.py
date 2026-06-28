from datetime import datetime, timezone

import pytest

from bootstrap.settings import Settings
from contexts.modeling.domain.errors import ArtifactNotFoundError
from contexts.modeling.domain.models.filter_key import FilterKey
from contexts.modeling.domain.models.trained_model_ref import TrainedModelRef
from contexts.modeling.domain.ports.artifact_store import ArtifactMetadata
from contexts.modeling.infrastructure.local.artifact_store import LocalArtifactStore


def _settings(tmp_path) -> Settings:
    return Settings(
        database_url="postgresql://user:pass@localhost/db",
        artifact_store="local",
        local_models_dir=str(tmp_path),
        s3_prefix="models",
    )


def _ref(model_name: str = "win_probability", filter_key: str = "format:T20") -> TrainedModelRef:
    return TrainedModelRef(model_name=model_name, filter_key=FilterKey(filter_key))


def _metadata(ref: TrainedModelRef) -> ArtifactMetadata:
    return ArtifactMetadata(
        model_name=ref.model_name,
        filter_key=ref.filter_key.value,
        filters={"format": "T20"},
        model_type="xgboost",
        features=["a", "b"],
        metrics={"accuracy": 0.91},
        row_count=1000,
        trained_at=datetime(2026, 6, 26, 5, 40, tzinfo=timezone.utc),
    )


class TestLocalArtifactStore:
    def test_save_then_load_round_trip(self, tmp_path):
        store = LocalArtifactStore(_settings(tmp_path))
        ref = _ref()
        metadata = _metadata(ref)

        uri = store.save(ref, b"model-bytes", metadata)
        assert uri.startswith("file://")

        store.invalidate_cache(ref)
        data, loaded = store.load(ref)
        assert data == b"model-bytes"
        assert loaded == metadata

    def test_save_writes_versioned_and_latest(self, tmp_path):
        store = LocalArtifactStore(_settings(tmp_path))
        ref = _ref()
        metadata = _metadata(ref)

        store.save(ref, b"model-bytes", metadata)

        instance_dir = tmp_path / "models" / ref.model_name / ref.filter_key.value
        assert (instance_dir / "latest.pkl").exists()
        assert (instance_dir / "latest.metadata.json").exists()
        assert (instance_dir / "20260626T054000Z.pkl").exists()

    def test_exists_true_and_false(self, tmp_path):
        store = LocalArtifactStore(_settings(tmp_path))
        ref = _ref()

        assert store.exists(ref) is False
        store.save(ref, b"model-bytes", _metadata(ref))
        assert store.exists(ref) is True

    def test_load_raises_when_missing(self, tmp_path):
        store = LocalArtifactStore(_settings(tmp_path))
        with pytest.raises(ArtifactNotFoundError):
            store.load(_ref())

    def test_list_instances(self, tmp_path):
        store = LocalArtifactStore(_settings(tmp_path))
        ref_a = _ref("win_probability", "format:T20")
        ref_b = _ref("score_predictor", "format:ODI")
        store.save(ref_a, b"a", _metadata(ref_a))
        store.save(ref_b, b"b", _metadata(ref_b))

        summaries = store.list_instances()
        assert [s.model_name for s in summaries] == ["score_predictor", "win_probability"]
        assert all(s.artifact_uri.startswith("file://") for s in summaries)

    def test_list_instances_filtered_by_model(self, tmp_path):
        store = LocalArtifactStore(_settings(tmp_path))
        ref_a = _ref("win_probability", "format:T20")
        ref_b = _ref("score_predictor", "format:ODI")
        store.save(ref_a, b"a", _metadata(ref_a))
        store.save(ref_b, b"b", _metadata(ref_b))

        summaries = store.list_instances("win_probability")
        assert [s.model_name for s in summaries] == ["win_probability"]

    def test_list_instances_empty_when_no_models(self, tmp_path):
        store = LocalArtifactStore(_settings(tmp_path))
        assert store.list_instances() == []

    def test_cache_invalidated_on_resave(self, tmp_path):
        store = LocalArtifactStore(_settings(tmp_path))
        ref = _ref()
        store.save(ref, b"first", _metadata(ref))

        data, _ = store.load(ref)
        assert data == b"first"

        store.save(ref, b"second", _metadata(ref))
        data, _ = store.load(ref)
        assert data == b"second"
