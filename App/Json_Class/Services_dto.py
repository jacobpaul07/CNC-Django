from dataclasses import dataclass
from App.Json_Class.DtoUtilities import *
from App.Json_Class.MongoDB_dto import mongodb
from App.Json_Class.Redis_dto import redis


@dataclass
class Services:
    MongoDB: mongodb
    Redis: redis

    @staticmethod
    def from_dict(obj: Any) -> 'Services':
        assert isinstance(obj, dict)
        MongoDB = mongodb.from_dict(obj.get("MongoDB"))
        Redis = redis.from_dict(obj.get("Redis"))

        return Services(MongoDB, Redis)

    def to_dict(self) -> dict:
        result: dict = {"MongoDB": to_class(mongodb, self.MongoDB),
                        "Redis": to_class(redis, self.Redis)}
        return result
