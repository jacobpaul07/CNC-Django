from dataclasses import dataclass
from App.Json_Class.DtoUtilities import *
from App.Json_Class.MTConnectMeasurementTags_dto import MTConnectMeasurementTags


@dataclass
class MtConnectParameters:
    MeasurementTag: List[MTConnectMeasurementTags]

    @staticmethod
    def from_dict(obj: Any) -> 'MtConnectParameters':
        assert isinstance(obj, dict)
        MeasurementTag = from_list(MTConnectMeasurementTags.from_dict, obj.get("MeasurementTag"))

        return MtConnectParameters(MeasurementTag)

    def to_dict(self) -> dict:
        result: dict = {
            "MeasurementTag": from_list(lambda x: to_class(MTConnectMeasurementTags, x), self.MeasurementTag)
        }
        return result
