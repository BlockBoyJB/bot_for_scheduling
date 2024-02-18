from datetime import datetime

from aiogram.fsm.context import FSMContext
from aiogram.types import User

from bot.database import MongoDb


class UserService:
    @classmethod
    async def add_user(cls, user: User, mongo: MongoDb):
        data = {
            "user_id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "subjects": [],
            "create_date": datetime.now(),
        }
        async with mongo:
            await mongo.user.add_one(data)

    @classmethod
    async def find_user(cls, user_id: int, mongo: MongoDb) -> dict | None:
        async with mongo:
            return await mongo.user.find_one(user_id=user_id)

    @classmethod
    async def get_subject(cls, state: FSMContext) -> str:
        return (await state.get_data())["subject"]
