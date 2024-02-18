from motor.motor_asyncio import AsyncIOMotorClient

from bot.config import Settings
from bot.repository import MongoDbRepository

conf = Settings()


class MongoDb:
    """
    Если честно, не знаю зачем решил сделать в виде контекстного меню.
    В будущем сделаю под транзакции (если вообще сделаю)
    """

    def __init__(self):
        self.__client = AsyncIOMotorClient(conf.mongo_url)
        self.__db = self.__client[conf.mongo_database]

    async def __aenter__(self):
        self.user = MongoDbRepository(self.__db["user"])
        self.subject = MongoDbRepository(self.__db["subject"])
        self.task = MongoDbRepository(self.__db["task"])
        self.deadline = MongoDbRepository(self.__db["deadline"])

    async def __aexit__(self, *args):
        pass
