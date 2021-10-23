from typing import Optional, List

from App.CNC_Calculation.DowntimeGraphDatum import DowntimeGraphDatum
from App.Json_Class.DtoUtilities import *
from dataclasses import dataclass

@dataclass
class DowntimeGraph:
    name: str
    color: str
    data: List[DowntimeGraphDatum]

    @staticmethod
    def from_dict(obj: Any) -> 'DowntimeGraph':
        assert isinstance(obj, dict)
        name = from_str(obj.get("name"))
        color = from_str(obj.get("color"))
        data = from_list(DowntimeGraphDatum.from_dict, obj.get("data"))

        return DowntimeGraph(name,color, data)

    def to_dict(self) -> dict:
        result: dict = {
            "name": from_str(self.name),
            "color": from_str(self.color),
            "data": from_list(lambda x: to_class(DowntimeGraphDatum, x), self.data),
        }
        return result
