from aiogram import Bot
from aiogram.types import BotCommand


async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Перезапуск бота"),
        BotCommand(command="new_section", description="Создать новый раздел"),
        BotCommand(command="sections", description="Перейти к разделам"),
        BotCommand(command="tasks", description="Посмотреть все задачи"),
        BotCommand(command="help", description="Помощь"),
        BotCommand(command="menu", description="Главное меню"),
    ]
    await bot.set_my_commands(commands=commands)
