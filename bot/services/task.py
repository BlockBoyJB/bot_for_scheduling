from datetime import datetime, timedelta, timezone
from uuid import uuid4

import datefinder
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.db import NotificationModel, TaskModel, UnitOfWork, UserModel
from bot.services import NotificationService
from bot.utils import TaskText, TimezoneService

default_tz = timezone.utc


class TaskService:
    @classmethod
    async def add_task(
        cls, user_id: int, task: dict, uow: UnitOfWork
    ) -> tuple[str, str]:
        """
        task:
            section_id str uuid
            section str
            title str
            description str
            deadline datetime with timezone | datetime without timezone | None
        """
        data = task.copy()  # делаем это, чтобы не испортить state
        del data["section"]
        task_id = str(uuid4())
        data["task_id"] = task_id
        data["user_id"] = user_id

        async with uow:
            user: UserModel = await uow.user.find_one(user_id=user_id)
            if data["deadline"]:
                data["deadline"] = TimezoneService.convert_to_tz(
                    data["deadline"], user.timezone
                )
            data["timezone"] = user.timezone
            await uow.task.add_one(data)
            await uow.commit()
        return task_id, user.timezone

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
            task: TaskModel = await uow.task.find_one(task_id=task_id)
            await uow.task.update(
                {"deadline": TimezoneService.convert_to_tz(deadline, task.timezone)},
                task_id=task_id,
            )
            await uow.commit()

    @classmethod
    async def update_tasks_timezone(
        cls,
        *tasks: str,
        user_id: int,
        new_tz: str,
        scheduler: AsyncIOScheduler,
        uow: UnitOfWork,
    ):
        """
        Если у пользователя есть задачи с дедлайнами и он хочет конвертировать их под новый часовой пояс

        Например: он жил в Екатеринбурге (UTC+5) и переехал в Москву (UTC+3).
        В Екатеринбурге у него были задачи в 15:00. При переезде по мск времени они будут в 13:00.
        По UTC это то же самое время. Но в Москве он захотел вернуть задачи к 15:00, а это уже другое время.
        Если 15:00 в Екатеринбурге это 10:00 UTC, то 15:00 в Москве это уже 12:00 UTC.

        Не знаю зачем я это так подробно расписал, все равно же никто не будет читать :)

        У некоторых задач пропадают напоминания ввиду истекшего времени напоминания, поэтому удаляем их.
        В конце обновлям значение часового пояса и у пользователя

        tasks: массив с task_id, в которых есть дедлайн
        new_time = old_time.astimezone(old_tz).replace(tzinfo=new_tz)
        """
        new_tz = TimezoneService.str_to_tz(new_tz)
        async with uow:
            for task_id in tasks:
                task: TaskModel = await uow.task.find_one(task_id=task_id)
                old_tz = TimezoneService.str_to_tz(task.timezone)
                new_time = task.deadline.astimezone(old_tz).replace(tzinfo=new_tz)
                notifications = await uow.notification.find_many(task_id=task_id)
                for notification in notifications:
                    new_notification = notification.notification - (
                        notification.deadline - new_time
                    )
                    if TimezoneService.valid_date(new_notification, new_tz) is False:
                        await uow.notification.delete(
                            scheduler_id=notification.scheduler_id
                        )
                        scheduler.remove_job(job_id=notification.scheduler_id)
                        continue
                    await uow.notification.update(
                        {"deadline": new_time, "notification": new_notification},
                        scheduler_id=notification.scheduler_id,
                    )
                    scheduler.modify_job(
                        job_id=notification.scheduler_id, next_run_time=new_notification
                    )
                await uow.task.update({"deadline": new_time}, task_id=task_id)

            # в конце обновляем все значения для колонки timezone
            new_tz = TimezoneService.tz_to_str(new_tz)
            await uow.task.update({"timezone": new_tz}, user_id=user_id)
            await uow.user.update({"timezone": new_tz}, user_id=user_id)
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
                text += f"{k}. {TaskText.format_task(task, await uow.notification.find_many(task_id=task.task_id))}\n\n"
                state_data[str(k)] = task.task_id
        return k, text, state_data

    @classmethod
    async def find_all_tasks_with_deadline(
        cls, section_id: str, uow: UnitOfWork
    ) -> list[str]:
        result = []
        async with uow:
            tasks: list[TaskModel] = await uow.task.find_many(section_id=section_id)
            for task in tasks:
                if task.deadline:
                    result.append(task.task_id)
        return result

    @classmethod
    async def get_deadline(cls, text: str) -> datetime | Exception:
        now = datetime.now(tz=default_tz).replace(microsecond=0, second=0)
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
                return datetime.now(tz=default_tz).replace(
                    microsecond=0, second=0
                ) + timedelta(minutes=int(message))
            except ValueError:
                continue
        return None

    @classmethod
    async def delete_task(
        cls, task_id: str, scheduler: AsyncIOScheduler, uow: UnitOfWork
    ):
        async with uow:
            await uow.task.delete(task_id=task_id)
            await NotificationService.delete_many_with_tx(
                scheduler=scheduler, uow=uow, task_id=task_id
            )
            await uow.commit()

    @classmethod
    async def delete_section_tasks(
        cls, section_id: str, scheduler: AsyncIOScheduler, uow: UnitOfWork
    ):
        async with uow:
            await uow.task.delete(section_id=section_id)
            await NotificationService.delete_many_with_tx(
                scheduler=scheduler, uow=uow, section_id=section_id
            )
            await uow.commit()

    @classmethod
    async def delete_all_tasks(
        cls, user_id: int, scheduler: AsyncIOScheduler, uow: UnitOfWork
    ):
        async with uow:
            await uow.task.delete(user_id=user_id)
            await NotificationService.delete_many_with_tx(
                scheduler=scheduler, uow=uow, user_id=user_id
            )
            await uow.commit()
