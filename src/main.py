from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from api.routers.health import router as health_router
from bootstrap.settings import Settings, get_settings
from shared.persistence.postgres.engine import create_db_engine, create_session_factory


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    engine = create_db_engine(settings.database_url)
    session_factory = create_session_factory(engine)

    app.state.settings = settings
    app.state.engine = engine
    app.state.session_factory = session_factory

    yield

    engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(title="Model API", lifespan=lifespan)
    app.include_router(health_router)
    return app


app = create_app()


def get_app_settings(app: FastAPI) -> Settings:
    return app.state.settings


def get_app_engine(app: FastAPI) -> Engine:
    return app.state.engine


def get_app_session_factory(app: FastAPI) -> sessionmaker[Session]:
    return app.state.session_factory
