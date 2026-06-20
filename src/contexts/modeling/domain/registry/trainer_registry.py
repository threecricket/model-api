from contexts.modeling.domain.ports.model_trainer import ModelTrainer
from contexts.modeling.domain.errors import TrainerNotFoundError


class TrainerRegistry:
    def __init__(self) -> None:
        self._trainers: dict[str, ModelTrainer] = {}

    @classmethod
    def create_default(cls) -> "TrainerRegistry":
        from contexts.modeling.infrastructure.trainers.sklearn_trainers import SKLEARN_TRAINERS
        from contexts.modeling.infrastructure.trainers.xgboost_trainers import XGBOOST_TRAINERS

        registry = cls()
        for trainer in [*SKLEARN_TRAINERS, *XGBOOST_TRAINERS]:
            registry.register(trainer)
        return registry

    def register(self, trainer: ModelTrainer) -> None:
        if trainer.model_type in self._trainers:
            raise ValueError(f"Trainer already registered: {trainer.model_type}")
        self._trainers[trainer.model_type] = trainer

    def get(self, model_type: str) -> ModelTrainer | None:
        return self._trainers.get(model_type)

    def require(self, model_type: str) -> ModelTrainer:
        trainer = self.get(model_type)
        if trainer is None:
            raise TrainerNotFoundError(model_type)
        return trainer
