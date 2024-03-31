from sqlalchemy import insert, update, select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User, Section, Task, Notification
from .schemas import BaseModel, UserModel, SectionModel, TaskModel, NotificationModel


class SQLAlchemyRepository:
    model = None
    read_model = BaseModel

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_one(self, data: dict):
        stmt = insert(self.model).values(**data)
        await self.session.execute(stmt)

    async def update(self, data: dict, **filter_params):
        stmt = update(self.model).filter_by(**filter_params).values(**data)
        await self.session.execute(stmt)

    async def find_one(self, **filter_params) -> read_model | None:
        query = select(self.model).filter_by(**filter_params)
        model = await self.session.scalar(query)
        return None if model is None else model.to_read_model()

    async def find_many(self, **filter_params) -> list[read_model] | None:
        query = select(self.model).filter_by(**filter_params)
        data = await self.session.execute(query)
        result = []
        for model in data.all():
            result.append(model[0].to_read_model())
        return result

    async def delete(self, **filter_params):
        stmt = delete(self.model).filter_by(**filter_params)
        await self.session.execute(stmt)


class UserRepository(SQLAlchemyRepository):
    model = User
    read_model = UserModel


class SectionRepository(SQLAlchemyRepository):
    model = Section
    read_model = SectionModel


class TaskRepository(SQLAlchemyRepository):
    model = Task
    read_model = TaskModel


class NotificationRepository(SQLAlchemyRepository):
    model = Notification
    read_model = NotificationModel

    async def find_all(self) -> list[read_model]:
        query = select(self.model)
        data = await self.session.execute(query)
        result = []
        for model in data.all():
            result.append(model[0].to_read_model())
        return result
