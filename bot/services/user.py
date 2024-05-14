from aiogram.types import User
from sqlalchemy.exc import IntegrityError

from bot.db import SectionModel, TaskModel, UnitOfWork
from bot.services import TaskService
from bot.utils import TaskText


class UserService:
    @classmethod
    async def add_user(cls, user: User, tz: str, uow: UnitOfWork):
        data = {
            "user_id": user.id,
            # "username": user.username,
            # "first_name": user.first_name,
            # "last_name": user.last_name,
            "timezone": tz,
        }
        try:
            async with uow:
                await uow.user.add_one(data=data)
                await uow.commit()
        except IntegrityError:
            pass

    @classmethod
    async def find_user(cls, user_id: int, uow: UnitOfWork):
        async with uow:
            return await uow.user.find_one(user_id=user_id)

    # а вот тут проблемы. Хотя, наверно, я просто усложняю, ведь очень просто в таблицу с задачами добавить колонку
    # с user_id. Но мы не ищем легких путей. Все равно скорость работы будет зависеть от кол-ва задач
    # Тем более в таблице task нет названия разделов
    # UPD: я добавил user_id в колонку task. Однако менять ничего не собираюсь, ведь названий разделов все еще нет =)
    @classmethod
    async def find_all_tasks(cls, user_id: int, uow: UnitOfWork) -> str | None:
        text = ""
        async with uow:
            sections = await uow.section.find_many(user_id=user_id)
            for section in sections:
                text += f"Раздел: {section.section}\n\t"
                tasks = await uow.task.find_many(section_id=section.section_id)
                if len(tasks) == 0:
                    text += "Задач нет\n"
                    continue
                for task in tasks:
                    notifications = await uow.notification.find_many(
                        task_id=task.task_id
                    )
                    text += TaskText.format_task(task, notifications) + "\n"
                text += "\n"
        return None if len(text) == 0 else text

    @classmethod
    async def find_all_tasks_with_deadline(
        cls, user_id: int, uow: UnitOfWork
    ) -> list[str]:
        tasks_with_deadlines = []
        async with uow:
            sections: list[SectionModel] = await uow.section.find_many(user_id=user_id)
            for section in sections:
                tasks_with_deadlines.extend(
                    await TaskService.find_all_tasks_with_deadline(
                        section_id=section.section_id, uow=uow
                    )
                )
        return tasks_with_deadlines

    @classmethod
    async def update_tz(cls, user_id: int, tz: str, uow: UnitOfWork):
        """
        Если у пользователя нет задач с дедлайнами, либо задач вообще нет. Просто меняем часовой пояс.
        """
        async with uow:
            await uow.user.update({"timezone": tz}, user_id=user_id)
            await uow.task.update({"timezone": tz}, user_id=user_id)
            await uow.commit()

    @classmethod
    async def delete_user(cls, user_id: int, uow: UnitOfWork):
        async with uow:
            await uow.user.delete(user_id=user_id)
            await uow.commit()
