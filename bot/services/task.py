from datetime import datetime, timedelta
from uuid import uuid4

import datefinder
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.db import NotificationModel, TaskModel, UnitOfWork, tz
from bot.utils import TaskText


class TaskService:
    @classmethod
    async def add_task(cls, task: dict, uow: UnitOfWork) -> str:
        """
        task:
            section_id str uuid
            section str
            title str
            description str
            deadline datetime | None
        """
        data = task.copy()  # делаем это, чтобы не испортить state
        del data["section"]
        task_id = str(uuid4())
        data["task_id"] = task_id

        async with uow:
            await uow.task.add_one(data)
            await uow.commit()
        return task_id

    @classmethod
    async def update_task_title(cls, task_id: str, new_title: str, uow: UnitOfWork):
        data = {"title": new_title}
        async with uow:
            await uow.task.update(data, task_id=task_id)
            await uow.notification.update(data, task_id=task_id)
            await uow.commit()

    @classmethod
    async def update_task_description(
        cls, task_id: str, description: str, uow: UnitOfWork
    ):
        async with uow:
            await uow.task.update({"description": description}, task_id=task_id)
            await uow.commit()

    @classmethod
    async def update_task_deadline(
        cls, task_id: str, deadline: datetime, uow: UnitOfWork
    ):
        async with uow:
            await uow.task.update({"deadline": deadline}, task_id=task_id)
            await uow.commit()

    @classmethod
    async def find_task(cls, task_id: str, uow: UnitOfWork) -> TaskModel | None:
        async with uow:
            return await uow.task.find_one(task_id=task_id)

    @classmethod
    async def find_task_with_notifications(
        cls, task_id: str, uow: UnitOfWork
    ) -> tuple[TaskModel, list[NotificationModel]] | None:
        async with uow:
            task = await uow.task.find_one(task_id=task_id)
            notifications = await uow.notification.find_many(task_id=task_id)
            if task is None or notifications is None:
                return None
            return task, notifications

    # Это конечно дичь редкостная, но таков путь
    @classmethod
    async def find_all_tasks_with_notifications(
        cls, section_id: str, uow: UnitOfWork
    ) -> tuple[int, str, dict] | Exception:
        """
        returns
            count of all tasks
            formatted string with notifications in minute format
            state data: dict[number str: task_id str uuid]
        """
        k = 0
        state_data = {}
        text = ""
        async with uow:
            tasks = await uow.task.find_many(section_id=section_id)
            if len(tasks) == 0:
                raise ValueError
            for task in tasks:
                k += 1
                text += f"{k}. {await TaskText.format_task(task, await uow.notification.find_many(task_id=task.task_id))}\n\n"
                state_data[str(k)] = task.task_id
        return k, text, state_data

    @classmethod
    async def get_deadline(cls, text: str) -> datetime | Exception:
        now = datetime.now(tz).replace(microsecond=0, second=0)
        match text.lower():
            case "через 5 минут":
                return now + timedelta(minutes=5)
            case "через 10 минут":
                return now + timedelta(minutes=10)
            case "через 15 минут":
                return now + timedelta(minutes=15)
            case "через 30 минут":
                return now + timedelta(minutes=30)
            case "через 1 час":
                return now + timedelta(hours=1)
            case _:
                try:
                    return next(datefinder.find_dates(text=text, first="day"))
                except StopIteration:
                    raise ValueError

    @classmethod
    async def get_custom_deadline(cls, time: str) -> datetime | None:
        for message in time.split():
            try:
                return datetime.now(tz).replace(microsecond=0, second=0) + timedelta(
                    minutes=int(message)
                )
            except ValueError:
                continue
        return None

    @classmethod
    async def delete_task(
        cls, task_id: str, scheduler: AsyncIOScheduler, uow: UnitOfWork
    ):
        # с удалением задачи чуть посложнее, тк могут быть напоминания, которые нужно удалять из scheduler
        async with uow:
            notificaitons = await uow.notification.find_many(task_id=task_id)
            await uow.task.delete(task_id=task_id)
            await uow.commit()

        if notificaitons:
            for notification in notificaitons:
                scheduler.remove_job(job_id=notification.scheduler_id)
