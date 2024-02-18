from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.database import MongoDb


async def load_tasks(scheduler: AsyncIOScheduler, bot: Bot):
    mongo = MongoDb()
    async with mongo:
        data = await mongo.deadline.find_all()
    for doc in data:
        message_data = {
            "title": doc["title"],
            "subject": doc["subject"],
            "delta": doc["deadline"] - doc["notification"],
            "scheduler_id": doc["scheduler_id"],
        }
        scheduler.add_job(
            send_message,
            id=doc["scheduler_id"],
            trigger="date",
            next_run_time=doc["notification"],
            args=[bot, doc["user_id"], message_data],
        )


async def send_message(bot: Bot, user_id: int, data: dict, **kwargs):
    """
    data: dict: {
        title: str,
        subject: str,
        delta: datetime,
        scheduler_id: str-uuid
    """
    if "new_title" in kwargs.keys():
        data["title"] = kwargs["new_title"]
    mongo = MongoDb()
    async with mongo:
        deadline = await mongo.deadline.find_one(scheduler_id=data["scheduler_id"])
        await mongo.deadline.delete_one(scheduler_id=data["scheduler_id"])
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
    minutes = data["delta"].total_seconds() // 60
    text = (
        f"Внимание! Дедлайн по задаче {data['title']} будет\n"
        f"через {round(minutes)} минут\n"
        f"Предмет: {data['subject']}"
    )

    await bot.send_message(chat_id=user_id, text=text)
