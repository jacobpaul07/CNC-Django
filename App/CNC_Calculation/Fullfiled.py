from typing import Optional, List
from dataclasses import dataclass
from App.Json_Class.DtoUtilities import *


@dataclass
class Fullfiled:
    current_run_time: str
    total_produced: str
    good: str
    bad: str

    @staticmethod
    def from_dict(obj: Any) -> 'Fullfiled':
        assert isinstance(obj, dict)
        current_run_time = from_str(obj.get("currentRunTime"))
        total_produced = from_str(obj.get("totalProduced"))
        good = from_str(obj.get("good"))
        bad = from_str(obj.get("bad"))

        return Fullfiled(current_run_time, total_produced, good, bad)

    def to_dict(self) -> dict:
        result: dict = {
            "currentRunTime": from_str(self.current_run_time),
            "expectedCount": from_str(self.total_produced),
            "good": from_str(self.good),
            "bad": from_str(self.bad),
        }
        return result
