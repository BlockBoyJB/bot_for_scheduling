from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from bot.keyboards import NotificationKB, TaskKB, ServiceKB
from bot.services import NotificationService, TaskService
from bot.states import CreateNotification, ChooseSection, UpdateNotification
from bot.utils import NotificationText
from bot.utils.templates import Buttons, CmdText

router = Router()


@router.message(CreateNotification.add_notification, F.text.lower() == "да")
async def yes_notification(message: Message, state: FSMContext):
    await state.set_state(CreateNotification.add_time_notification)
    await message.answer(
        text=NotificationText.add_notification,
        reply_markup=NotificationKB.choose_time(),
    )


@router.message(CreateNotification.add_notification, F.text.lower() == "нет")
async def no_notification(message: Message, state: FSMContext):
    data = await state.get_data()
    section_id, section = data["section_id"], data["section"]
    await state.clear()
    await state.set_state(ChooseSection.choose_action)
    await state.update_data(section_id=section_id, section=section)
    await message.answer(
        text=NotificationText.further_actions, reply_markup=TaskKB.create_task()
    )


@router.message(CreateNotification.add_time_notification)
async def add_notification(message: Message, state: FSMContext):
    """
    state data:
        section_id: str
        section: str
        title: str
        deadline: datetime
        task_id: str
    """
    data = await state.get_data()
    if message.text.lower() == "свое время":
        await state.set_state(CreateNotification.add_custom_time_notification)
        await message.answer(
            text=NotificationText.add_custom_notification,
            reply_markup=ReplyKeyboardRemove(),
        )
    elif message.text in Buttons.add_notification:
        delta = await NotificationService.get_notification(message.text)
        notification = data["deadline"] - delta
        await state.set_state(CreateNotification.add_message)
        await state.update_data(notification=notification)
        await message.answer(
            text=NotificationText.add_message, reply_markup=NotificationKB.add_message()
        )
    else:
        await message.answer(text=CmdText.incorrect_btn)


@router.message(CreateNotification.add_custom_time_notification)
async def add_custom_notification(message: Message, state: FSMContext):
    """
    state data:
        section_id: str
        section: str
        title: str
        deadline: datetime
        task_id: str
    """
    data = await state.get_data()
    delta = await NotificationService.get_notification(message.text)
    if delta:
        notification = data["deadline"] - delta
        await state.set_state(CreateNotification.add_message)
        await state.update_data(notification=notification)
        await message.answer(
            text=NotificationText.add_message, reply_markup=NotificationKB.add_message()
        )
    else:
        await message.answer(
            text="Неправильный формат!\n" + NotificationText.add_custom_notification
        )


@router.message(CreateNotification.add_message)
async def add_message(message: Message, state: FSMContext, bot, scheduler, uow):
    data = await state.get_data()
    if message.text.lower() == "без сообщения":
        data["message"] = None
    else:
        data["message"] = message.text

    await NotificationService.add_notification(
        user_id=message.from_user.id,
        task=data,
        scheduler=scheduler,
        bot=bot,
        uow=uow,
    )
    section_id, section = data["section_id"], data["section"]
    await state.clear()
    await state.set_state(ChooseSection.choose_action)
    await state.update_data(section_id=section_id, section=section)
    await message.answer(
        text=NotificationText.created_notification, reply_markup=TaskKB.create_task()
    )


@router.message(UpdateNotification.update_notifications)
async def update_notifications(message: Message, state: FSMContext, scheduler, uow):
    """
    state data:
        section_id: str
        section: str
        task_id: str
        new_deadline: datetime
    """
    data = await state.get_data()
    text = None
    await TaskService.update_task_deadline(
        task_id=data["task_id"], deadline=data["new_deadline"], uow=uow
    )

    match message.text.split()[0].lower():
        case "сохранить":
            await NotificationService.update_many_notifications(
                task_id=data["task_id"],
                new_deadline=data["new_deadline"],
                scheduler=scheduler,
                uow=uow,
            )
            text = NotificationText.save_notifications
        case "удалить":
            await NotificationService.delete_many_notifications(
                task_id=data["task_id"], scheduler=scheduler, uow=uow
            )
            text = NotificationText.delete_many_notifications
    if text:
        await message.answer(text=text, reply_markup=ReplyKeyboardRemove())

    else:
        await message.answer(CmdText.incorrect_btn)


@router.message(UpdateNotification.edit_notifications)
async def edit_notifications(message: Message, state: FSMContext):
    """
    state data:
        section_id: str
        section: str
        task_id: str
        notifications: dict[number str, scheduler_id str uuid]
    """
    data = await state.get_data()
    try:
        notification = data["notifications"][message.text]
        del data["notifications"]
        data["scheduler_id"] = notification
        await state.clear()
        await state.set_state(UpdateNotification.choose_action)
        await state.update_data(**data)
        await message.answer(
            text=NotificationText.choose_update_action,
            reply_markup=NotificationKB.notification_actions(),
        )
    except KeyError:
        await message.answer(text=CmdText.incorrect_btn)


@router.message(UpdateNotification.choose_action)
async def edit_time_notification(message: Message, state: FSMContext):
    text = None
    s = None
    kb = None
    match message.text.split()[0].lower():
        case "изменить":
            s = UpdateNotification.edit_time_notification
            text = "Нажмите на любую из кнопок, либо введите свое значение (обязательно в минутах!)"
            kb = NotificationKB.edit_notification()
        case "удалить":
            s = UpdateNotification.delete_notification
            text = (
                "Вы собираетесь удалить напоминание! Данное действие нельзя отменить. Вы уверены, что хотите "
                "удалить уведомление"
            )
            kb = ServiceKB.yes_or_no()
    if text:
        await state.set_state(s)
        await message.answer(text=text, reply_markup=kb)
    else:
        await message.answer(text=CmdText.incorrect_btn)


@router.message(UpdateNotification.edit_time_notification)
async def edit_time_notification(message: Message, state: FSMContext, scheduler, uow):
    data = await state.get_data()
    delta = await NotificationService.get_notification(message.text)
    if delta:
        await NotificationService.update_notification(
            scheduler_id=data["scheduler_id"], delta=delta, scheduler=scheduler, uow=uow
        )
        await message.answer(
            text=NotificationText.edit_time_notification,
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        await message.answer(text=NotificationText.incorrect_time_notification)


@router.message(UpdateNotification.delete_notification)
async def delete_notification(message: Message, state: FSMContext, scheduler, uow):
    data = await state.get_data()
    if message.text.lower() == "да":
        await NotificationService.delete_notification(
            scheduler_id=data["scheduler_id"], scheduler=scheduler, uow=uow
        )
        text = NotificationText.delete_notification
    else:
        text = NotificationText.no_delete_notification
    await message.answer(text=text, reply_markup=ReplyKeyboardRemove())
