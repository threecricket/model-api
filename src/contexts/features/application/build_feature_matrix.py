from dataclasses import dataclass

from contexts.features.application.commands import TrainingFilter
from contexts.features.domain.registry.feature_registry import FeatureRegistry
from contexts.features.infrastructure.postgres.delivery_context_repository import (
    DeliveryContextRepository,
)


@dataclass(frozen=True)
class FeatureMatrix:
    features: dict[str, list[float]]
    targets: dict[str, list[float]]
    row_count: int


class BuildFeatureMatrixUseCase:
    def __init__(
        self,
        delivery_context_repository: DeliveryContextRepository,
        feature_registry: FeatureRegistry,
    ) -> None:
        self._delivery_context_repository = delivery_context_repository
        self._feature_registry = feature_registry

    def execute(
        self,
        feature_names: list[str],
        target_names: list[str],
        training_filter: TrainingFilter,
    ) -> FeatureMatrix:
        for name in [*feature_names, *target_names]:
            self._feature_registry.require(name)

        contexts = self._delivery_context_repository.find_by_filter(training_filter)
        row_count = len(contexts)

        features = {name: [] for name in feature_names}
        targets = {name: [] for name in target_names}

        for context in contexts:
            for name in feature_names:
                features[name].append(self._feature_registry.compute(name, context))
            for name in target_names:
                targets[name].append(self._feature_registry.compute(name, context))

        return FeatureMatrix(features=features, targets=targets, row_count=row_count)
