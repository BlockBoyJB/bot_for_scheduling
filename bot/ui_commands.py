from aiogram import Bot
from aiogram.types import BotCommand


async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Перезапустить бота"),
        BotCommand(command="create", description="Создать новый предмет"),
        BotCommand(command="subjects", description="Перейти к предметам"),
        BotCommand(command="hometasks", description="Посмотреть все задачи"),
        BotCommand(command="help", description="Помощь"),
        BotCommand(command="menu", description="Главное меню"),
    ]
    await bot.set_my_commands(commands=commands)
