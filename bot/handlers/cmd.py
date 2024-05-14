from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from bot.keyboards import SectionKB, ServiceKB, TaskKB, UserKB
from bot.services import SectionService, UserService
from bot.states import AllTasks, ChooseSection, CreateSection, CreateTask, UserActions
from bot.utils import CmdText, SectionText, TaskText, UserText

router = Router()


@router.message(Command("test"))
async def cmd_test(message: Message):
    await message.answer("ok!")


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.set_state(UserActions.create_user)
    await message.answer(
        text=UserText.create, reply_markup=ServiceKB.one_button("Пропустить")
    )


@router.message(Command("stop"))
async def cmd_stop(message: Message, state: FSMContext):
    await state.set_state(UserActions.delete_user)
    await message.answer(
        text=UserText.confirm_delete, reply_markup=ServiceKB.yes_or_no()
    )


@router.message(Command("settings"))
async def cmd_settings(message: Message, state: FSMContext):
    await state.set_state(UserActions.settings)
    await message.answer(text=UserText.settings, reply_markup=UserKB.settings())


@router.message(Command("help"))
async def cmd_help(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(CmdText.help, reply_markup=ReplyKeyboardRemove())


@router.message(Command("menu"))
async def cmd_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(CmdText.menu, reply_markup=ReplyKeyboardRemove())


@router.message(Command("new_section"))
async def cmd_new_section(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(CreateSection.choose_name)
    await message.answer(SectionText.create, reply_markup=ReplyKeyboardRemove())


@router.message(Command("sections"))
async def cmd_sections(message: Message, state: FSMContext, uow):
    await state.clear()
    sections = await SectionService.find_all_sections(
        user_id=message.from_user.id, uow=uow
    )
    if sections:
        await state.set_state(ChooseSection.choose_section)
        await state.update_data(sections=sections)
        await message.answer(
            text=SectionText.choose_section,
            reply_markup=SectionKB.cmd_sections(sections),
        )
    else:
        await message.answer(SectionText.no_sections)


@router.message(Command("tasks"))
async def cmd_tasks(message: Message, state: FSMContext, uow):
    await state.clear()
    text = await UserService.find_all_tasks(user_id=message.from_user.id, uow=uow)
    if text:
        await state.set_state(AllTasks.delete_all_tasks)
        await message.answer(text=text, reply_markup=TaskKB.delete_all_tasks())
    else:
        await message.answer(
            text=TaskText.no_one_task, reply_markup=ReplyKeyboardRemove()
        )


@router.message(Command("new_task"))
async def cmd_new_task(message: Message, state: FSMContext, uow):
    await state.clear()
    sections = await SectionService.find_all_sections(
        user_id=message.from_user.id, uow=uow
    )
    if sections:
        await state.set_state(CreateTask.choose_section)
        await state.update_data(sections=sections)
        await message.answer(
            text=SectionText.choose_section,
            reply_markup=SectionKB.cmd_sections(sections),
        )
    else:
        await message.answer(SectionText.no_sections)
