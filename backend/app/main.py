from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.api.router import api_router
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.db.base import Base
from app.db.session import engine
from app import models  # noqa: F401

settings = get_settings()
setup_logging()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    if settings.database_url.startswith("postgresql"):
        with engine.begin() as connection:
            connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)
app.include_router(api_router, prefix=settings.api_v1_prefix)
