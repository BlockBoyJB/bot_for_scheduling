from aiogram.types import InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from bot.utils.templates import Buttons


class ServiceKB:
    @classmethod
    def yes_or_no(cls) -> ReplyKeyboardMarkup:
        keyboard = [[KeyboardButton(text="Да")], [KeyboardButton(text="Нет")]]
        return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

    @classmethod
    def numbers(cls, k: int) -> ReplyKeyboardMarkup:
        builder = ReplyKeyboardBuilder()
        for i in range(k):
            builder.add(KeyboardButton(text=str(i + 1)))
        builder.adjust(4)
        return builder.as_markup(resize_keyboard=True)


class SectionKB:
    @classmethod
    def cmd_sections(cls, sections: dict[str, str]) -> ReplyKeyboardMarkup:
        """
        sections: {section_uuid: section_name}
        """
        builder = InlineKeyboardBuilder()
        for sid, name in sections.items():
            builder.add(
                InlineKeyboardButton(
                    text=name,
                    callback_data=sid,
                )
            )
        builder.adjust(4)
        return builder.as_markup()  # TODO resize keyboard???

    @classmethod
    def section_actions(cls) -> ReplyKeyboardMarkup:
        keyboard = [[KeyboardButton(text=item) for item in Buttons.section_actions]]
        return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


class TaskKB:
    @classmethod
    def create_task(cls) -> ReplyKeyboardMarkup:
        keyboard = [[KeyboardButton(text="Создать новую задачу")]]
        return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

    @classmethod
    def enter_deadline(cls) -> ReplyKeyboardMarkup:
        builder = ReplyKeyboardBuilder()
        for item in Buttons.enter_deadline:
            builder.add(KeyboardButton(text=item))

        builder.adjust(4)
        return builder.as_markup(resize_keyboard=True)

    @classmethod
    def enter_description(cls) -> ReplyKeyboardMarkup:
        keyboard = [[KeyboardButton(text="Без описания")]]
        return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

    @classmethod
    def task_actions(
        cls, has_notifications=False, has_deadline=False
    ) -> ReplyKeyboardMarkup:
        builder = ReplyKeyboardBuilder()
        for item in Buttons.task_actions:
            builder.add(KeyboardButton(text=item))
        if has_notifications:
            builder.add(KeyboardButton(text="Редактировать напоминания"))
        if has_deadline:
            builder.add(KeyboardButton(text="Добавить напоминание"))
        builder.adjust(3)
        return builder.as_markup(resize_keyboard=True)

    @classmethod
    def update_notifications_actions(cls) -> ReplyKeyboardMarkup:
        keyboard = [
            [KeyboardButton(text=item) for item in Buttons.update_notifications_actions]
        ]
        return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


class NotificationKB:
    @classmethod
    def choose_time(cls) -> ReplyKeyboardMarkup:
        builder = ReplyKeyboardBuilder()
        for item in Buttons.add_notification:
            builder.add(KeyboardButton(text=item))
        builder.adjust(4)
        return builder.as_markup(resize_keyboard=True)

    @classmethod
    def add_message(cls) -> ReplyKeyboardMarkup:
        keyboard = [[KeyboardButton(text="Без сообщения")]]
        return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

    @classmethod
    def notification_actions(cls) -> ReplyKeyboardMarkup:
        keyboard = [
            [KeyboardButton(text=item) for item in Buttons.notification_actions]
        ]
        return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

    @classmethod
    def edit_notification(cls) -> ReplyKeyboardMarkup:
        builder = ReplyKeyboardBuilder()
        for item in Buttons.add_notification:
            if item != "Свое время":
                builder.add(KeyboardButton(text=item))
        builder.adjust(3)
        return builder.as_markup(resize_keyboard=True)
