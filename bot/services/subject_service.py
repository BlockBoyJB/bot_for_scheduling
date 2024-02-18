from datetime import datetime

from bot.database import MongoDb


class SubjectService:
    @classmethod
    async def add_subject(cls, user_id: int, subject: str, mongo: MongoDb):
        data = {
            "user_id": user_id,
            "subject": subject,
            "tasks": [],
            "create_date": datetime.now(),
        }
        async with mongo:
            await mongo.user.update_one(
                {"$push": {"subjects": subject}}, user_id=user_id
            )
            await mongo.subject.add_one(data)

    @classmethod
    async def find_subject(
        cls, user_id: int, subject: str, mongo: MongoDb
    ) -> dict | None:
        async with mongo:
            return await mongo.subject.find_one(user_id=user_id, subject=subject)

    @classmethod
    async def find_all_subjects(cls, user_id: int, mongo: MongoDb) -> None | list[str]:
        async with mongo:
            res = (await mongo.user.find_one(user_id=user_id))["subjects"]
            return None if len(res) == 0 else res

    @classmethod
    # Вот тут начинается дичь
    async def update_subject_name(
        cls, user_id: int, subject: str, new_name: str, mongo: MongoDb
    ):
        async with mongo:
            user_subjects = (await mongo.user.find_one(user_id=user_id))["subjects"]
            user_subjects.remove(subject)
            user_subjects.append(new_name)
            await mongo.user.update_one(
                {"$set": {"subjects": user_subjects}}, user_id=user_id
            )

            await mongo.subject.update_one(
                {"$set": {"subject": new_name}}, user_id=user_id
            )
            await mongo.task.update_many(
                {"$set": {"subject": new_name}}, user_id=user_id, subject=subject
            )

            await mongo.deadline.update_many(
                {"$set": {"subject": new_name}}, user_id=user_id, subject=subject
            )

    @classmethod
    async def delete_subject(cls, user_id: int, subject: str, mongo: MongoDb):
        async with mongo:
            await mongo.user.update_one(
                {"$pull": {"subjects": subject}}, user_id=user_id
            )
            await mongo.subject.delete_one(user_id=user_id, subject=subject)
            await mongo.task.delete_many(user_id=user_id, subject=subject)
            await mongo.deadline.delete_many(user_id=user_id, subject=subject)
