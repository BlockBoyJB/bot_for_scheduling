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

    # redis_url: str

    pg_host: str
    pg_port: int
    pg_user: str
    pg_pass: str
    pg_db: str

    test_pg_host: str
    test_pg_port: int
    test_pg_user: str
    test_pg_pass: str
    test_pg_db: str

    # pg_url: str
    @property
    def redis_url(self):
        return f"redis://{self.redis_host}:{self.redis_port}"

    @property
    def pg_url(self):
        return f"postgresql+asyncpg://{self.pg_user}:{self.pg_pass}@{self.pg_host}:{self.pg_port}/{self.pg_db}"

    @property
    def test_pg_url(self):
        return f"postgresql+asyncpg://{self.test_pg_user}:{self.test_pg_pass}@{self.test_pg_host}:{self.test_pg_port}/{self.test_pg_db}"
