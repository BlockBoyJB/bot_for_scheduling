from motor.core import AgnosticCollection


class MongoDbRepository:
    def __init__(self, collection: AgnosticCollection):
        self.collection = collection

    async def add_one(self, data: dict):
        await self.collection.insert_one(data)

    async def find_one(self, **filter_params) -> dict[str] | None:
        return await self.collection.find_one(filter_params)

    async def update_one(self, data: dict, **filter_params):
        await self.collection.update_one(filter_params, data)

    async def delete_one(self, **filter_params):
        await self.collection.delete_one(filter_params)

    async def find_many(self, **filter_params) -> list[dict] | None:
        result = [data async for data in self.collection.find(filter_params)]
        return None if len(result) == 0 else result

    async def update_many(self, data: dict, **filter_params):
        await self.collection.update_many(filter_params, data)

    async def delete_many(self, **filter_params):
        await self.collection.delete_many(filter_params)

    async def find_all(self) -> list[dict[str]] | None:
        return [data async for data in self.collection.find()]
