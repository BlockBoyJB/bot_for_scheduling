from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery

from bot.keyboards import SectionKB, ServiceKB
from bot.services import UserService, SectionService, TaskService
from bot.utils import SectionText, TaskText
from bot.states import (
    CreateSection,
    ChooseSection,
    CreateTask,
    ChooseTask,
    UpdateSection,
)

router = Router()


@router.message(CreateSection.choose_name)
async def create_section(message: Message, state: FSMContext, uow):
    await SectionService.add_section(
        user_id=message.from_user.id, section=message.text, uow=uow
    )
    await message.answer(text=SectionText.create_success.format(section=message.text))
    await state.clear()


@router.callback_query(ChooseSection.choose_section)
async def choose_section(callback: CallbackQuery, state: FSMContext):
    """
    callback data: section_id (str)
    state data:
        sections: dict[section_id: uuid, section: str]

    after update:
        section_id: str uuid
        section: str
    """
    sections = (await state.get_data())["sections"]
    section = sections[callback.data]
    await state.clear()
    await callback.answer()
    await state.update_data(section_id=callback.data, section=section)
    await state.set_state(ChooseSection.choose_action)

    await callback.message.answer(
        text=SectionText.chosen_section.format(section=section),
        reply_markup=SectionKB.section_actions(),
    )


@router.message(ChooseSection.choose_action, F.text.lower() == "посмотреть все задачи")
async def check_all_tasks(message: Message, state: FSMContext, uow):
    data = await state.get_data()

    try:
        k, text, state_data = await TaskService.find_all_tasks_with_notifications(
            section_id=data["section_id"], uow=uow
        )
        # state_data - dict[str(number), task_id]
        await state.update_data(tasks=state_data)
        await state.set_state(ChooseTask.choose_task)
        await message.answer(text=text, reply_markup=ServiceKB.numbers(k))
    except ValueError:
        await message.answer(text=TaskText.no_task.format(section=data["section"]))


@router.message(ChooseSection.choose_action, F.text.lower() == "редактировать название")
async def edit_section_name(message: Message, state: FSMContext):
    await state.set_state(UpdateSection.edit_name)
    await message.answer(TaskText.edit_name)


@router.message(UpdateSection.edit_name)
async def edit_name(message: Message, state: FSMContext, uow):
    date = await state.get_data()
    await SectionService.update_name(
        section_id=date["section_id"], new_name=message.text, uow=uow
    )
    await message.answer(
        SectionText.edit_name.format(new_name=message.text),
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message(ChooseSection.choose_action, F.text.lower() == "создать новую задачу")
async def create_new_task(message: Message, state: FSMContext):
    await state.set_state(CreateTask.enter_title)
    await message.answer(text=TaskText.enter_title, reply_markup=ReplyKeyboardRemove())


@router.message(ChooseSection.choose_action, F.text.lower() == "удалить раздел")
async def confirm_delete_section(message: Message, state: FSMContext):
    await state.set_state(UpdateSection.delete_section)
    await message.answer(
        SectionText.confirm_delete_section, reply_markup=ServiceKB.yes_or_no()
    )


@router.message(UpdateSection.delete_section)
async def delete_section(message: Message, state: FSMContext, uow):
    data = await state.get_data()
    if message.text.lower() == "да":
        await SectionService.delete_section(
            section_id=data["section_id"], uow=uow
        )
        text = SectionText.delete_section.format(section=data["section"])
    else:
        text = SectionText.no_delete_section

    await message.answer(text=text, reply_markup=ReplyKeyboardRemove())
    await state.clear()
