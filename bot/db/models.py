from datetime import datetime, timedelta, timezone

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeMeta, Mapped, declarative_base, mapped_column
from sqlalchemy.sql.functions import now

from .schemas import NotificationModel, SectionModel, TaskModel, UserModel

Base: DeclarativeMeta = declarative_base()


tz = timezone(timedelta(hours=3))


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(nullable=False, unique=True)
    username: Mapped[str | None] = mapped_column(nullable=True)
    first_name: Mapped[str | None] = mapped_column(nullable=True)
    last_name: Mapped[str | None] = mapped_column(nullable=True)
    create_date: Mapped[datetime] = mapped_column(default=now())

    def to_read_model(self) -> UserModel:
        return UserModel(
            id=self.id,
            user_id=self.user_id,
            username=self.username,
            first_name=self.first_name,
            last_name=self.last_name,
            create_date=self.create_date,
        )


class Section(Base):
    __tablename__ = "section"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.user_id", ondelete="cascade"), nullable=False
    )
    section_id: Mapped[str] = mapped_column(nullable=False, unique=True)
    section: Mapped[str] = mapped_column(nullable=False)
    create_date: Mapped[datetime] = mapped_column(default=now())

    def to_read_model(self) -> SectionModel:
        return SectionModel(
            id=self.id,
            user_id=self.user_id,
            section_id=self.section_id,
            section=self.section,
            create_date=self.create_date,
        )


class Task(Base):
    __tablename__ = "task"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    section_id: Mapped[str] = mapped_column(
        ForeignKey("section.section_id", ondelete="cascade"), nullable=False
    )
    task_id: Mapped[str] = mapped_column(unique=True, nullable=False)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    deadline: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    create_date: Mapped[datetime] = mapped_column(default=now())

    def to_read_model(self) -> TaskModel:
        return TaskModel(
            id=self.id,
            section_id=self.section_id,
            task_id=self.task_id,
            title=self.title,
            description=self.description,
            deadline=self.deadline,
            create_date=self.create_date,
        )


class Notification(Base):
    __tablename__ = "notification"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.user_id", ondelete="cascade"), nullable=False
    )
    section_id: Mapped[str] = mapped_column(
        ForeignKey("section.section_id", ondelete="cascade"), nullable=False
    )
    task_id: Mapped[str] = mapped_column(
        ForeignKey("task.task_id", ondelete="cascade"), nullable=False
    )
    deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    notification: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    scheduler_id: Mapped[str] = mapped_column(unique=True, nullable=False)
    section: Mapped[str] = mapped_column(nullable=False)
    title: Mapped[str] = mapped_column(nullable=False)
    message: Mapped[str | None] = mapped_column(nullable=True)

    def to_read_model(self) -> NotificationModel:
        return NotificationModel(
            id=self.id,
            user_id=self.user_id,
            section_id=self.section_id,
            task_id=self.task_id,
            deadline=self.deadline,
            notification=self.notification,
            scheduler_id=self.scheduler_id,
            section=self.section,
            title=self.title,
            message=self.message,
        )
