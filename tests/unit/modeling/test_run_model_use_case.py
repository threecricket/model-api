from datetime import datetime, timezone
from unittest.mock import MagicMock

import numpy as np
import pytest

from contexts.modeling.application.commands import RunModelCommand
from contexts.modeling.application.run_model import RunModelUseCase
from contexts.modeling.domain.errors import (
    ArtifactNotFoundError,
    InputValidationError,
    ModelNotFoundError,
)
from contexts.modeling.domain.models.model_definition import ModelDefinition
from contexts.modeling.domain.models.filter_key import FilterKey
from contexts.modeling.domain.models.trained_model_ref import TrainedModelRef
from contexts.modeling.domain.ports.artifact_store import ArtifactMetadata
from contexts.modeling.domain.ports.model_trainer import PredictResult
from contexts.modeling.domain.registry.model_definition_registry import ModelDefinitionRegistry
from contexts.modeling.domain.registry.trainer_registry import TrainerRegistry


MODEL_NAME = "batting_team_win_probability"
FEATURES = [
    "current_innings_runs",
    "current_innings_wickets",
    "current_innings_legal_ball_no",
]


@pytest.fixture
def model_definition() -> ModelDefinition:
    return ModelDefinition(
        name=MODEL_NAME,
        model_type="test.trainer",
        features=FEATURES,
        target_features=["batting_team_won"],
    )


@pytest.fixture
def model_registry(model_definition: ModelDefinition) -> ModelDefinitionRegistry:
    registry = ModelDefinitionRegistry()
    registry.register(model_definition)
    return registry


@pytest.fixture
def mock_trainer():
    trainer = MagicMock()
    trainer.model_type = "test.trainer"
    trainer.deserialize.return_value = {"mock": "artifact"}
    trainer.predict.return_value = PredictResult(
        predictions=[0.72, 0.31],
        probabilities=[[0.28, 0.72], [0.69, 0.31]],
    )
    return trainer


@pytest.fixture
def trainer_registry(mock_trainer) -> TrainerRegistry:
    registry = TrainerRegistry()
    registry.register(mock_trainer)
    return registry


@pytest.fixture
def artifact_store():
    store = MagicMock()
    store.load.return_value = (
        b"serialized-artifact",
        ArtifactMetadata(
            model_name=MODEL_NAME,
            filter_key="format:t20",
            filters={"format": ["t20"]},
            model_type="test.trainer",
            features=FEATURES,
            metrics={"accuracy": 0.81},
            row_count=100,
            trained_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        ),
    )
    return store


@pytest.fixture
def use_case(model_registry, trainer_registry, artifact_store) -> RunModelUseCase:
    return RunModelUseCase(model_registry, trainer_registry, artifact_store)


def _sample_input() -> dict[str, list[float]]:
    return {
        "current_innings_runs": [45.0, 120.0],
        "current_innings_wickets": [1.0, 4.0],
        "current_innings_legal_ball_no": [30.0, 100.0],
    }


class TestRunModelUseCase:
    def test_predict_with_filters(self, use_case, mock_trainer, artifact_store):
        result = use_case.execute(
            RunModelCommand(
                model_name=MODEL_NAME,
                filters={"format": ["t20"]},
                input_features=_sample_input(),
            )
        )

        assert result.model == MODEL_NAME
        assert result.filter_key == "format:t20"
        assert result.predictions == [0.72, 0.31]
        assert result.probabilities == [[0.28, 0.72], [0.69, 0.31]]

        ref = TrainedModelRef(model_name=MODEL_NAME, filter_key=FilterKey("format:t20"))
        artifact_store.load.assert_called_once_with(ref)
        mock_trainer.deserialize.assert_called_once_with(b"serialized-artifact")
        mock_trainer.predict.assert_called_once()
        X = mock_trainer.predict.call_args[0][1]
        np.testing.assert_array_equal(
            X,
            np.array([[45.0, 1.0, 30.0], [120.0, 4.0, 100.0]]),
        )

    def test_predict_with_explicit_filter_key(self, use_case):
        result = use_case.execute(
            RunModelCommand(
                model_name=MODEL_NAME,
                filter_key="format:t20",
                input_features=_sample_input(),
            )
        )
        assert result.filter_key == "format:t20"

    def test_unknown_model_raises(self, trainer_registry, artifact_store):
        use_case = RunModelUseCase(ModelDefinitionRegistry(), trainer_registry, artifact_store)
        with pytest.raises(ModelNotFoundError):
            use_case.execute(
                RunModelCommand(
                    model_name="nonexistent",
                    filter_key="format:t20",
                    input_features=_sample_input(),
                )
            )

    def test_missing_artifact_raises(self, use_case, artifact_store):
        artifact_store.load.side_effect = ArtifactNotFoundError(MODEL_NAME, "format:t20")
        with pytest.raises(ArtifactNotFoundError):
            use_case.execute(
                RunModelCommand(
                    model_name=MODEL_NAME,
                    filter_key="format:t20",
                    input_features=_sample_input(),
                )
            )

    def test_missing_features_raises(self, use_case):
        with pytest.raises(InputValidationError, match="Missing input features"):
            use_case.execute(
                RunModelCommand(
                    model_name=MODEL_NAME,
                    filter_key="format:t20",
                    input_features={"current_innings_runs": [45.0, 120.0]},
                )
            )

    def test_extra_features_raises(self, use_case):
        data = _sample_input()
        data["extra_feature"] = [1.0, 2.0]
        with pytest.raises(InputValidationError, match="Unexpected input features"):
            use_case.execute(
                RunModelCommand(
                    model_name=MODEL_NAME,
                    filter_key="format:t20",
                    input_features=data,
                )
            )

    def test_mismatched_lengths_raises(self, use_case):
        data = _sample_input()
        data["current_innings_runs"] = [45.0]
        with pytest.raises(InputValidationError, match="lengths must match"):
            use_case.execute(
                RunModelCommand(
                    model_name=MODEL_NAME,
                    filter_key="format:t20",
                    input_features=data,
                )
            )

    def test_artifact_cache_avoids_second_load(self, use_case, artifact_store):
        command = RunModelCommand(
            model_name=MODEL_NAME,
            filter_key="format:t20",
            input_features=_sample_input(),
        )
        use_case.execute(command)
        use_case.execute(command)
        artifact_store.load.assert_called_once()

    def test_invalidate_cache(self, use_case, artifact_store):
        ref = TrainedModelRef(model_name=MODEL_NAME, filter_key=FilterKey("format:t20"))
        command = RunModelCommand(
            model_name=MODEL_NAME,
            filter_key="format:t20",
            input_features=_sample_input(),
        )
        use_case.execute(command)
        use_case.invalidate_cache(ref)
        use_case.execute(command)
        assert artifact_store.load.call_count == 2
