from fastapi import APIRouter, Depends

from api.schemas.predict import PredictRequest, PredictResponse
from bootstrap.dependencies import AppDependencies, get_app_dependencies
from contexts.modeling.application.commands import RunModelCommand

router = APIRouter(tags=["predict"])


@router.post("/predict", response_model=PredictResponse)
def predict(
    request: PredictRequest,
    deps: AppDependencies = Depends(get_app_dependencies),
) -> PredictResponse:
    result = deps.run_model_use_case.execute(
        RunModelCommand(
            model_name=request.model,
            input_features=request.input,
            filters=request.filters,
            filter_key=request.filter_key,
        ),
    )
    return PredictResponse(
        model=result.model,
        filter_key=result.filter_key,
        predictions=result.predictions,
        probabilities=result.probabilities,
    )
