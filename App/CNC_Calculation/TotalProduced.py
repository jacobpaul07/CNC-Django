from App.CNC_Calculation.DowntimeDatum import DowntimeDatum
from App.Json_Class.DtoUtilities import *
from dataclasses import dataclass


@dataclass
class TotalProduced:
    total: str
    data: List[DowntimeDatum]

    @staticmethod
    def from_dict(obj: Any) -> 'TotalProduced':
        assert isinstance(obj, dict)
        total = from_str(obj.get("total"))
        data = from_list(DowntimeDatum.from_dict, obj.get("data"))

        return TotalProduced(total, data)

    def to_dict(self) -> dict:
        result: dict = {
            "total": from_str(self.total),
            "data": from_list(lambda x: to_class(DowntimeDatum, x), self.data),
        }
        return result
