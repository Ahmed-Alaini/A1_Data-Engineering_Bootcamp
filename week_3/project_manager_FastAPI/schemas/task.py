
from typing import Optional

from pydantic import BaseModel, ConfigDict


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False
    project_id: int
    assignee_id: Optional[int] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    project_id: Optional[int] = None
    assignee_id: Optional[int] = None


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str] = None
    completed: bool
    project_id: int
    assignee_id: Optional[int] = None
