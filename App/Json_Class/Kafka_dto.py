from dataclasses import dataclass
from App.Json_Class.DtoUtilities import *


@dataclass
class kafkas:
    bootstrap_servers: str
    topicName: str
    group_id: str
    cloudEnabled: str
    cloudServers: str

    @staticmethod
    def from_dict(obj: Any) -> 'kafkas':
        assert isinstance(obj, dict)
        bootstrap_servers = from_str(obj.get("bootstrap_servers"))
        topicName = from_str(obj.get("topicName"))
        group_id = from_str(obj.get("group_id"))
        cloudEnabled = from_str(obj.get("cloudEnabled"))
        cloudServers = from_str(obj.get("cloudServers"))

        return kafkas(bootstrap_servers, topicName, group_id, cloudEnabled, cloudServers)

    def to_dict(self) -> dict:
        result: dict = {
            "bootstrap_servers": from_str(self.bootstrap_servers),
            "topicName": from_str(self.topicName),
            "group_id": from_str(self.group_id),
            "cloudEnabled": from_str(self.cloudEnabled),
            "cloudServers": from_str(self.cloudServers)
            }
        return result
