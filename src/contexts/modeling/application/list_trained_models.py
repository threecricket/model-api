from contexts.modeling.application.commands import ListTrainedModelsCommand
from contexts.modeling.domain.ports.artifact_store import ArtifactStore, TrainedInstanceSummary


class ListTrainedModelsUseCase:
    def __init__(self, artifact_store: ArtifactStore) -> None:
        self._artifact_store = artifact_store

    def execute(self, command: ListTrainedModelsCommand) -> list[TrainedInstanceSummary]:
        return self._artifact_store.list_instances(command.model_name)
