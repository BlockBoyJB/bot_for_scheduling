from aiogram import BaseMiddleware, Bot


class BotMiddleware(BaseMiddleware):
    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot

    async def __call__(self, handler, event, data):
        data["bot"] = self.bot
        await handler(event, data)
