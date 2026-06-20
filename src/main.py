from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from api.exception_handlers import register_exception_handlers
from api.routers.health import router as health_router
from api.routers.models import router as models_router
from api.routers.predict import router as predict_router
from api.routers.train import router as train_router
from bootstrap.dependencies import create_dependencies
from bootstrap.settings import Settings, get_settings
from contexts.features.domain.registry.feature_registry import FeatureRegistry
from contexts.modeling.domain.registry.model_definition_registry import ModelDefinitionRegistry
from contexts.modeling.domain.registry.trainer_registry import TrainerRegistry
from shared.persistence.postgres.engine import create_db_engine, create_session_factory

MODEL_DEFINITIONS_PATH = Path(__file__).resolve().parent / "contexts" / "modeling" / "config" / "models.yaml"


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    engine = create_db_engine(settings.database_url)
    session_factory = create_session_factory(engine)

    feature_registry = FeatureRegistry.create_default()
    model_definition_registry = ModelDefinitionRegistry.from_yaml(MODEL_DEFINITIONS_PATH)
    trainer_registry = TrainerRegistry.create_default()

    dependencies = create_dependencies(
        settings=settings,
        session_factory=session_factory,
        feature_registry=feature_registry,
        model_definition_registry=model_definition_registry,
        trainer_registry=trainer_registry,
    )

    app.state.settings = settings
    app.state.engine = engine
    app.state.session_factory = session_factory
    app.state.feature_registry = feature_registry
    app.state.model_definition_registry = model_definition_registry
    app.state.trainer_registry = trainer_registry
    app.state.dependencies = dependencies

    yield

    engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(title="Model API", lifespan=lifespan)
    register_exception_handlers(app)
    app.include_router(health_router)
    app.include_router(train_router)
    app.include_router(predict_router)
    app.include_router(models_router)
    return app


app = create_app()


def get_app_settings(app: FastAPI) -> Settings:
    return app.state.settings


def get_app_engine(app: FastAPI) -> Engine:
    return app.state.engine


def get_app_session_factory(app: FastAPI) -> sessionmaker[Session]:
    return app.state.session_factory


def get_app_feature_registry(app: FastAPI) -> FeatureRegistry:
    return app.state.feature_registry


def get_app_model_definition_registry(app: FastAPI) -> ModelDefinitionRegistry:
    return app.state.model_definition_registry


def get_app_trainer_registry(app: FastAPI) -> TrainerRegistry:
    return app.state.trainer_registry
