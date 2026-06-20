class ModelNotFoundError(Exception):
    def __init__(self, model_name: str) -> None:
        super().__init__(f"Unknown model: {model_name}")
        self.model_name = model_name


class ArtifactNotFoundError(Exception):
    def __init__(self, model_name: str, filter_key: str) -> None:
        super().__init__(
            f"No trained artifact for model={model_name!r}, filter_key={filter_key!r}. "
            f"Check GET /models/{model_name}/trained for available instances."
        )
        self.model_name = model_name
        self.filter_key = filter_key


class TrainerNotFoundError(Exception):
    def __init__(self, model_type: str) -> None:
        super().__init__(f"Unknown model type: {model_type}")
        self.model_type = model_type


class EmptyTrainingDataError(Exception):
    def __init__(self) -> None:
        super().__init__("No training rows matched the provided filters")


class InputValidationError(Exception):
    pass
