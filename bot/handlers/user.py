from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from bot.keyboards import UserKB
from bot.services import TaskService, UserService
from bot.states import SettingsActions, UserActions
from bot.utils import CmdText, TimezoneService, UserText

router = Router()


@router.message(UserActions.create_user)
async def create_user(message: Message, uow):
    tz = None
    if message.text.lower() == "пропустить":
        tz = "+3"  # дефолт решил сделать мск время
    elif TimezoneService.is_timezone(message.text):
        tz = message.text

    if tz:
        await UserService.add_user(user=message.from_user, tz=tz, uow=uow)
        await message.answer(
            text=UserText.user_created, reply_markup=ReplyKeyboardRemove()
        )
    else:
        await message.answer(UserText.incorrect_tz)


@router.message(UserActions.delete_user)
async def delete_user(message: Message, uow):
    if message.text.lower() == "да":
        await UserService.delete_user(user_id=message.from_user.id, uow=uow)
        await message.answer(
            text=UserText.user_deleted, reply_markup=ReplyKeyboardRemove()
        )
    else:
        await message.answer(
            text=UserText.user_not_deleted, reply_markup=ReplyKeyboardRemove()
        )


@router.message(UserActions.settings)
async def settings(message: Message, state: FSMContext):
    text = None
    action = None
    match message.text.lower():
        case "изменить пояс":
            action = SettingsActions.edit_timezone
            text = 'Введите новое значение для часового пояса относительно UTC\nНапример: "+2" или "-4"'

    if text and action:
        await state.set_state(action)
        await message.answer(text=text, reply_markup=ReplyKeyboardRemove())

    else:
        await message.answer(text=CmdText.incorrect_btn)


@router.message(SettingsActions.edit_timezone)
async def edit_timezone(message: Message, state: FSMContext, uow):
    if TimezoneService.is_timezone(message.text):
        tasks = await UserService.find_all_tasks_with_deadline(
            user_id=message.from_user.id, uow=uow
        )
        reply = None
        if len(tasks) != 0:
            await state.set_state(SettingsActions.reformat_tasks)
            await state.update_data(tasks=tasks, tz=message.text)
            text = UserText.edit_timezone_with_tasks
            reply = UserKB.edit_timezone()
        else:
            await UserService.update_tz(
                user_id=message.from_user.id, tz=message.text, uow=uow
            )
            text = UserText.update_timezone

        await message.answer(text=text, reply_markup=reply)

    else:
        await message.answer(UserText.incorrect_tz)


@router.message(SettingsActions.reformat_tasks)
async def reformat_tasks(message: Message, state: FSMContext, scheduler, uow):
    # state data: tasks: list[task_id] - все задачи, в которых указан дедлайн
    """
    state data:
        tasks: list[task_id]
        tz: str
    """
    data = await state.get_data()
    text = None
    tasks, tz = [], data["tz"]
    match message.text.lower():
        case "перенести все задачи":
            text = UserText.update_tz_with_tasks
            tasks = data["tasks"]
        case "оставить без изменений":
            text = UserText.update_tz_without_tasks

    if text:
        await TaskService.update_tasks_timezone(
            *tasks,
            user_id=message.from_user.id,
            new_tz=tz,
            scheduler=scheduler,
            uow=uow,
        )
        await message.answer(text=text, reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer(text=CmdText.incorrect_btn)
