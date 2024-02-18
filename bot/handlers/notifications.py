from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from bot.keyboards import HometaskKB, NotificationKB
from bot.services import NotificationService, UserService
from bot.states import ChooseSubject, CreateHometask, HometaskNotification
from bot.utils.templates import Buttons, HometaskText, NotificationText

router = Router()


@router.message(CreateHometask.add_notification, F.text.lower() == "да")
async def notification_to_hometask(message: Message, state: FSMContext):
    await state.set_state(CreateHometask.set_time)
    await message.answer(
        text=NotificationText.set_notification,
        reply_markup=NotificationKB.choose_time(),
    )


@router.message(CreateHometask.add_notification, F.text.lower() == "нет")
async def no_notification_to_task(message: Message, state: FSMContext):
    subject = await UserService.get_subject(state)
    await state.clear()
    await state.set_state(ChooseSubject.choose_action)
    await state.update_data(subject=subject)
    await message.answer(
        NotificationText.further_actions, reply_markup=HometaskKB.create_task()
    )


@router.message(CreateHometask.set_time)
async def set_hometask_notification(
    message: Message, state: FSMContext, scheduler, bot, mongo
):
    # {subject: str, title: str, deadline: datetime | timedelta | None}
    data = await state.get_data()
    if message.text.lower() == "свое время":
        await state.set_state(CreateHometask.set_custom_time)
        await message.answer(
            text=NotificationText.set_custom_notificaion,
            reply_markup=ReplyKeyboardRemove(),
        )

    elif message.text in Buttons.set_notification:
        notification = await NotificationService.get_notification(text=message.text)
        time_notification = data["deadline"] - notification
        await NotificationService.set_notification(
            user_id=message.from_user.id,
            subject=data["subject"],
            title=data["title"],
            deadline=data["deadline"],
            notification=time_notification,
            scheduler=scheduler,
            bot=bot,
            mongo=mongo,
        )
        subject = data["subject"]
        await state.clear()
        await state.set_state(ChooseSubject.choose_action)
        await state.update_data(subject=subject)
        await message.answer(
            text=NotificationText.created_notification,
            reply_markup=HometaskKB.create_task(),
        )
    else:
        await message.answer(text=NotificationText.incorrect_notification_btn)


@router.message(CreateHometask.set_custom_time)
async def set_hometask_custom_time(
    message: Message, state: FSMContext, scheduler, bot, mongo
):
    data = await state.get_data()
    try:
        notification = data["deadline"] - await NotificationService.get_notification(
            text=message.text
        )
        await NotificationService.set_notification(
            user_id=message.from_user.id,
            subject=data["subject"],
            title=data["title"],
            deadline=data["deadline"],
            notification=notification,
            scheduler=scheduler,
            bot=bot,
            mongo=mongo,
        )
        subject = data["subject"]
        await state.clear()
        await state.set_state(ChooseSubject.choose_action)
        await state.update_data(subject=subject)
        await message.answer(
            text=NotificationText.created_notification,
            reply_markup=HometaskKB.create_task(),
        )
    except ValueError:
        await message.answer(text=NotificationText.set_custom_notificaion)


@router.message(HometaskNotification.edit_notification)
async def update_notification(
    message: Message, state: FSMContext, scheduler, bot, mongo
):
    """
    cases:
        За х минут  }
        За 1 час    } => удаляем все, оставляем новое
        Свое время  }
        Сохранить все значения
        Удалить все напоминания

    data: {subject: str, title: str, deadline: datetime, old_deadline: datetime}
    """
    data = await state.get_data()
    text = None
    match message.text.split()[0].lower():
        case "свое":
            await state.set_state(CreateHometask.set_custom_time)
            text = NotificationText.set_custom_notificaion
            await NotificationService.delete_many_notifications(
                user_id=message.from_user.id,
                data=data,
                scheduler=scheduler,
                mongo=mongo,
            )

        case "сохранить":
            await NotificationService.update_notfications(
                user_id=message.from_user.id,
                data=data,
                scheduler=scheduler,
                mongo=mongo,
            )
            text = NotificationText.save_notifications

        case "удалить":
            await NotificationService.delete_many_notifications(
                user_id=message.from_user.id,
                data=data,
                scheduler=scheduler,
                mongo=mongo,
            )
            text = NotificationText.delete_many_notifications

        case "за":
            await NotificationService.delete_many_notifications(
                user_id=message.from_user.id,
                data=data,
                scheduler=scheduler,
                mongo=mongo,
            )
            notification = data[
                "deadline"
            ] - await NotificationService.get_notification(message.text)
            await NotificationService.set_notification(
                user_id=message.from_user.id,
                subject=data["subject"],
                title=data["title"],
                deadline=data["deadline"],
                notification=notification,
                scheduler=scheduler,
                bot=bot,
                mongo=mongo,
            )
            text = NotificationText.new_notification.format(
                notification=message.text.lower()
            )

    if text:
        await message.answer(text=text, reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer(text=NotificationText.incorrect_notification_btn)


@router.message(HometaskNotification.update_notifications)
async def action_update_task_notifications(message: Message, state: FSMContext):
    # data: {subject: str, title: str, notifications: dict[number: str-uuid]}
    data = await state.get_data()
    try:
        number = message.text
        await state.clear()
        await state.update_data(
            {
                "subject": data["subject"],
                "title": data["title"],
                "scheduler_id": data["notifications"][number],
            }
        )
        await state.set_state(HometaskNotification.choose_update_action)
        await message.answer(
            text=NotificationText.choose_update_action,
            reply_markup=NotificationKB.notification_actions(),
        )
    except KeyError:
        await message.answer(text=NotificationText.incorrect_notification_btn)


@router.message(HometaskNotification.choose_update_action)
async def chosen_update_notification_action(
    message: Message, state: FSMContext, scheduler, mongo
):
    data = await state.get_data()
    if message.text.lower() == "изменить время напоминания":
        await state.set_state(HometaskNotification.new_notification_time)
        await message.answer(
            text=NotificationText.new_time_notification,
            reply_markup=NotificationKB.new_notification_time(),
        )
    elif message.text.lower() == "удалить напоминание":
        await NotificationService.delete_notification(
            user_id=message.from_user.id, data=data, scheduler=scheduler, mongo=mongo
        )
        await message.answer(
            text=NotificationText.delete_notification,
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        await message.answer(NotificationText.incorrect_notification_btn)


@router.message(HometaskNotification.new_notification_time)
async def update_notification_time(
    messsage: Message, state: FSMContext, scheduler, mongo
):
    data = await state.get_data()
    delta = await NotificationService.get_notification(messsage.text)
    if delta:
        data["delta"] = delta
        await NotificationService.update_notification(
            user_id=messsage.from_user.id, data=data, scheduler=scheduler, mongo=mongo
        )
        await messsage.answer(
            text=NotificationText.update_notification,
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        await messsage.answer(HometaskText.incorrect_custom_deadline)
