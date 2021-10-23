from typing import Optional, List
from App.Json_Class.DtoUtilities import *
from dataclasses import dataclass


@dataclass
class DowntimeGraphDatum:
    x: str
    y: List[int]

    @staticmethod
    def from_dict(obj: Any) -> 'DowntimeGraphDatum':
        assert isinstance(obj, dict)
        x = from_str(obj.get("x"))
        y = from_list(int, obj.get("y"))

        return DowntimeGraphDatum(x, y)

    def to_dict(self) -> dict:
        result: dict = {
            "x": from_str(self.x),
            "y": from_list(lambda x: to_class(int, x), self.y),
        }
        return result
