from dataclasses import dataclass
from App.Json_Class.DtoUtilities import *


@dataclass
class redis:
    IpAddress: str
    Port: str

    @staticmethod
    def from_dict(obj: Any) -> 'redis':
        assert isinstance(obj, dict)
        IpAddress = from_str(obj.get("IpAddress"))
        Port = from_str(obj.get("Port"))

        return redis(IpAddress, Port)

    def to_dict(self) -> dict:
        result: dict = {
            "IpAddress": from_str(self.IpAddress),
            "Port": from_str(self.Port),
            }
        return result
