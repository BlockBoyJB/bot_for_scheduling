from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from bot.keyboards import HometaskKB, NotificationKB, ServiceKB, SubjectKB
from bot.services import HometaskService, NotificationService
from bot.states import (
    ChooseHometask,
    ChooseSubject,
    CreateHometask,
    HometaskNotification,
)
from bot.utils.templates import CmdText, HometaskText

router = Router()


@router.message(ChooseSubject.choose_action, F.text.lower() == "создать новую задачу")
async def create_hometask(message: Message, state: FSMContext):
    await state.set_state(CreateHometask.enter_title)
    await message.answer(
        text=HometaskText.enter_title, reply_markup=ReplyKeyboardRemove()
    )


@router.message(CreateHometask.enter_title)
async def entered_hometask_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(CreateHometask.enter_deadline)
    await message.answer(
        text=HometaskText.enter_deadline, reply_markup=HometaskKB.enter_deadline()
    )


@router.message(CreateHometask.enter_deadline)
async def entered_deadline(message: Message, state: FSMContext):
    if message.text.lower() == "свое время":
        await state.set_state(CreateHometask.set_custom_deadline)
        await message.answer(
            text=HometaskText.set_custom_deadline, reply_markup=ReplyKeyboardRemove()
        )
    else:
        try:
            if message.text.lower() == "без дедлайна":
                deadline = None
            else:
                deadline = await HometaskService.get_deadline(message.text)

            await state.update_data(deadline=deadline)
            await state.set_state(CreateHometask.enter_description)
            await message.answer(
                text=HometaskText.enter_description,
                reply_markup=SubjectKB.without_description(),
            )

        except ValueError:
            await message.answer(
                text=HometaskText.incorrect_deadline,
                reply_markup=HometaskKB.enter_deadline(),
            )


@router.message(CreateHometask.set_custom_deadline)
async def enter_custom_deadline(message: Message, state: FSMContext):
    deadline = await HometaskService.get_custom_time(message.text)
    if deadline:
        await state.update_data(deadline=deadline)
        await state.set_state(CreateHometask.enter_description)
        await message.answer(
            text=HometaskText.enter_description,
            reply_markup=SubjectKB.without_description(),
        )
    else:
        await message.answer(
            HometaskText.incorrect_custom_deadline, reply_markup=ReplyKeyboardRemove()
        )


@router.message(CreateHometask.enter_description)
async def entered_description(message: Message, state: FSMContext, mongo):
    """
    state data:
        subject: str,
        title: str,
        deadline: datetime | timedelta | None
    """
    data = await state.get_data()
    data["description"] = message.text
    await HometaskService.create_hometask(
        user_id=message.from_user.id, data=data, mongo=mongo
    )
    if data["deadline"] is None:
        data["deadline"] = "без дедлайна"
        subject = data["subject"]
        await state.clear()
        await state.set_state(ChooseSubject.choose_action)
        await state.update_data(subject=subject)
        await message.answer(
            text=HometaskText.create_hometask.format(**data) + CmdText.default,
            reply_markup=HometaskKB.create_task(),
        )
    else:
        deadline = await NotificationService.check_deadline_type(data["deadline"])
        data["deadline"] = deadline
        await state.update_data(deadline=deadline)
        await state.set_state(CreateHometask.add_notification)

        await message.answer(
            text=HometaskText.create_hometask.format(**data)
            + HometaskText.add_notification,
            reply_markup=ServiceKB.yes_or_no(),
        )


@router.message(ChooseHometask.choose_hometask)
async def chosen_hometask(message: Message, state: FSMContext, mongo):
    """
    state data:
        subjects: list[str]
        subject: str
        tasks: dict[number: title]
    """
    try:
        number = message.text
        data = await state.get_data()
        subject = data["subject"]
        title = data["tasks"][number]
        hometask = await HometaskService.find_hometask(
            user_id=message.from_user.id, subject=subject, title=title, mongo=mongo
        )
        text = await HometaskText.format_task(hometask)
        text += "\n\nВыберите дальнейшие действия с заданием:"
        await state.clear()  # ненужный мусор хранится
        await state.set_state(ChooseHometask.choose_action)

        await state.update_data(subject=subject, title=title)
        await message.answer(
            text=text,
            reply_markup=HometaskKB.hometask_action(
                notifications=(len(hometask["notifications"]) != 0),
                deadline=(hometask["deadline"] is not None),
            ),
        )
    except ValueError:  # KeyError
        await message.answer(HometaskText.incorrect_number)


@router.message(ChooseHometask.choose_action)
async def chosen_hometask_action(message: Message, state: FSMContext, mongo):
    text = "Введите новое значение "
    action = None
    kb = None
    data = await state.get_data()

    match message.text.lower():
        case "изменить название":
            action = ChooseHometask.edit_title
            text += "для названия (рекомендуем короткое)"

        case "изменить дедлайн":
            action = ChooseHometask.edit_deadline
            text += "для дедлайна (в формате ДД:ММ:ГГ ЧАС:МИН)"

        case "редактировать описание":
            action = ChooseHometask.edit_description
            text += "для описания"

        case "удалить задачу":
            action = ChooseHometask.delete_task
            text = (
                "Внимание! Вы собираетесь удалить задачу!\n"
                "Данное действие будет невозможно отменить.\n"
                "Вы уверены, что хотите удалить задание?"
            )
            kb = ServiceKB.yes_or_no()

        case "редактировать напоминания":
            action = HometaskNotification.update_notifications
            # state_data: {number: scheduler_id}
            k, state_data, text = await HometaskService.format_all_notifications(
                user_id=message.from_user.id, data=data, mongo=mongo
            )
            await state.update_data(notifications=state_data)
            text = "Выберите напоминание (нажмите на одну из цифр)\n" + text
            kb = ServiceKB.numbers(k)

        case "добавить напоминание":
            task = await HometaskService.find_hometask(
                user_id=message.from_user.id,
                subject=data["subject"],
                title=data["title"],
                mongo=mongo,
            )
            await state.update_data(deadline=task["deadline"])
            action = CreateHometask.set_time
            text = "Укажите за сколько нужно напомнить о задаче\n" "(Нажмите на кнопку)"
            kb = NotificationKB.choose_time()

    if action:
        await state.set_state(action)
        await message.answer(
            text=text, reply_markup=kb if kb else ReplyKeyboardRemove()
        )
    else:
        await message.answer(text="Пожалуйста, выбирайте только из списка доступных")


@router.message(ChooseHometask.edit_title)
async def update_hometask_title(message: Message, state: FSMContext, scheduler, mongo):
    # {subject: str, title: str}
    data = await state.get_data()
    data["new_title"] = message.text
    await HometaskService.update_hometask_title(
        user_id=message.from_user.id, data=data, scheduler=scheduler, mongo=mongo
    )
    await message.answer(
        text=HometaskText.update_title.format(
            title=data["title"], new_title=message.text
        ),
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message(ChooseHometask.edit_description)
async def update_hometask_description(message: Message, state: FSMContext, mongo):
    data = await state.get_data()
    await HometaskService.update_description(
        user_id=message.from_user.id,
        subject=data["subject"],
        title=data["title"],
        description=message.text,
        mongo=mongo,
    )
    await message.answer(
        text=HometaskText.update_description.format(title=data["title"]),
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message(ChooseHometask.edit_deadline)
async def update_hometask_deadline(message: Message, state: FSMContext, mongo):
    data = await state.get_data()
    try:
        deadline = await HometaskService.get_deadline(message.text)

        deadline_data = await NotificationService.find_notifications(
            user_id=message.from_user.id,
            subject=data["subject"],
            title=data["title"],
            mongo=mongo,
        )
        await HometaskService.update_deadline(
            user_id=message.from_user.id,
            subject=data["subject"],
            title=data["title"],
            deadline=deadline,
            mongo=mongo,
        )
        if deadline_data:
            old_deadline, notifications = deadline_data
            text = HometaskText.deadline_with_notifications.format(
                deadline=deadline,
                notifications=await HometaskText.format_notifications(
                    old_deadline, notifications
                ),
            )
            await state.update_data(deadline=deadline, old_deadline=old_deadline)
            await state.set_state(HometaskNotification.edit_notification)
            await message.answer(
                text=text,
                reply_markup=NotificationKB.choose_time(has_notifications=True),
            )
        else:
            text = HometaskText.update_deadline.format(deadline=deadline)
            await message.answer(text=text)

    except ValueError:
        await message.answer(HometaskText.incorrect_deadline)


@router.message(ChooseHometask.delete_task)
async def delete_task(message: Message, state: FSMContext, scheduler, mongo):
    data = await state.get_data()
    if message.text.lower() == "да":
        await HometaskService.delete_hometask(
            user_id=message.from_user.id,
            subject=data["subject"],
            title=data["title"],
            scheduler=scheduler,
            mongo=mongo,
        )
        text = HometaskText.success_delete_hometask.format(title=data["title"])
    else:
        text = HometaskText.no_delete_hometask

    await message.answer(text=text, reply_markup=ReplyKeyboardRemove())
