from datetime import datetime, timedelta
from uuid import uuid4

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.database import MongoDb
from bot.utils.scheduler import send_message


class NotificationService:
    @classmethod
    async def set_notification(
        cls,
        user_id: int,
        subject: str,
        title: str,
        deadline: datetime,
        notification: datetime,
        scheduler: AsyncIOScheduler,
        bot: Bot,
        mongo: MongoDb,
    ):
        scheduler_id = str(uuid4())
        data = {
            "user_id": user_id,
            "deadline": deadline,
            "notification": notification,
            "scheduler_id": scheduler_id,
            "subject": subject,
            "title": title,
        }
        async with mongo:
            await mongo.deadline.add_one(data)
            await mongo.task.update_one(
                {
                    "$push": {
                        "notifications": notification,
                        "scheduler_id": scheduler_id,
                    }
                },
                user_id=user_id,
                subject=subject,
                title=title,
            )
        delta = deadline - notification
        message_data = {
            "subject": subject,
            "title": title,
            "delta": delta,
            "scheduler_id": scheduler_id,
        }

        scheduler.add_job(
            send_message,
            id=scheduler_id,
            trigger="date",
            next_run_time=notification,
            args=[bot, user_id, message_data],
        )

    @classmethod
    async def get_notification(cls, text: str) -> timedelta | None:
        if text.lower() == "за 1 час":
            return timedelta(hours=1)
        for message in text.split():
            try:
                return timedelta(minutes=int(message))
            except ValueError:
                continue

    @classmethod
    # дичь
    async def update_notification(
        cls, user_id: int, data: dict, scheduler: AsyncIOScheduler, mongo: MongoDb
    ):
        # data: {subject: str, title: str, delta: timedelta, scheduler_id: str-uuid}
        async with mongo:
            deadline = await mongo.deadline.find_one(scheduler_id=data["scheduler_id"])
            new_notificaton = deadline["deadline"] - data["delta"]
            task = await mongo.task.find_one(
                user_id=user_id, subject=data["subject"], title=data["title"]
            )
            notifications: list = task["notifications"]
            schedulers: list = task["scheduler_id"]
            notifications.remove(deadline["notification"])
            # напоминания и scheduler_id находятся в упорядоченном виде, поэтому лишнее действие необходимо
            schedulers.remove(data["scheduler_id"])

            notifications.append(new_notificaton)
            schedulers.append(data["scheduler_id"])
            await mongo.task.update_one(
                {"$set": {"notifications": notifications, "scheduler_id": schedulers}},
                user_id=user_id,
                subject=data["subject"],
                title=data["title"],
            )
            await mongo.deadline.update_one(
                {"$set": {"notification": new_notificaton}},
                scheduler_id=data["scheduler_id"],
            )
        scheduler.modify_job(job_id=data["scheduler_id"], next_run_time=new_notificaton)

    @classmethod
    async def delete_notification(
        cls, user_id: int, data: dict, scheduler: AsyncIOScheduler, mongo: MongoDb
    ):
        # data: {subject: str, title: str, scheduler_id: str-uuid}
        async with mongo:
            deadline = await mongo.deadline.find_one(scheduler_id=data["scheduler_id"])
            await mongo.task.update_one(
                {
                    "$pull": {
                        "notifications": deadline["notification"],
                        "scheduler_id": data["scheduler_id"],
                    }
                },
                user_id=user_id,
                subject=data["subject"],
                title=data["title"],
            )
            await mongo.deadline.delete_one(scheduler_id=data["scheduler_id"])
        scheduler.remove_job(job_id=data["scheduler_id"])

    @classmethod
    async def check_deadline_type(cls, deadline: datetime | timedelta) -> datetime:
        if isinstance(deadline, timedelta):
            return datetime.now().replace(microsecond=0) + deadline
        return deadline

    @classmethod
    async def find_notifications(
        cls, user_id: int, subject: str, title: str, mongo: MongoDb
    ) -> tuple[datetime, list[datetime]] | None:
        async with mongo:
            task = await mongo.task.find_one(
                user_id=user_id, subject=subject, title=title
            )
            task_notifications = task["notifications"]
            return (
                None
                if len(task_notifications) == 0
                else (task["deadline"], task_notifications)
            )

    @classmethod
    # тут какая то дичь творится прошу прощения
    async def update_notfications(
        cls, user_id: int, data: dict, scheduler: AsyncIOScheduler, mongo: MongoDb
    ):
        """
        data : {subject: str, title: str, deadline: datetime, old_deadline: datetime}
        """
        async with mongo:
            # task already has a new deadline
            task = await mongo.task.find_one(
                user_id=user_id, subject=data["subject"], title=data["title"]
            )
            new_notifications = []
            notifications = task["notifications"]
            for i in range(len(notifications)):
                delta = data["old_deadline"] - notifications[i]
                new_time = task["deadline"] - delta
                new_notifications.append(new_time)
                await mongo.deadline.update_one(
                    {"$set": {"notification": new_time}},
                    user_id=user_id,
                    subject=data["subject"],
                    title=data["title"],
                    scheduler_id=task["scheduler_id"][i],
                )
                scheduler.modify_job(
                    job_id=task["scheduler_id"][i], next_run_time=new_time
                )
            await mongo.task.update_one(
                {"$set": {"notifications": new_notifications}},
                user_id=user_id,
                subject=data["subject"],
                title=data["title"],
            )

    @classmethod
    async def delete_many_notifications(
        cls, user_id: int, data: dict, scheduler: AsyncIOScheduler, mongo: MongoDb
    ):
        async with mongo:
            notifications = await mongo.deadline.find_many(
                user_id=user_id, subject=data["subject"], title=data["title"]
            )
            await mongo.task.update_one(
                {"$set": {"notifications": [], "scheduler_id": []}},
                user_id=user_id,
                subject=data["subject"],
                title=data["title"],
            )
            await mongo.deadline.delete_many(
                user_id=user_id, subject=data["subject"], title=data["title"]
            )
        if notifications:
            for notification in notifications:
                scheduler.remove_job(job_id=notification["scheduler_id"])
