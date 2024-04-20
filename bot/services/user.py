from aiogram.types import User

from bot.db import UnitOfWork
from bot.utils import TaskText


class UserService:
    @classmethod
    async def add_user(cls, user: User, uow: UnitOfWork):
        data = {
            "user_id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }
        async with uow:
            await uow.user.add_one(data=data)
            await uow.commit()

    @classmethod
    async def find_user(cls, user_id: int, uow: UnitOfWork):
        async with uow:
            return await uow.user.find_one(user_id=user_id)

    # а вот тут проблемы. Хотя, наверно, я просто усложняю, ведь очень просто в таблицу с задачами добавить колонку
    # с user_id. Но мы не ищем легких путей. Все равно скорость работы будет зависеть от кол-ва задач
    # Тем более в таблице task нет названия разделов
    @classmethod
    async def find_all_tasks(cls, user_id: int, uow: UnitOfWork) -> str | None:
        text = ""
        async with uow:
            sections = await uow.section.find_many(user_id=user_id)
            for section in sections:
                text += f"Раздел: {section.section}\n\t"
                tasks = await uow.task.find_many(section_id=section.section_id)
                for task in tasks:
                    notifications = await uow.notification.find_many(
                        task_id=task.task_id
                    )
                    text += await TaskText.format_task(task, notifications) + "\n"
                text += "\n"
        return None if len(text) == 0 else text
