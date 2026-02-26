from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from app.api import routes as task_routes
from app.core.config import get_settings
from app.db.mongo import MongoClientManager
from app.repository.task_repository import TaskRepository
from app.services.external_platform import GitHubExternalPlatformService


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    mongo_manager = MongoClientManager(settings)

    mongo_manager.connect()
    task_collection = mongo_manager.tasks_collection

    task_repository = TaskRepository(task_collection)
    external_service = GitHubExternalPlatformService(
        settings=settings,
        repository=task_repository,
    )

    app.state.mongo_manager = mongo_manager
    app.state.task_repository = task_repository
    app.state.external_service = external_service

    try:
        yield
    finally:
        await mongo_manager.close()


app = FastAPI(
    title="Task Manager API",
    version="0.1.0",
    lifespan=lifespan,
)


app.include_router(task_routes.router)

