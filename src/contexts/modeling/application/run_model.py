import numpy as np

from contexts.modeling.application.commands import RunModelCommand, RunModelResult
from contexts.modeling.domain.errors import ArtifactNotFoundError, InputValidationError, ModelNotFoundError
from contexts.modeling.domain.models.filter_key import FilterKey
from contexts.modeling.domain.models.trained_model_ref import TrainedModelRef
from contexts.modeling.domain.ports.artifact_store import ArtifactStore
from contexts.modeling.domain.registry.model_definition_registry import ModelDefinitionRegistry
from contexts.modeling.domain.registry.trainer_registry import TrainerRegistry


class RunModelUseCase:
    def __init__(
        self,
        model_definition_registry: ModelDefinitionRegistry,
        trainer_registry: TrainerRegistry,
        artifact_store: ArtifactStore,
    ) -> None:
        self._model_definition_registry = model_definition_registry
        self._trainer_registry = trainer_registry
        self._artifact_store = artifact_store
        self._artifact_cache: dict[tuple[str, str], object] = {}

    def execute(self, command: RunModelCommand) -> RunModelResult:
        try:
            definition = self._model_definition_registry.require(command.model_name)
        except KeyError as exc:
            raise ModelNotFoundError(command.model_name) from exc

        filter_key = self._resolve_filter_key(command)
        ref = TrainedModelRef(model_name=definition.name, filter_key=filter_key)

        self._validate_input(definition.features, command.input_features)
        X = self._build_matrix(definition.features, command.input_features)

        artifact = self._load_artifact(ref, definition.model_type)
        trainer = self._trainer_registry.require(definition.model_type)
        predict_result = trainer.predict(artifact, X)

        return RunModelResult(
            model=definition.name,
            filter_key=filter_key.value,
            predictions=predict_result.predictions,
            probabilities=predict_result.probabilities,
        )

    def _resolve_filter_key(self, command: RunModelCommand) -> FilterKey:
        if command.filter_key:
            return FilterKey(command.filter_key)
        return FilterKey.from_filters(command.filters)

    def _load_artifact(self, ref: TrainedModelRef, model_type: str):
        cache_key = (ref.model_name, ref.filter_key.value)
        cached = self._artifact_cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            data, _metadata = self._artifact_store.load(ref)
        except ArtifactNotFoundError:
            raise

        trainer = self._trainer_registry.require(model_type)
        artifact = trainer.deserialize(data)
        self._artifact_cache[cache_key] = artifact
        return artifact

    @staticmethod
    def _validate_input(expected_features: list[str], input_features: dict[str, list[float]]) -> None:
        expected_set = set(expected_features)
        provided_set = set(input_features)

        missing = expected_set - provided_set
        if missing:
            raise InputValidationError(f"Missing input features: {sorted(missing)}")

        extra = provided_set - expected_set
        if extra:
            raise InputValidationError(f"Unexpected input features: {sorted(extra)}")

        lengths = {name: len(values) for name, values in input_features.items()}
        unique_lengths = set(lengths.values())
        if len(unique_lengths) != 1:
            raise InputValidationError(f"Input feature lengths must match: {lengths}")

        if not lengths:
            raise InputValidationError("Input features cannot be empty")

        if next(iter(unique_lengths)) == 0:
            raise InputValidationError("Input features must contain at least one sample")

    @staticmethod
    def _build_matrix(feature_names: list[str], input_features: dict[str, list[float]]) -> np.ndarray:
        columns = [input_features[name] for name in feature_names]
        return np.column_stack(columns)
