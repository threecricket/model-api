from contexts.features.domain.models.feature import Feature, FeatureStrategy
from contexts.features.domain.strategies.innings_state import INNINGS_STATE_STRATEGIES
from contexts.features.domain.strategies.outcome import OUTCOME_STRATEGIES
from contexts.features.domain.strategies.player_state import PLAYER_STATE_STRATEGIES

DEFAULT_FEATURE_STRATEGIES: list[FeatureStrategy] = [
    *INNINGS_STATE_STRATEGIES,
    *PLAYER_STATE_STRATEGIES,
    *OUTCOME_STRATEGIES,
]


class FeatureRegistry:
    def __init__(self) -> None:
        self._strategies: dict[str, FeatureStrategy] = {}

    @classmethod
    def create_default(cls) -> "FeatureRegistry":
        registry = cls()
        for strategy in DEFAULT_FEATURE_STRATEGIES:
            registry.register(strategy)
        return registry

    def register(self, strategy: FeatureStrategy) -> None:
        if strategy.name in self._strategies:
            raise ValueError(f"Feature strategy already registered: {strategy.name}")
        self._strategies[strategy.name] = strategy

    def get(self, name: str) -> FeatureStrategy | None:
        return self._strategies.get(name)

    def require(self, name: str) -> FeatureStrategy:
        strategy = self.get(name)
        if strategy is None:
            raise KeyError(f"Unknown feature: {name}")
        return strategy

    def list_features(self) -> list[Feature]:
        return [Feature(name=name) for name in sorted(self._strategies)]

    def compute(self, name: str, context) -> float:
        return self.require(name).compute(context)
