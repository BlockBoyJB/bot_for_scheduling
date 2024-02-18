from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from bot.keyboards import SubjectKB
from bot.services import HometaskService, SubjectService, UserService
from bot.states import ChooseSubject, CreateSubject
from bot.utils.templates import CmdText, HometaskText, SubjectText

router = Router()


@router.message(Command("test"))
async def cmd_test(message: Message):
    # cmd for some tests
    await message.answer("ok!")


@router.message(Command("start"))
async def cmd_start(message: Message, mongo):
    if await UserService.find_user(user_id=message.from_user.id, mongo=mongo) is None:
        await UserService.add_user(user=message.from_user, mongo=mongo)
    await message.answer(text=CmdText.start, reply_markup=ReplyKeyboardRemove())


@router.message(Command("help"))
async def cmd_help(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(text=CmdText.help)


@router.message(Command("create"))
async def cmd_create_task(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(SubjectText.create, reply_markup=ReplyKeyboardRemove())
    await state.set_state(CreateSubject.choose_name)


@router.message(Command("menu"))
async def cmd_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(CmdText.menu, reply_markup=ReplyKeyboardRemove())


@router.message(Command("subjects"))
async def cmd_subjects(message: Message, state: FSMContext, mongo):
    subjects = await SubjectService.find_all_subjects(
        user_id=message.from_user.id, mongo=mongo
    )
    if subjects:
        await state.set_state(ChooseSubject.choose_subject)
        await state.update_data(subjects=subjects)
        await message.answer(
            text=SubjectText.subject, reply_markup=SubjectKB.cmd_subjects(subjects)
        )
    else:
        await message.answer(SubjectText.no_subjects)


@router.message(Command("hometasks"))
async def cmd_hometasks(message: Message, mongo):
    tasks = await HometaskService.find_all_hometasks(
        user_id=message.from_user.id, mongo=mongo
    )
    if tasks:
        text = tasks
    else:
        text = HometaskText.no_all_hometasks

    await message.answer(text=text, reply_markup=ReplyKeyboardRemove())
