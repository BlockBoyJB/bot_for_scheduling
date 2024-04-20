import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.config import Settings
from bot.handlers import cmd_router, notification_router, section_router, task_router
from bot.middlewares import BotMiddleware, DatabaseMiddleware, SchedulerMiddleware
from bot.utils import CustomRedisStorage, load_tasks, set_bot_commands


async def main():
    logging.basicConfig(level=logging.INFO)

    config = Settings()
    bot = Bot(token=config.bot_token.get_secret_value())

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
    dp.update.middleware(DatabaseMiddleware())
    dp.message.middleware(BotMiddleware(bot=bot))
    dp.message.middleware(SchedulerMiddleware(scheduler=scheduler))

    # routers. Предпочитаю каждый прописывать отдельно для наглядности
    dp.include_router(cmd_router)
    dp.include_router(section_router)
    dp.include_router(task_router)
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
