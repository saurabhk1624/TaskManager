from typing import Annotated, List

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Query,
    Request,
    status,
)

from app.models.task import Task
from app.repository.task_repository import TaskRepository
from app.schemas.task_schema import TaskCreate, TaskOut, TaskUpdate
from app.services.external_platform import ExternalPlatformService


router = APIRouter()


def get_task_repository(request: Request) -> TaskRepository:
    repo = getattr(request.app.state, "task_repository", None)
    if repo is None:
        raise RuntimeError("TaskRepository is not configured on application state")
    return repo


def get_external_service(request: Request) -> ExternalPlatformService:
    service = getattr(request.app.state, "external_service", None)
    if service is None:
        raise RuntimeError("ExternalPlatformService is not configured on application state")
    return service


TaskRepoDep = Annotated[TaskRepository, Depends(get_task_repository)]
ExternalServiceDep = Annotated[ExternalPlatformService, Depends(get_external_service)]


@router.post(
    "/tasks",
    response_model=TaskOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_task(
    payload: TaskCreate,
    background_tasks: BackgroundTasks,
    repo: TaskRepoDep,
    external_service: ExternalServiceDep,
) -> TaskOut:
    task: Task = await repo.create_task(payload)
    # Fire-and-forget background integration; failures are swallowed.
    background_tasks.add_task(external_service.handle_task_created, task)
    return TaskOut.model_validate(task)


@router.get("/tasks", response_model=List[TaskOut])
async def list_tasks(
    repo: TaskRepoDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> List[TaskOut]:
    tasks = await repo.list_tasks(skip=skip, limit=limit)
    return [TaskOut.model_validate(t) for t in tasks]


@router.get("/tasks/{task_id}", response_model=TaskOut)
async def get_task(task_id: str, repo: TaskRepoDep) -> TaskOut:
    task = await repo.get_task(task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return TaskOut.model_validate(task)


@router.put("/tasks/{task_id}", response_model=TaskOut)
async def update_task(
    task_id: str,
    payload: TaskUpdate,
    repo: TaskRepoDep,
) -> TaskOut:
    task = await repo.update_task(task_id, payload)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return TaskOut.model_validate(task)


@router.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_task(task_id: str, repo: TaskRepoDep) -> None:
    deleted = await repo.delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")


@router.post("/tasks/{task_id}/complete", response_model=TaskOut)
async def complete_task(
    task_id: str,
    repo: TaskRepoDep,
) -> TaskOut:
    task = await repo.mark_complete(task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return TaskOut.model_validate(task)

