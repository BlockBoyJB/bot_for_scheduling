from aiogram import BaseMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler


class SchedulerMiddleware(BaseMiddleware):
    def __init__(self, scheduler: AsyncIOScheduler):
        super().__init__()
        self.scheduler = scheduler

    async def __call__(self, handler, event, data):
        data["scheduler"] = self.scheduler
        await handler(event, data)
