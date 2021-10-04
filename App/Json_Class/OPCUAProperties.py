from dataclasses import dataclass
from App.Json_Class.DtoUtilities import *


@dataclass
class OPCProperties:
    Enable: str
    ClientName: str
    url: str
    UpdateTime: str
    Param: str
    RetryCount: str
    RecoveryTime: str

    @staticmethod
    def from_dict(obj: Any) -> 'OPCProperties':
        assert isinstance(obj, dict)
        Enable = from_str(obj.get("Enable"))
        ClientName = from_str(obj.get("ClientName"))
        url = from_str(obj.get("url"))
        UpdateTime = from_str(obj.get("UpdateTime"))
        Param = from_str(obj.get("Param"))
        RetryCount = from_str(obj.get("RetryCount"))
        RecoveryTime = from_str(obj.get("RecoveryTime"))
        return OPCProperties(Enable, ClientName, url, UpdateTime, Param, RetryCount, RecoveryTime)

    def to_dict(self) -> dict:
        result: dict = {
            "Enable": from_str(self.Enable),
            "ServerName": from_str(self.ClientName),
            "url": from_str(self.url),
            "UpdateTime": from_str(self.UpdateTime),
            "Param": from_str(self.Param),
            "RetryCount": from_str(self.RetryCount),
            "RecoveryTime": from_str(self.RecoveryTime)
            }
        return result
