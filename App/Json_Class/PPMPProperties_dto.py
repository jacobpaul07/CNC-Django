from dataclasses import dataclass
from typing import Any, Optional, List, TypeVar, Callable, Type, cast
from App.Json_Class.DtoUtilities import *


@dataclass
class PPMPPropertiess:
    Enable: str
    contentspec: str
    timestamp: str

    @staticmethod
    def from_dict(obj: Any) -> 'PPMPPropertiess':
        assert isinstance(obj, dict)
        Enable = from_str(obj.get("Enable"))
        contentspec = from_str(obj.get("contentspec"))
        timestamp = from_str(obj.get("timestamp"))
        return PPMPPropertiess(Enable, contentspec, timestamp)

    def to_dict(self) -> dict:
        result: dict = {"Enable": from_str(self.Enable), "contentspec": from_str(self.contentspec),
                        "timestamp": from_str(self.timestamp)}
        return result
