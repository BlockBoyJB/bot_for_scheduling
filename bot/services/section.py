from uuid import uuid4

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State

from bot.db import SectionModel, UnitOfWork


class SectionService:
    @classmethod
    async def add_section(cls, user_id: int, section: str, uow: UnitOfWork):
        data = {
            "user_id": user_id,
            "section_id": str(uuid4()),
            "section": section,
        }
        async with uow:
            await uow.section.add_one(data)
            await uow.commit()

    @classmethod
    async def find_all_sections(
        cls, user_id: int, uow: UnitOfWork
    ) -> dict[str, str] | None:
        """
        :return: dict[section_id: uuid, section: str]
        """
        async with uow:
            data: list[SectionModel] = await uow.section.find_many(user_id=user_id)

        if data:
            # делаем такой 200IQ мув, потому что пользователь может создать с одинаковым названием и массив сломается
            sections = {}
            for s in data:
                sections[s.section_id] = s.section
            return sections
        else:
            return None

    @classmethod
    async def update_name(cls, section_id: str, new_name: str, uow: UnitOfWork):
        data = {"section": new_name}
        async with uow:
            await uow.section.update(data, section_id=section_id)
            await uow.notification.update(data, section_id=section_id)
            await uow.commit()

    @classmethod
    async def save_section(cls, state: FSMContext, action: State = None, clear=False):
        """
        Вынес повторяющееся действие с разделом в отдельную функцию.
        По-сути, просто перезаписываем state

        :param state: ну эээ state, который будем обновлять
        :param action: Опциональное действие (в некоторых ручках требуется перезаписать состояние
        :param clear: Иногда нужно полностью очищать state
        """
        data = await state.get_data()
        section_id, section = data["section_id"], data["section"]

        if clear:
            await state.clear()
        if action:
            await state.set_state(action)

        await state.update_data(section_id=section_id, section=section)

    @classmethod
    async def delete_section(cls, section_id: str, uow: UnitOfWork):
        async with uow:
            await uow.section.delete(section_id=section_id)
            await uow.commit()

    @classmethod
    async def delete_all_sections(cls, user_id: int, uow: UnitOfWork):
        async with uow:
            await uow.section.delete(user_id=user_id)
            await uow.commit()
