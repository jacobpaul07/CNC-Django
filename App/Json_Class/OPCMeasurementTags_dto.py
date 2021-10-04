from dataclasses import dataclass
from typing import Any, Optional, List, TypeVar, Callable, Type, cast
from App.Json_Class.DtoUtilities import *



@dataclass
class MeasurementTags:
    NameSpace: str
    Identifier: str
    DisplayName: str
    InitialValue: str

    @staticmethod
    def from_dict(obj: Any) -> 'MeasurementTags':
        assert isinstance(obj, dict)
        NameSpace = from_str(obj.get("NameSpace"))
        Identifier = from_str(obj.get("Identifier"))
        DisplayName = from_str(obj.get("DisplayName"))
        InitialValue = from_str(obj.get("InitialValue"))

        return MeasurementTags(NameSpace, Identifier, DisplayName, InitialValue)

    def to_dict(self) -> dict:
        result: dict = {}
        result["NameSpace"] = from_str(self.NameSpace)
        result["Identifier"] = from_str(self.Identifier)
        result["DisplayName"] = from_str(self.DisplayName)
        result["InitialValue"] = from_str(self.InitialValue)

        return result
