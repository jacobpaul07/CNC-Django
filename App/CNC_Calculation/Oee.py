from dataclasses import dataclass
from typing import Optional, List
from App.CNC_Calculation.Fullfiled import Fullfiled
from App.CNC_Calculation.Scheduled import Scheduled
from App.Json_Class.DtoUtilities import *


@dataclass
class Oee:
    scheduled: Scheduled
    fullfiled: Fullfiled
    availability: str
    performance: str
    quality: str
    target_oee: str
    oee: str

    @staticmethod
    def from_dict(obj: Any) -> 'Oee':
        assert isinstance(obj, dict)
        scheduled = Scheduled.from_dict(obj.get("scheduled"))
        fullfiled = Fullfiled.from_dict(obj.get("fullfiled"))
        availability = from_str(obj.get("availability"))
        performance = from_str(obj.get("performance"))
        quality = from_str(obj.get("quality"))
        target_oee = from_str(obj.get("target_oee"))
        oee = from_str(obj.get("oee"))

        return Oee(scheduled, fullfiled, availability, performance, quality, target_oee, oee)

    def to_dict(self) -> dict:
        result: dict = {
            "scheduled": to_class(Scheduled, self.scheduled),
            "fullfiled": to_class(Fullfiled, self.fullfiled),
            "availability": from_str(self.availability),
            "performance": from_str(self.performance),
            "quality": from_str(self.quality),
            "target_oee": from_str(self.target_oee),
            "oee": from_str(self.oee),

        }
        return result
