import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.config import Settings
from bot.database import MongoDb
from bot.handlers import (
    cmd_router,
    hometask_router,
    notification_router,
    subject_router,
)
from bot.middlewares import BotMiddleware, MongoDBMiddleware, SchedulerMiddleware
from bot.storage import CustomRedisStorage
from bot.ui_commands import set_bot_commands
from bot.utils.scheduler import load_tasks


async def main():
    logging.basicConfig(level=logging.INFO)

    config = Settings()
    bot = Bot(token=config.bot_token.get_secret_value(), parse_mode="HTML")

    if config.fsm_mode == "redis":
        storage = CustomRedisStorage.from_url(
            url=config.redis_url,
            connection_kwargs={"decode_responses": True},
        )
    else:
        storage = MemoryStorage()

    scheduler = AsyncIOScheduler()
    scheduler.start()

    await load_tasks(scheduler=scheduler, bot=bot)

    scheduler.print_jobs()  # для наглядности

    dp = Dispatcher(storage=storage)

    # middlewares
    dp.update.middleware(MongoDBMiddleware(mongo=MongoDb))
    dp.update.middleware(SchedulerMiddleware(scheduler=scheduler))
    dp.update.middleware(BotMiddleware(bot=bot))

    # routers. Предпочитаю каждый прописывать отдельно для наглядности
    dp.include_router(cmd_router)
    dp.include_router(subject_router)
    dp.include_router(hometask_router)
    dp.include_router(notification_router)

    await set_bot_commands(bot=bot)

    try:
        print("Бот запущен!")
        await dp.start_polling(bot)

    finally:
        await storage.close()
        await bot.session.close()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
