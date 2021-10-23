from App.Json_Class.DtoUtilities import *
from App.CNC_Calculation.DowntimeDatum import DowntimeDatum
from dataclasses import dataclass


@dataclass
class Downtime:
    active_hours: str
    data: List[DowntimeDatum]

    @staticmethod
    def from_dict(obj: Any) -> 'Downtime':
        assert isinstance(obj, dict)
        active_hours = from_str(obj.get("activeHours"))
        data = from_list(DowntimeDatum.from_dict, obj.get("data"))

        return Downtime(active_hours, data)

    def to_dict(self) -> dict:
        result: dict = {
            "activeHours": from_str(self.active_hours),
            "data": from_list(lambda x: to_class(DowntimeDatum, x), self.data),
        }
        return result
