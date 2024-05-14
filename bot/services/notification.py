from datetime import datetime, timedelta
from uuid import uuid4

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.db import NotificationModel, TaskModel, UnitOfWork, UserModel
from bot.utils import TaskText, TimezoneService, send_message


class NotificationService:
    @classmethod
    async def add_notification(
        cls,
        user_id: int,
        task: dict,
        scheduler: AsyncIOScheduler,
        bot: Bot,
        uow: UnitOfWork,
    ):
        """
        task data:
            section_id: str
            section: str
            title: str
            deadline: datetime with timezone | datetime
            notification: datetime with timezone | datetime
            task_id: str
            message: str
            tz: str
        """
        # сюда может приходить с tz либо без tz как результат парсера времени
        scheduler_id = str(uuid4())
        data = task.copy()
        del data["tz"]
        data["user_id"] = user_id
        data["scheduler_id"] = scheduler_id
        async with uow:
            user: UserModel = await uow.user.find_one(user_id=user_id)
            data["deadline"] = TimezoneService.convert_to_tz(
                data["deadline"], user.timezone
            )
            data["notification"] = TimezoneService.convert_to_tz(
                data["notification"], user.timezone
            )
            await uow.notification.add_one(data)
            await uow.commit()

        scheduler.add_job(
            send_message,
            id=scheduler_id,
            trigger="date",
            next_run_time=data["notification"],
            args=[bot, user_id, scheduler_id],
        )

    @classmethod
    async def update_notification(
        cls,
        scheduler_id: str,
        delta: timedelta,
        scheduler: AsyncIOScheduler,
        uow: UnitOfWork,
    ):
        async with uow:
            notificaiton: NotificationModel = await uow.notification.find_one(
                scheduler_id=scheduler_id
            )
            new_time = notificaiton.deadline - delta

            # новое время может быть "просроченным"
            if TimezoneService.valid_date(date=new_time) is False:
                raise ValueError

            await uow.notification.update(
                {"notification": new_time}, scheduler_id=scheduler_id
            )
            await uow.commit()

        scheduler.modify_job(job_id=scheduler_id, next_run_time=new_time)

    @classmethod
    async def find_notifications(
        cls, task_id: str, uow: UnitOfWork
    ) -> list[NotificationModel] | None:
        async with uow:
            return await uow.notification.find_many(task_id=task_id)

    @classmethod
    async def update_many_notifications(
        cls,
        task_id: str,
        new_deadline: datetime,
        scheduler: AsyncIOScheduler,
        uow: UnitOfWork,
    ) -> str | None:
        """
        new_notification = old_notification - (old_deadline - new_deadline)
        """
        missed_notifications = []
        async with uow:
            task: TaskModel = await uow.task.find_one(task_id=task_id)
            new_deadline = TimezoneService.convert_to_tz(new_deadline, task.timezone)
            notifications: list[NotificationModel] = await uow.notification.find_many(
                task_id=task_id
            )
            # делаем циклом, тк дополнительно нужно менять время в scheduler
            for notification in notifications:
                new_notification = notification.notification - (
                    notification.deadline - new_deadline
                )

                # некоторые напоминания могут быть "просроченными", поэтому их удаляем
                if TimezoneService.valid_date(new_notification, task.timezone) is False:
                    await uow.notification.delete(
                        scheduler_id=notification.scheduler_id
                    )
                    scheduler.remove_job(job_id=notification.scheduler_id)
                    missed_notifications.append(notification)
                    continue

                await uow.notification.update(
                    {"deadline": new_deadline, "notification": new_notification},
                    scheduler_id=notification.scheduler_id,
                )
                scheduler.modify_job(
                    job_id=notification.scheduler_id,
                    next_run_time=new_notification,
                )
            await uow.commit()

        if len(missed_notifications) == 0:
            return None
        return TaskText.format_notifications(missed_notifications)

    @classmethod
    async def format_notifications(
        cls, task_id: str, uow: UnitOfWork
    ) -> tuple[int, str, dict] | Exception:
        """
        returns
            count of notifications\n
            formatted text with notifications in minute format\n
            state data: dict[number str: scheduler_id str uuid]
        """
        async with uow:
            notifications = await uow.notification.find_many(task_id=task_id)
            if notifications is None:
                raise ValueError
            k = 0
            state_data = {}
            text = ""
            for notification in notifications:
                notification: NotificationModel
                k += 1
                delta = (
                    notification.deadline - notification.notification
                ).total_seconds() // 60
                text += f"{k}. за {round(delta)} минут\n"
                state_data[str(k)] = notification.scheduler_id
            return k, text, state_data

    @classmethod
    def get_notification(cls, time: str) -> timedelta | None:
        if time.lower() == "за 1 час":
            return timedelta(hours=1)
        for message in time.split():
            try:
                return timedelta(minutes=int(message))
            except ValueError:
                continue
        return None

    @classmethod
    async def find_task_notificatoins(
        cls, task_id: str, uow: UnitOfWork
    ) -> list[str] | None:
        async with uow:
            notifications = await uow.notification.find_many(task_id=task_id)
        if len(notifications) == 0:
            return None
        return list(notification.scheduler_id for notification in notifications)

    @classmethod
    async def delete_notification(
        cls, scheduler_id: str, scheduler: AsyncIOScheduler, uow: UnitOfWork
    ):
        await cls.delete_many_notifications(scheduler, uow, scheduler_id=scheduler_id)

    @classmethod
    async def delete_many_notifications(
        cls, scheduler: AsyncIOScheduler, uow: UnitOfWork, **filter_params
    ):
        async with uow:  # интерпретация работы без транзакций
            await cls.delete_many_with_tx(scheduler, uow, **filter_params)
            await uow.commit()

    @classmethod
    async def delete_many_with_tx(
        cls, scheduler: AsyncIOScheduler, uow: UnitOfWork, **filter_params
    ):
        """
        решил сделать универсальным работу с напоминаниями.
        Тут не вызывается контекстный менеджер для поддержания работы транзакций
        """
        notifications: list[NotificationModel] = await uow.notification.find_many(
            **filter_params
        )
        await uow.notification.delete(**filter_params)

        for notification in notifications:
            scheduler.remove_job(job_id=notification.scheduler_id)
