from dataclasses import dataclass
from App.Json_Class.DtoUtilities import *
from App.Json_Class.Kafka_dto import kafkas
from App.Json_Class.MongoDB_dto import mongodb
from App.Json_Class.Redis_dto import redis


@dataclass
class Services:
    MongoDB: mongodb
    Redis: redis
    Kafka: kafkas

    @staticmethod
    def from_dict(obj: Any) -> 'Services':
        assert isinstance(obj, dict)
        MongoDB = mongodb.from_dict(obj.get("MongoDB"))
        Redis = redis.from_dict(obj.get("Redis"))
        Kafka = kafkas.from_dict(obj.get("Kafka"))

        return Services(MongoDB, Redis, Kafka)

    def to_dict(self) -> dict:
        result: dict = {"MongoDB": to_class(mongodb, self.MongoDB),
                        "Redis": to_class(redis, self.Redis),
                        "Kafka": to_class(kafkas, self.Kafka)}
        return result
