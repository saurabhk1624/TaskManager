from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Literal
from uuid import uuid4


Priority = Literal["low", "medium", "high"]


@dataclass
class Task:
    id: str
    title: str
    description: Optional[str]
    due_date: Optional[datetime]
    priority: Priority
    is_completed: bool
    created_at: datetime
    updated_at: datetime
    external_reference_id: Optional[str]

    @staticmethod
    def new(
        title: str,
        description: Optional[str] = None,
        due_date: Optional[datetime] = None,
        priority: Priority = "medium",
    ) -> "Task":
        now = datetime.utcnow()
        return Task(
            id=str(uuid4()),
            title=title,
            description=description,
            due_date=due_date,
            priority=priority,
            is_completed=False,
            created_at=now,
            updated_at=now,
            external_reference_id=None,
        )

    def mark_completed(self) -> None:
        self.is_completed = True
        self.updated_at = datetime.utcnow()

