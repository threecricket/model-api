from datetime import datetime, timezone

import numpy as np

from contexts.features.application.build_feature_matrix import BuildFeatureMatrixUseCase
from contexts.features.application.commands import TrainingFilter
from contexts.modeling.application.commands import TrainModelCommand, TrainModelResult
from contexts.modeling.domain.errors import EmptyTrainingDataError, ModelNotFoundError
from contexts.modeling.domain.models.filter_key import FilterKey
from contexts.modeling.domain.models.trained_model_ref import TrainedModelRef
from contexts.modeling.domain.ports.artifact_store import ArtifactMetadata, ArtifactStore
from contexts.modeling.domain.registry.model_definition_registry import ModelDefinitionRegistry
from contexts.modeling.domain.registry.trainer_registry import TrainerRegistry


class TrainModelUseCase:
    def __init__(
        self,
        model_definition_registry: ModelDefinitionRegistry,
        trainer_registry: TrainerRegistry,
        artifact_store: ArtifactStore,
        build_feature_matrix: BuildFeatureMatrixUseCase,
    ) -> None:
        self._model_definition_registry = model_definition_registry
        self._trainer_registry = trainer_registry
        self._artifact_store = artifact_store
        self._build_feature_matrix = build_feature_matrix

    def execute(self, command: TrainModelCommand) -> TrainModelResult:
        try:
            definition = self._model_definition_registry.require(command.model_name)
        except KeyError as exc:
            raise ModelNotFoundError(command.model_name) from exc

        options = command.options or {}
        filters = options.get("filters", {})
        filter_key = FilterKey.from_filters(filters)
        ref = TrainedModelRef(model_name=definition.name, filter_key=filter_key)

        training_filter = TrainingFilter.from_dict(filters)
        matrix = self._build_feature_matrix.execute(
            feature_names=definition.features,
            target_names=definition.target_features,
            training_filter=training_filter,
        )

        if matrix.row_count == 0:
            raise EmptyTrainingDataError()

        X = self._build_matrix(definition.features, matrix.features)
        y = self._build_target_vector(definition.target_features, matrix.targets)

        trainer = self._trainer_registry.require(definition.model_type)
        fit_result = trainer.fit(X, y, options)

        trained_at = datetime.now(timezone.utc)
        metadata = ArtifactMetadata(
            model_name=definition.name,
            filter_key=filter_key.value,
            filters=filters,
            model_type=definition.model_type,
            features=definition.features,
            metrics=fit_result.metrics,
            row_count=matrix.row_count,
            trained_at=trained_at,
        )

        artifact_bytes = trainer.serialize(fit_result.artifact)
        artifact_uri = self._artifact_store.save(ref, artifact_bytes, metadata)

        return TrainModelResult(
            model=definition.name,
            filter_key=filter_key.value,
            filters=filters,
            metrics=fit_result.metrics,
            rows_used=matrix.row_count,
            artifact_uri=artifact_uri,
        )

    @staticmethod
    def _build_matrix(feature_names: list[str], features: dict[str, list[float]]) -> np.ndarray:
        columns = [features[name] for name in feature_names]
        return np.column_stack(columns)

    @staticmethod
    def _build_target_vector(target_names: list[str], targets: dict[str, list[float]]) -> np.ndarray:
        if len(target_names) != 1:
            raise ValueError("v1 supports exactly one target feature")
        return np.array(targets[target_names[0]], dtype=float)
