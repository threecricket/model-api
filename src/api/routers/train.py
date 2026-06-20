from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.schemas.train import TrainRequest, TrainResponse
from bootstrap.dependencies import AppDependencies, get_app_dependencies, get_db_session
from contexts.modeling.application.commands import TrainModelCommand
from contexts.modeling.domain.models.filter_key import FilterKey
from contexts.modeling.domain.models.trained_model_ref import TrainedModelRef

router = APIRouter(tags=["train"])


@router.post("/train", response_model=TrainResponse)
def train(
    request: TrainRequest,
    session: Session = Depends(get_db_session),
    deps: AppDependencies = Depends(get_app_dependencies),
) -> TrainResponse:
    use_case = deps.train_model_use_case(session)
    result = use_case.execute(
        TrainModelCommand(model_name=request.model, options=request.options),
    )

    ref = TrainedModelRef(model_name=result.model, filter_key=FilterKey(result.filter_key))
    deps.run_model_use_case.invalidate_cache(ref)

    return TrainResponse(
        model=result.model,
        filter_key=result.filter_key,
        filters=result.filters,
        metrics=result.metrics,
        rows_used=result.rows_used,
        artifact_uri=result.artifact_uri,
    )
