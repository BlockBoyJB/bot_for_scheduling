from uuid import uuid4

from bot.db import UnitOfWork, SectionModel


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
    async def find_all_sections(cls, user_id: int, uow: UnitOfWork) -> dict[str, str] | None:
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
    async def delete_section(cls, section_id: str, uow: UnitOfWork):
        async with uow:
            await uow.section.delete(section_id=section_id)
            await uow.commit()
