from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from app.api import routes as task_routes
from app.core.config import get_settings
from app.db.mongo import MongoClientManager
from  app.repository.task_repository import TaskRepository
from app.services.external_platform import GitHubExternalPlatformService
# from core.logging_config import setup_logging
import uvicorn
# from core.config import settings

# setup_logging(settings.log_level)
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

if __name__ == "__main__":
    try:
        print("Starting server...")
        uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
    except Exception as e:
        print(f"Server failed to start: {e}")
        raise



