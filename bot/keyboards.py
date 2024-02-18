from aiogram.utils.keyboard import (
    KeyboardButton,
    ReplyKeyboardBuilder,
    ReplyKeyboardMarkup,
)

from bot.utils.templates import Buttons


class SubjectKB:
    @classmethod
    def cmd_subjects(cls, subjects: list[str]) -> ReplyKeyboardMarkup:
        builder = ReplyKeyboardBuilder()
        for subject in subjects:
            builder.add(KeyboardButton(text=subject))
        builder.adjust(3)
        return builder.as_markup(resize_keyboard=True)

    @classmethod
    def subject_actions(cls) -> ReplyKeyboardMarkup:
        keyboard = [[KeyboardButton(text=item) for item in Buttons.subject_actions]]
        return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

    @classmethod
    def without_description(cls) -> ReplyKeyboardMarkup:
        keyboard = [[KeyboardButton(text="Без описания")]]
        return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


class HometaskKB:
    @classmethod
    def create_task(cls) -> ReplyKeyboardMarkup:
        keyboard = [[KeyboardButton(text="Создать новую задачу")]]
        return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

    @classmethod
    def enter_deadline(cls) -> ReplyKeyboardMarkup:
        builder = ReplyKeyboardBuilder()
        for item in Buttons.enter_deadline:
            builder.add(KeyboardButton(text=item))
        builder.adjust(3)
        return builder.as_markup(resize_keyboard=True)

    @classmethod
    def hometask_action(
        cls, notifications: bool = False, deadline: bool = False
    ) -> ReplyKeyboardMarkup:
        builder = ReplyKeyboardBuilder()
        for item in Buttons.hometask_action:
            builder.add(KeyboardButton(text=item))
        if notifications:
            builder.add(KeyboardButton(text="Редактировать напоминания"))
        if deadline:
            builder.add(KeyboardButton(text="Добавить напоминание"))
        builder.adjust(3)
        return builder.as_markup(resize_keyboard=True)


class NotificationKB:
    @classmethod
    def choose_time(cls, has_notifications: bool = False) -> ReplyKeyboardMarkup:
        buidler = ReplyKeyboardBuilder()
        for item in Buttons.set_notification:
            buidler.add(KeyboardButton(text=item))
        if has_notifications:
            buidler.add(KeyboardButton(text="Сохранить все значения"))
            buidler.add(KeyboardButton(text="Удалить все напоминания"))
        buidler.adjust(3)
        return buidler.as_markup(resize_keyboard=True)

    @classmethod
    def notification_actions(cls) -> ReplyKeyboardMarkup:
        keyboard = [
            [KeyboardButton(text=item) for item in Buttons.notification_actions]
        ]
        return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

    @classmethod
    def new_notification_time(cls) -> ReplyKeyboardMarkup:
        keyboard = [
            [
                KeyboardButton(text=item)
                for item in Buttons.set_notification
                if item != "Свое время"
            ]
        ]
        return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


class ServiceKB:
    @classmethod
    def numbers(cls, count: int) -> ReplyKeyboardMarkup:
        builder = ReplyKeyboardBuilder()
        for i in range(count):
            builder.add(KeyboardButton(text=str(i + 1)))
        builder.adjust(4)
        return builder.as_markup(resize_keyboard=True)

    @classmethod
    def yes_or_no(cls) -> ReplyKeyboardMarkup:
        keyboard = [[KeyboardButton(text="Да")], [KeyboardButton(text="Нет")]]
        return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
