from pathlib import Path

import yaml

from contexts.modeling.domain.models.model_definition import ModelDefinition


class ModelDefinitionRegistry:
    def __init__(self) -> None:
        self._definitions: dict[str, ModelDefinition] = {}

    @classmethod
    def from_yaml(cls, path: Path) -> "ModelDefinitionRegistry":
        registry = cls()
        with path.open() as f:
            data = yaml.safe_load(f)

        for entry in data.get("models", []):
            definition = ModelDefinition(
                name=entry["name"],
                model_type=entry["model_type"],
                features=list(entry["features"]),
                target_features=list(entry["target_features"]),
            )
            registry.register(definition)

        return registry

    def register(self, definition: ModelDefinition) -> None:
        if definition.name in self._definitions:
            raise ValueError(f"Model definition already registered: {definition.name}")
        self._definitions[definition.name] = definition

    def get(self, name: str) -> ModelDefinition | None:
        return self._definitions.get(name)

    def require(self, name: str) -> ModelDefinition:
        definition = self.get(name)
        if definition is None:
            raise KeyError(f"Unknown model: {name}")
        return definition

    def list_definitions(self) -> list[ModelDefinition]:
        return [self._definitions[name] for name in sorted(self._definitions)]
