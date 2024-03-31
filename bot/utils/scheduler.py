from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.db import NotificationRepo
from bot.db.repository import NotificationRepository


# async def load_tasks(scheduler: AsyncIOScheduler, bot: Bot):
#     uow = UnitOfWork()
#     async with uow:
#         data = await uow.notification.find_all()
#     for task in data:
#         message_data = {
#             "scheduler_id": task.scheduler_id,
#             "section": task.section,
#             "title": task.title,
#             "delta": task.deadline - task.notification,
#             "message": task.message,
#         }
#         scheduler.add_job(
#             send_message,
#             id=task.scheduler_id,
#             trigger="date",
#             next_run_time=task.notification,
#             args=[bot, task.user_id, message_data],
#         )


async def load_tasks(scheduler: AsyncIOScheduler, bot: Bot):
    repo = NotificationRepo()
    async with repo:
        notifications = await repo.notification.find_all()
    for notification in notifications:
        scheduler.add_job(
            send_message,
            id=notification.scheduler_id,
            trigger="date",
            next_run_time=notification.notification,
            args=[bot, notification.user_id, notification.scheduler_id],
        )


async def send_message(bot: Bot, user_id: int, scheduler_id: str):
    repo = NotificationRepo()
    async with repo:
        notification = await repo.notification.find_one(scheduler_id=scheduler_id)
        await repo.notification.delete(scheduler_id=scheduler_id)
        await repo.commit()

    minutes = (notification.deadline - notification.notification).total_seconds() // 60
    text = (
        f"Внимание! Дедлайн по задаче {notification.title} будет через {round(minutes)} минут!\n"
        f"Раздел: {notification.section}"
    )
    if notification.message:
        text += f"\nСообщение: {notification.message}"

    await bot.send_message(chat_id=user_id, text=text)
