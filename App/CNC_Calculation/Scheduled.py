from typing import Optional, List
from dataclasses import dataclass
from App.Json_Class.DtoUtilities import *


@dataclass
class Scheduled:
    run_time: str
    expected_count: str
    production_rate: str

    @staticmethod
    def from_dict(obj: Any) -> 'Scheduled':
        assert isinstance(obj, dict)
        run_time = from_str(obj.get("runTime"))
        expected_count = from_str(obj.get("expectedCount"))
        production_rate = from_str(obj.get("productionRate"))

        return Scheduled(run_time, expected_count, production_rate)

    def to_dict(self) -> dict:
        result: dict = {
            "runTime": from_str(self.run_time),
            "expectedCount": from_str(self.expected_count),
            "productionRate": from_str(self.production_rate),
        }
        return result
