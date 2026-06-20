from dataclasses import dataclass


@dataclass(frozen=True)
class ModelDefinition:
    name: str
    model_type: str
    features: list[str]
    target_features: list[str]
