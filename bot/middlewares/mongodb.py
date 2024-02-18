from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class MongoDBMiddleware(BaseMiddleware):
    def __init__(self, mongo):
        super().__init__()
        self.mongo = mongo

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ):
        data["mongo"] = self.mongo()
        await handler(event, data)
