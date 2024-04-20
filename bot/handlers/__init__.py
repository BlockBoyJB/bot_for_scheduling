from aiogram import Router

from .cmd import router as cmd_router
from .notification import router as notification_router
from .section import router as section_router
from .task import router as task_router


def get_routers() -> list[Router]:
    return [cmd_router, section_router, task_router, notification_router]


__all__ = [
    "cmd_router",
    "section_router",
    "task_router",
    "notification_router",
    "get_routers",
]
