from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel, Field


Priority = Literal["low", "medium", "high"]


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    due_date: Optional[datetime] = None
    priority: Priority = "medium"


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    due_date: Optional[datetime] = None
    priority: Optional[Priority] = None


class TaskOut(TaskBase):
    id: str
    is_completed: bool
    created_at: datetime
    updated_at: datetime
    external_reference_id: Optional[str] = None

    class Config:
        from_attributes = True

