from typing import Optional, List
from dataclasses import dataclass
from App.Json_Class.DtoUtilities import *


@dataclass
class DowntimeDatum:
    name: str
    value: str
    color: str

    @staticmethod
    def from_dict(obj: Any) -> 'DowntimeDatum':
        assert isinstance(obj, dict)
        name = from_str(obj.get("name"))
        value = from_str(obj.get("value"))
        color = from_str(obj.get("color"))

        return DowntimeDatum(name, value, color)

    def to_dict(self) -> dict:
        result: dict = {
            "name": from_str(self.name),
            "value": from_str(self.value),
            "color": from_str(self.color),
            }
        return result
