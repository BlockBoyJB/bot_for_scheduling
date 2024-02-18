from datetime import datetime, timedelta

import datefinder
from apscheduler.jobstores.base import JobLookupError
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.database import MongoDb
from bot.utils.templates import HometaskText, NotificationText


class HometaskService:
    @classmethod
    async def create_hometask(cls, user_id: int, data: dict, mongo: MongoDb):
        """
        data:
            subject: str
            title: str
            deadline: datetime | timedelta | None
            description: str
        """
        data = data.copy()
        if isinstance(data["deadline"], timedelta):
            data["deadline"] = datetime.now().replace(microsecond=0) + data["deadline"]

        data["user_id"] = user_id
        data["notifications"] = []
        data["scheduler_id"] = []
        data["create_date"] = datetime.now().replace(microsecond=0)

        async with mongo:
            await mongo.task.add_one(data)
            await mongo.subject.update_one(
                {"$push": {"tasks": data["title"]}}, user_id=user_id
            )

    @classmethod
    async def find_hometask(
        cls, user_id: int, subject: str, title: str, mongo: MongoDb
    ):
        async with mongo:
            return await mongo.task.find_one(
                user_id=user_id, subject=subject, title=title
            )

    @classmethod
    async def find_all_hometasks(cls, user_id: int, mongo: MongoDb) -> str | None:
        async with mongo:
            hometasks = await mongo.task.find_many(user_id=user_id)
            if hometasks:
                return await HometaskText.format_all_tasks(hometasks)
            return None

    @classmethod
    async def delete_hometask(
        cls,
        user_id: int,
        subject: str,
        title: str,
        scheduler: AsyncIOScheduler,
        mongo: MongoDb,
    ):
        async with mongo:
            await mongo.task.delete_one(user_id=user_id, subject=subject, title=title)
            await mongo.subject.update_one(
                {"$pull": {"tasks": title}}, user_id=user_id, subject=subject
            )
            notifications = await mongo.deadline.find_many(
                user_id=user_id, subject=subject, title=title
            )
            await mongo.deadline.delete_many(
                user_id=user_id, subject=subject, title=title
            )
        try:
            if notifications:
                for notification in notifications:
                    scheduler.remove_job(job_id=notification["scheduler_id"])
        except JobLookupError:
            pass

    @classmethod
    async def find_all_subject_hometasks(
        cls, user_id: int, subject: str, mongo: MongoDb
    ) -> tuple[int, str, dict] | Exception:
        async with mongo:
            hometasks = await mongo.task.find_many(user_id=user_id, subject=subject)
        if hometasks:
            return await HometaskText.format_all_subject_tasks(hometasks)
        else:
            raise TypeError

    @classmethod
    # {number: scheduler_id}
    async def format_all_notifications(
        cls, user_id: int, data: dict, mongo: MongoDb
    ) -> tuple[int, dict[str, str], str] | None:
        async with mongo:
            task = await mongo.task.find_one(
                user_id=user_id, subject=data["subject"], title=data["title"]
            )
        if task is None:
            return None
        return await NotificationText.format_notification(
            deadline=task["deadline"],
            scheduler_id=task["scheduler_id"],
            notifications=task["notifications"],
        )

    @classmethod
    async def get_deadline(cls, text: str) -> timedelta | datetime | Exception:
        match text.lower():
            case "через 5 минут":
                return timedelta(minutes=5)
            case "через 10 минут":
                return timedelta(minutes=10)
            case "через 15 минут":
                return timedelta(minutes=15)
            case "через 30 минут":
                return timedelta(minutes=30)
            case "через 1 час":
                return timedelta(hours=1)
            case _:
                try:
                    return next(datefinder.find_dates(text=text, first="day"))
                except StopIteration:
                    raise ValueError

    @classmethod
    async def get_custom_time(cls, time: str) -> timedelta | None:
        for message in time.split():
            try:
                return timedelta(minutes=int(message))
            except ValueError:
                continue
        return None

    @classmethod
    async def update_hometask_title(
        cls, user_id, data: dict, scheduler: AsyncIOScheduler, mongo: MongoDb
    ):
        # data: {subject: str, title: str, new_title: str}
        async with mongo:
            subject_tasks = (
                await mongo.subject.find_one(user_id=user_id, subject=data["subject"])
            )["tasks"]
            subject_tasks.remove(data["title"])
            subject_tasks.append(data["new_title"])
            await mongo.subject.update_one(
                {"$set": {"tasks": subject_tasks}},
                user_id=user_id,
                subject=data["subject"],
            )
            await mongo.task.update_one(
                {"$set": {"title": data["new_title"]}},
                user_id=user_id,
                subject=data["subject"],
                title=data["title"],
            )
            await mongo.deadline.update_many(
                {"$set": {"title": data["new_title"]}},
                user_id=user_id,
                subject=data["subject"],
                title=data["title"],
            )
            notifications = await mongo.deadline.find_many(
                user_id=user_id, subject=data["subject"], title=data["title"]
            )
        try:
            for notification in notifications:
                scheduler.modify_job(
                    job_id=notification["scheduler_id"],
                    kwargs={"new_title": data["new_title"]},
                )
        except JobLookupError:
            pass

    @classmethod
    async def update_description(
        cls, user_id: int, subject: str, title: str, description: str, mongo: MongoDb
    ):
        async with mongo:
            await mongo.task.update_one(
                {"$set": {"description": description}},
                user_id=user_id,
                subject=subject,
                title=title,
            )

    @classmethod
    async def update_deadline(
        cls, user_id: int, subject: str, title: str, deadline: datetime, mongo: MongoDb
    ):
        async with mongo:
            await mongo.task.update_one(
                {"$set": {"deadline": deadline}},
                user_id=user_id,
                subject=subject,
                title=title,
            )
