from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from bot.keyboards import NotificationKB, ServiceKB, TaskKB
from bot.services import NotificationService, TaskService
from bot.states import (
    ChooseSection,
    ChooseTask,
    CreateNotification,
    CreateTask,
    UpdateNotification,
    UpdateTask,
)
from bot.utils import CmdText, NotificationText, TaskText

router = Router()


@router.message(CreateTask.enter_title)
async def enter_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(CreateTask.enter_deadline)
    await message.answer(
        text=TaskText.enter_deadline, reply_markup=TaskKB.enter_deadline()
    )


@router.message(CreateTask.enter_deadline)
async def enter_deadline(message: Message, state: FSMContext):
    if message.text.lower() == "свое время":
        await state.set_state(CreateTask.enter_custom_deadline)
        await message.answer(
            text=TaskText.enter_custom_deadline, reply_markup=ReplyKeyboardRemove()
        )
    else:
        try:
            if message.text.lower() == "без дедлайна":
                deadline = None
            else:
                deadline = await TaskService.get_deadline(message.text)

            await state.update_data(deadline=deadline)
            await state.set_state(CreateTask.enter_description)
            await message.answer(
                text=TaskText.enter_description, reply_markup=TaskKB.enter_description()
            )

        except ValueError:
            await message.answer(
                text=TaskText.incorrect_deadline, reply_markup=TaskKB.enter_deadline()
            )


@router.message(CreateTask.enter_custom_deadline)
async def enter_custom_deadline(message: Message, state: FSMContext):
    deadline = await TaskService.get_custom_deadline(message.text)
    if deadline:
        await state.update_data(deadline=deadline)
        await state.set_state(CreateTask.enter_description)
        await message.answer(
            text=TaskText.enter_description, reply_markup=TaskKB.enter_description()
        )
    else:
        await message.answer(
            text=TaskText.incorrect_custom_deadline, reply_markup=ReplyKeyboardRemove()
        )


@router.message(CreateTask.enter_description)
async def enter_description(message: Message, state: FSMContext, uow):
    """
    state data:
        section_id str uuid
        section str
        title str
        deadline datetime | None
    """
    data = await state.get_data()
    data["description"] = message.text
    task_id = await TaskService.add_task(task=data, uow=uow)
    if data["deadline"] is None:
        data["deadline"] = "Без дедлайна"
        section_id, section = data["section_id"], data["section"]
        await state.clear()
        await state.set_state(ChooseSection.choose_action)
        await state.update_data(section_id=section_id, section=section)
        await message.answer(
            text=TaskText.create.format(
                section=data["section"],
                title=data["title"],
                deadline=data["deadline"],
                description=data["description"],
            )
            + CmdText.default,
            reply_markup=TaskKB.create_task(),
        )
    else:
        await state.update_data(task_id=task_id)
        await state.set_state(CreateNotification.add_notification)
        await message.answer(
            text=TaskText.create.format(
                section=data["section"],
                title=data["title"],
                deadline=data["deadline"],
                description=data["description"],
            )
            + NotificationText.ask_notification,
            reply_markup=ServiceKB.yes_or_no(),
        )


@router.message(ChooseTask.choose_task)
async def choose_task(message: Message, state: FSMContext, uow):
    """
    state data:
        section_id: str uuid
        section: str
        tasks: dict[number: str, task_id: str]
    """
    data = await state.get_data()
    number = message.text
    try:
        task_id = data["tasks"][number]
        task_data = await TaskService.find_task_with_notifications(
            task_id=task_id, uow=uow
        )
        if task_data is None:
            raise KeyError
        task, notifications = task_data[0], task_data[1]
        text = await TaskText.format_task(task, notifications)
        text += "\n\nВыберите действия с задачей:"
        section_id, section = data["section_id"], data["section"]
        await state.clear()
        await state.set_state(ChooseTask.choose_action)
        await state.update_data(section_id=section_id, section=section, task_id=task_id)
        await message.answer(
            text=text,
            reply_markup=TaskKB.task_actions(
                has_notifications=(len(notifications) != 0),
                has_deadline=(task.deadline is not None),
            ),
        )
    except KeyError:
        await message.answer(TaskText.incorrect_number)


@router.message(ChooseTask.choose_action)
async def choose_action(message: Message, state: FSMContext, uow):
    """
    state data:
        section_id: str
        section: str
        task_id: str
    """
    text = "Введите новое значение "
    action = None
    kb = None
    data = await state.get_data()

    match message.text.lower():
        case "изменить название":
            action = UpdateTask.edit_title
            text += "для названия (рекомендуем короткое)"

        case "изменить дедлайн":
            action = UpdateTask.edit_deadline
            text += "для дедлайна (в формате ДД:ММ:ГГ ЧАС:МИН"

        case "редактировать описание":
            action = UpdateTask.edit_description
            text += "для описания"

        case "удалить задачу":
            action = UpdateTask.delete_task
            text = (
                "Внимание! Вы собираетесь удалить задачу!\n"
                "Данное действие будет невозможно отменить.\n"
                "Вы уверены, что хотите удалить задание?"
            )
            kb = ServiceKB.yes_or_no()

        case "редактировать напоминания":
            action = UpdateNotification.edit_notifications
            k, text, state_data = await NotificationService.format_notifications(
                task_id=data["task_id"], uow=uow
            )
            await state.update_data(notifications=state_data)
            text = "Выберите напоминание (нажмите на одну из цифр)\n" + text
            kb = ServiceKB.numbers(k)

        case "добавить напоминание":
            # Возможно, стоило сделать отдельную ручку
            action = CreateNotification.add_time_notification
            text = "Укажите, за сколько нужно напомнить о задаче\n(Нажмите на одну из кнопок)"
            task = await TaskService.find_task(task_id=data["task_id"], uow=uow)
            await state.update_data(deadline=task.deadline, title=task.title)
            kb = NotificationKB.choose_time()

    if action:
        await state.set_state(action)
        await message.answer(
            text=text, reply_markup=kb if kb else ReplyKeyboardRemove()
        )
    else:
        await message.answer(text="Пожалуйста, выбирайте только из списка доступных")


@router.message(UpdateTask.edit_title)
async def edit_title(message: Message, state: FSMContext, uow):
    """
    state data:
        section_id: str
        section: str
        task_id: str
    """
    data = await state.get_data()
    await TaskService.update_task_title(
        task_id=data["task_id"], new_title=message.text, uow=uow
    )
    await message.answer(
        text=TaskText.edit_title.format(new_title=message.text),
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message(UpdateTask.edit_description)
async def edit_description(message: Message, state: FSMContext, uow):
    """
    state data:
        section_id: str
        section: str
        task_id: str
    """
    data = await state.get_data()
    await TaskService.update_task_description(
        task_id=data["task_id"], description=message.text, uow=uow
    )
    await message.answer(
        text=TaskText.edit_description, reply_markup=ReplyKeyboardRemove()
    )


@router.message(UpdateTask.edit_deadline)
async def edit_deadline(message: Message, state: FSMContext, uow):
    """
    state data:
        section_id: str
        section: str
        task_id: str
    """
    data = await state.get_data()
    try:
        new_deadline = await TaskService.get_deadline(message.text)
        notifications = await NotificationService.find_notifications(
            task_id=data["task_id"], uow=uow
        )
        if notifications:
            text = await TaskText.format_notifications(notifications)
            await state.update_data(new_deadline=new_deadline)
            await state.set_state(UpdateNotification.update_notifications)
            await message.answer(
                text=TaskText.edit_deadline_with_notifications.format(
                    deadline=new_deadline, notifications=text
                ),
                reply_markup=TaskKB.update_notifications_actions(),
            )
        else:
            await TaskService.update_task_deadline(
                task_id=data["task_id"], deadline=new_deadline, uow=uow
            )
            await state.clear()
            await message.answer(
                text=TaskText.edit_deadline.format(deadline=new_deadline)
            )
    except ValueError:
        await message.answer(text=TaskText.incorrect_deadline)


@router.message(UpdateTask.delete_task)
async def delete_task(message: Message, state: FSMContext, scheduler, uow):
    data = await state.get_data()
    if message.text.lower() == "да":
        await TaskService.delete_task(
            task_id=data["task_id"], scheduler=scheduler, uow=uow
        )
        text = TaskText.delete_task
    else:
        text = TaskText.no_delete_task

    await message.answer(text=text, reply_markup=ReplyKeyboardRemove())
