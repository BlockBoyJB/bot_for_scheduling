from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from sqlalchemy.exc import IntegrityError

from bot.keyboards import SectionKB
from bot.services import SectionService, UserService
from bot.states import ChooseSection, CreateSection
from bot.utils import CmdText, SectionText, TaskText

router = Router()


@router.message(Command("test"))
async def cmd_test(message: Message):
    await message.answer("ok!")


@router.message(Command("start"))
async def cmd_start(message: Message, uow):
    try:
        await UserService.add_user(message.from_user, uow)
    except IntegrityError:
        pass
    await message.answer(text=CmdText.start)


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
async def cmd_tasks(message: Message, uow):
    text = await UserService.find_all_tasks(user_id=message.from_user.id, uow=uow)
    if text:
        await message.answer(text=text, reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer(
            text=TaskText.no_one_task, reply_markup=ReplyKeyboardRemove()
        )
