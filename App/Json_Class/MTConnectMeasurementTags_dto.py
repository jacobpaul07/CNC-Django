from dataclasses import dataclass
from App.Json_Class.DtoUtilities import *


@dataclass
class MTConnectMeasurementTags:
    param_name: str
    parent_path: str
    return_value_mode: str
    attribute_name: str

    @staticmethod
    def from_dict(obj: Any) -> 'MTConnectMeasurementTags':
        assert isinstance(obj, dict)
        param_name = from_str(obj.get("paramName"))
        parent_path = from_str(obj.get("parentPath"))
        return_value_mode = from_str(obj.get("returnvalueMode"))
        attribute_name = from_str(obj.get("attribName"))

        return MTConnectMeasurementTags(param_name, parent_path, return_value_mode, attribute_name)

    def to_dict(self) -> dict:
        result: dict = {"paramName": from_str(self.param_name),
                        "parentPath": from_str(self.parent_path),
                        "returnvalueMode": from_str(self.return_value_mode),
                        "attribName": from_str(self.attribute_name)}

        return result
