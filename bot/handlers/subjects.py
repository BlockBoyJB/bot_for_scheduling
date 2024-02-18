from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from bot.keyboards import ServiceKB, SubjectKB
from bot.services import HometaskService, SubjectService, UserService
from bot.states import ChooseHometask, ChooseSubject, CreateSubject, EditSubject
from bot.utils.templates import HometaskText, SubjectText

router = Router()


@router.message(CreateSubject.choose_name)
async def add_entered_subject(message: Message, state: FSMContext, mongo):
    await SubjectService.add_subject(
        user_id=message.from_user.id, subject=message.text, mongo=mongo
    )
    await message.answer(text=SubjectText.subject_created.format(subject=message.text))
    await state.clear()


@router.message(ChooseSubject.choose_subject)
async def chosen_subject(message: Message, state: FSMContext):
    subjects = (await state.get_data())["subjects"]
    if message.text in subjects:
        await state.set_state(ChooseSubject.choose_action)
        await state.update_data(subject=message.text)

        await message.answer(
            text=SubjectText.subject_choose.format(subject=message.text),
            reply_markup=SubjectKB.subject_actions(),
        )

    else:
        await message.answer(
            text=SubjectText.wrong_subject_choose,
            reply_markup=SubjectKB.cmd_subjects(subjects),
        )


@router.message(ChooseSubject.choose_action, F.text.lower() == "посмотреть все задачи")
async def check_all_hometasks(message: Message, state: FSMContext, mongo):
    subject = await UserService.get_subject(state)
    try:
        count, text, state_data = await HometaskService.find_all_subject_hometasks(
            user_id=message.from_user.id, subject=subject, mongo=mongo
        )
        await state.update_data(tasks=state_data)
        await state.set_state(ChooseHometask.choose_hometask)
        await message.answer(text=text, reply_markup=ServiceKB.numbers(count))
    except TypeError:
        await message.answer(HometaskText.no_hometasks.format(subject=subject))


@router.message(ChooseSubject.choose_action, F.text.lower() == "редактировать название")
async def edit_subject(message: Message, state: FSMContext):
    await state.set_state(EditSubject.edit_name)
    await message.answer(SubjectText.new_name)


@router.message(EditSubject.edit_name)
async def edit_subject_name(message: Message, state: FSMContext, mongo):
    await SubjectService.update_subject_name(
        user_id=message.from_user.id,
        subject=await UserService.get_subject(state),
        new_name=message.text,
        mongo=mongo,
    )
    await message.answer(
        SubjectText.new_name_changed.format(new_name=message.text),
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message(ChooseSubject.choose_action, F.text.lower() == "удалить предмет")
async def confirm_delete_subject(message: Message, state: FSMContext):
    await state.set_state(EditSubject.delete_subject)
    await message.answer(
        text=SubjectText.confirm_delete, reply_markup=ServiceKB.yes_or_no()
    )


@router.message(EditSubject.delete_subject)
async def delete_subject(message: Message, state: FSMContext, mongo):
    subject = await UserService.get_subject(state)
    if message.text.lower() == "да":
        await SubjectService.delete_subject(
            user_id=message.from_user.id, subject=subject, mongo=mongo
        )
        await message.answer(
            text=SubjectText.delete_subject.format(subject=subject),
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        await message.answer(
            text=SubjectText.no_delete_subject,
            reply_markup=ReplyKeyboardRemove(),
        )
    await state.clear()
