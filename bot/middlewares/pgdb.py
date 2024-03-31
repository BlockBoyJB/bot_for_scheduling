from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from bot.db import UnitOfWork


class DatabaseMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()
        self.uow = UnitOfWork()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ):
        data["uow"] = self.uow
        await handler(event, data)
