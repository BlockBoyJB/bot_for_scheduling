from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from bot.config import Settings

from .repository import UserRepository, SectionRepository, TaskRepository, NotificationRepository

cfg = Settings()

engine = create_async_engine(cfg.pg_url, pool_size=20)
async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


class BaseContextRepo(ABC):
    def __init__(self):
        self.session = async_session_maker()

    @abstractmethod
    async def __aenter__(self):
        pass

    async def __aexit__(self, *args):
        await self.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()


class UnitOfWork(BaseContextRepo):
    async def __aenter__(self):
        self.user = UserRepository(self.session)
        self.section = SectionRepository(self.session)
        self.task = TaskRepository(self.session)
        self.notification = NotificationRepository(self.session)


# вынес отдельно, чтобы не инициализировать все сразу
class NotificationRepo(BaseContextRepo):
    async def __aenter__(self):
        self.notification = NotificationRepository(self.session)
