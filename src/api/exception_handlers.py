from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from contexts.modeling.domain.errors import (
    ArtifactNotFoundError,
    EmptyTrainingDataError,
    InputValidationError,
    ModelNotFoundError,
)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ModelNotFoundError)
    async def model_not_found_handler(_request: Request, exc: ModelNotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(ArtifactNotFoundError)
    async def artifact_not_found_handler(_request: Request, exc: ArtifactNotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(EmptyTrainingDataError)
    async def empty_training_data_handler(_request: Request, exc: EmptyTrainingDataError) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @app.exception_handler(InputValidationError)
    async def input_validation_handler(_request: Request, exc: InputValidationError) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": str(exc)})
