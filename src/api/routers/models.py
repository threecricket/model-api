from fastapi import APIRouter, Depends

from api.schemas.models import ModelDefinitionResponse, TrainedInstanceResponse
from bootstrap.dependencies import AppDependencies, get_app_dependencies
from contexts.modeling.application.commands import ListTrainedModelsCommand
from contexts.modeling.domain.errors import ModelNotFoundError

router = APIRouter(tags=["models"])


@router.get("/models", response_model=list[ModelDefinitionResponse])
def list_models(
    deps: AppDependencies = Depends(get_app_dependencies),
) -> list[ModelDefinitionResponse]:
    definitions = deps.model_definition_registry.list_definitions()
    return [
        ModelDefinitionResponse(
            name=definition.name,
            model_type=definition.model_type,
            features=definition.features,
            target_features=definition.target_features,
        )
        for definition in definitions
    ]


@router.get("/models/{name}/trained", response_model=list[TrainedInstanceResponse])
def list_trained_models(
    name: str,
    deps: AppDependencies = Depends(get_app_dependencies),
) -> list[TrainedInstanceResponse]:
    if deps.model_definition_registry.get(name) is None:
        raise ModelNotFoundError(name)

    summaries = deps.list_trained_models_use_case.execute(
        ListTrainedModelsCommand(model_name=name),
    )
    return [
        TrainedInstanceResponse(
            filter_key=summary.filter_key,
            trained_at=summary.trained_at,
            metrics=summary.metrics,
            artifact_uri=summary.artifact_uri,
            row_count=summary.row_count,
        )
        for summary in summaries
    ]
