from dataclasses import dataclass
from App.Json_Class.DtoUtilities import *
from App.Json_Class.OPCMeasurementTags_dto import MeasurementTags


@dataclass
class OPCParameters:
    MeasurementTag: List[MeasurementTags]

    @staticmethod
    def from_dict(obj: Any) -> 'OPCParameters':
        assert isinstance(obj, dict)
        MeasurementTag = from_list(MeasurementTags.from_dict, obj.get("MeasurementTag"))

        return OPCParameters(MeasurementTag)

    def to_dict(self) -> dict:
        result: dict = {
            "MeasurementTag": from_list(lambda x: to_class(MeasurementTags, x), self.MeasurementTag)
        }
        return result
