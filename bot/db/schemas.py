from datetime import datetime

from pydantic import BaseModel


class UserModel(BaseModel):
    id: int
    user_id: int
    timezone: str | None
    create_date: datetime


class SectionModel(BaseModel):
    id: int
    user_id: int
    section_id: str
    section: str
    create_date: datetime


class TaskModel(BaseModel):
    id: int
    user_id: int
    section_id: str
    task_id: str
    title: str
    description: str
    deadline: datetime | None
    timezone: str | None
    create_date: datetime


class NotificationModel(BaseModel):
    id: int
    user_id: int
    section_id: str
    task_id: str
    deadline: datetime
    notification: datetime
    scheduler_id: str
    section: str
    title: str
    message: str | None
