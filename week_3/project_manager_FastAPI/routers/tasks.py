from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models.project import Project
from models.task import Task
from models.user import User
from schemas import TaskCreate, TaskRead, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == task.project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    if task.assignee_id is not None:
        user = db.query(User).filter(User.id == task.assignee_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignee not found.")

    db_task = Task(**task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@router.get("", response_model=list[TaskRead])
def list_tasks(
    project_id: Optional[int] = None,
    assignee_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    q = db.query(Task)
    if project_id is not None:
        q = q.filter(Task.project_id == project_id)
    if assignee_id is not None:
        q = q.filter(Task.assignee_id == assignee_id)
    return q.order_by(Task.id.asc()).all()


@router.get("/{task_id}", response_model=TaskRead)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")
    return task


@router.put("/{task_id}", response_model=TaskRead)
def update_task(task_id: int, updates: TaskUpdate, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")

    data = updates.model_dump(exclude_unset=True)
    if "project_id" in data:
        project = db.query(Project).filter(Project.id == data["project_id"]).first()
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    if "assignee_id" in data and data["assignee_id"] is not None:
        user = db.query(User).filter(User.id == data["assignee_id"]).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignee not found.")

    for key, value in data.items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")

    db.delete(task)
    db.commit()
    return None
