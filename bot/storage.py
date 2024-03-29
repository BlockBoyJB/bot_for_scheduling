from datetime import datetime, timedelta
from json import JSONDecoder, JSONEncoder, dumps, loads
from typing import Any, Dict, Optional, cast

from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.redis import KeyBuilder, RedisStorage, _JsonDumps, _JsonLoads
from redis.asyncio import Redis
from redis.typing import ExpiryT


class DateTimeAwareJSONEncoder(JSONEncoder):
    """
    Converts a python object, where datetime and timedelta objects are converted
    into objects that can be decoded using the DateTimeAwareJSONDecoder.
    """

    def default(self, obj):
        if isinstance(obj, datetime):
            return {
                "__type__": "datetime",
                "year": obj.year,
                "month": obj.month,
                "day": obj.day,
                "hour": obj.hour,
                "minute": obj.minute,
                "second": obj.second,
                "microsecond": obj.microsecond,
            }

        elif isinstance(obj, timedelta):
            return {
                "__type__": "timedelta",
                "days": obj.days,
                "seconds": obj.seconds,
                "microseconds": obj.microseconds,
            }

        else:
            return JSONEncoder.default(self, obj)


class DateTimeAwareJSONDecoder(JSONDecoder):
    """
    Converts a json string, where datetime and timedelta objects were converted
    into objects using the DateTimeAwareJSONEncoder, back into a python object.
    """

    def __init__(self):
        JSONDecoder.__init__(self, object_hook=self.dict_to_object)

    @staticmethod
    def dict_to_object(d):
        if "__type__" not in d:
            return d

        type = d.pop("__type__")
        if type == "datetime":
            return datetime(**d)
        elif type == "timedelta":
            return timedelta(**d)
        else:
            d["__type__"] = type
            return d


class CustomRedisStorage(RedisStorage):
    """
    Переписал дефолтное редис хранилище, тк с datetime и timedelta имеются проблемы
    (json не переваривает их). Поэтому чуток кастомизировал под свои требования
    Требует небольшой оптимизации, тк на мой взгляд два if get() выглядят костыльно
    """

    def __init__(
        self,
        redis: Redis,
        key_builder: Optional[KeyBuilder] = None,
        state_ttl: Optional[ExpiryT] = None,
        data_ttl: Optional[ExpiryT] = None,
        json_loads: _JsonLoads = loads,
        json_dumps: _JsonDumps = dumps,
    ):
        super().__init__(
            redis, key_builder, state_ttl, data_ttl, json_loads, json_dumps
        )
        self.encode = DateTimeAwareJSONEncoder().encode
        self.decode = DateTimeAwareJSONDecoder().decode

    async def set_data(self, key: StorageKey, data: Dict[str, Any]) -> None:
        redis_key = self.key_builder.build(key, "data")
        if not data:
            await self.redis.delete(redis_key)
            return
        if data.get("deadline"):
            data["deadline"] = self.encode(data["deadline"])
        if data.get("old_deadline"):
            data["old_deadline"] = self.encode(data["old_deadline"])
        await self.redis.set(
            redis_key,
            self.json_dumps(data),
            ex=self.data_ttl,
        )

    async def get_data(self, key: StorageKey) -> Dict[str, Any]:
        redis_key = self.key_builder.build(key, "data")
        value = await self.redis.get(redis_key)
        if value is None:
            return {}
        if isinstance(value, bytes):
            value = value.decode("utf-8")
        data: dict = self.json_loads(value)
        if data.get("deadline"):
            data["deadline"] = self.decode(data["deadline"])
        if data.get("old_deadline"):
            data["old_deadline"] = self.decode(data["old_deadline"])
        return cast(Dict[str, Any], data)
