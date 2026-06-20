from collections.abc import Generator
from dataclasses import dataclass

from fastapi import Request
from sqlalchemy.orm import Session, sessionmaker

from bootstrap.settings import Settings
from contexts.features.application.build_feature_matrix import BuildFeatureMatrixUseCase
from contexts.features.domain.registry.feature_registry import FeatureRegistry
from contexts.features.infrastructure.postgres.delivery_context_repository import (
    DeliveryContextRepository,
)
from contexts.modeling.application.list_trained_models import ListTrainedModelsUseCase
from contexts.modeling.application.run_model import RunModelUseCase
from contexts.modeling.application.train_model import TrainModelUseCase
from contexts.modeling.domain.registry.model_definition_registry import ModelDefinitionRegistry
from contexts.modeling.domain.registry.trainer_registry import TrainerRegistry
from contexts.modeling.infrastructure.s3.artifact_store import S3ArtifactStore


@dataclass(frozen=True)
class AppDependencies:
    settings: Settings
    session_factory: sessionmaker[Session]
    feature_registry: FeatureRegistry
    model_definition_registry: ModelDefinitionRegistry
    trainer_registry: TrainerRegistry
    artifact_store: S3ArtifactStore
    run_model_use_case: RunModelUseCase
    list_trained_models_use_case: ListTrainedModelsUseCase

    def train_model_use_case(self, session: Session) -> TrainModelUseCase:
        delivery_repository = DeliveryContextRepository(session)
        build_feature_matrix = BuildFeatureMatrixUseCase(
            delivery_repository,
            self.feature_registry,
        )
        return TrainModelUseCase(
            self.model_definition_registry,
            self.trainer_registry,
            self.artifact_store,
            build_feature_matrix,
        )


def create_dependencies(
    settings: Settings,
    session_factory: sessionmaker[Session],
    feature_registry: FeatureRegistry,
    model_definition_registry: ModelDefinitionRegistry,
    trainer_registry: TrainerRegistry,
) -> AppDependencies:
    artifact_store = S3ArtifactStore(settings)
    run_model_use_case = RunModelUseCase(
        model_definition_registry,
        trainer_registry,
        artifact_store,
    )
    list_trained_models_use_case = ListTrainedModelsUseCase(artifact_store)
    return AppDependencies(
        settings=settings,
        session_factory=session_factory,
        feature_registry=feature_registry,
        model_definition_registry=model_definition_registry,
        trainer_registry=trainer_registry,
        artifact_store=artifact_store,
        run_model_use_case=run_model_use_case,
        list_trained_models_use_case=list_trained_models_use_case,
    )


def get_app_dependencies(request: Request) -> AppDependencies:
    return request.app.state.dependencies


def get_db_session(request: Request) -> Generator[Session, None, None]:
    session_factory = request.app.state.session_factory
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
