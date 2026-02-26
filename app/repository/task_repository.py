from datetime import datetime
from typing import Any, List, Optional

from motor.motor_asyncio import AsyncIOMotorCollection

from app.models.task import Task
from app.schemas.task_schema import TaskCreate, TaskUpdate


class TaskRepository:
    """
    Data access layer for tasks.
    All direct MongoDB interactions live here.
    """

    def __init__(self, collection: AsyncIOMotorCollection) -> None:
        self._collection = collection

    @staticmethod
    def _document_to_task(doc: dict[str, Any]) -> Task:
        return Task(
            id=doc["id"],
            title=doc["title"],
            description=doc.get("description"),
            due_date=doc.get("due_date"),
            priority=doc.get("priority", "medium"),
            is_completed=doc.get("is_completed", False),
            created_at=doc["created_at"],
            updated_at=doc["updated_at"],
            external_reference_id=doc.get("external_reference_id"),
        )

    async def create_task(self, data: TaskCreate) -> Task:
        task = Task.new(
            title=data.title,
            description=data.description,
            due_date=data.due_date,
            priority=data.priority,
        )
        await self._collection.insert_one(task.__dict__)
        return task

    async def list_tasks(self, skip: int = 0, limit: int = 20) -> List[Task]:
        cursor = (
            self._collection.find().sort("created_at", -1).skip(skip).limit(limit)
        )
        items: list[Task] = []
        async for doc in cursor:
            items.append(self._document_to_task(doc))
        return items

    async def get_task(self, task_id: str) -> Optional[Task]:
        doc = await self._collection.find_one({"id": task_id})
        if not doc:
            return None
        return self._document_to_task(doc)

    async def update_task(self, task_id: str, data: TaskUpdate) -> Optional[Task]:
        update_data: dict[str, Any] = {
            k: v for k, v in data.model_dump(exclude_unset=True).items()
        }
        if not update_data:
            return await self.get_task(task_id)

        update_data["updated_at"] = datetime.utcnow()
        result = await self._collection.find_one_and_update(
            {"id": task_id},
            {"$set": update_data},
            return_document=True,
        )
        if not result:
            return None
        return self._document_to_task(result)

    async def delete_task(self, task_id: str) -> bool:
        result = await self._collection.delete_one({"id": task_id})
        return result.deleted_count == 1

    async def mark_complete(self, task_id: str) -> Optional[Task]:
        result = await self._collection.find_one_and_update(
            {"id": task_id},
            {"$set": {"is_completed": True, "updated_at": datetime.utcnow()}},
            return_document=True,
        )
        if not result:
            return None
        return self._document_to_task(result)

    async def set_external_reference(
        self, task_id: str, reference_id: str
    ) -> Optional[Task]:
        result = await self._collection.find_one_and_update(
            {"id": task_id},
            {
                "$set": {
                    "external_reference_id": reference_id,
                    "updated_at": datetime.utcnow(),
                }
            },
            return_document=True,
        )
        if not result:
            return None
        return self._document_to_task(result)

