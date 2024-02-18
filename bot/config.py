from enum import Enum

from dotenv import load_dotenv
from pydantic import SecretStr
from pydantic_settings import BaseSettings

load_dotenv()


class FSMMode(str, Enum):
    MEMORY = "memory"
    REDIS = "redis"


class Settings(BaseSettings):
    bot_token: SecretStr
    fsm_mode: FSMMode
    redis_host: str
    redis_port: int

    mongo_host: str
    mongo_port: int

    mongo_database: str

    @property
    def redis_url(self):
        return f"redis://{self.redis_host}:{self.redis_port}"

    @property
    def mongo_url(self):
        return f"mongodb://{self.mongo_host}:{self.mongo_port}"
