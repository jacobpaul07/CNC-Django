from dataclasses import dataclass
from App.Json_Class.DtoUtilities import *


@dataclass
class kafkas:
    bootstrap_servers: str
    topicName: str
    group_id: str

    @staticmethod
    def from_dict(obj: Any) -> 'kafkas':
        assert isinstance(obj, dict)
        bootstrap_servers = from_str(obj.get("bootstrap_servers"))
        topicName = from_str(obj.get("topicName"))
        group_id = from_str(obj.get("group_id"))

        return kafkas(bootstrap_servers, topicName, group_id)

    def to_dict(self) -> dict:
        result: dict = {
            "bootstrap_servers": from_str(self.bootstrap_servers),
            "topicName": from_str(self.topicName),
            "group_id": from_str(self.group_id)
            }
        return result
