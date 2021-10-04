from dataclasses import dataclass
from App.Json_Class.DtoUtilities import *
from App.Json_Class.OPCUAProperties import OPCProperties
from App.Json_Class.OPCUAParameters import OPCParameters


@dataclass
class opcua:
    Properties: OPCProperties
    Parameters: OPCParameters

    @staticmethod
    def from_dict(obj: Any) -> 'opcua':
        assert isinstance(obj, dict)
        Properties = OPCProperties.from_dict(obj.get("Properties"))
        Parameters = OPCParameters.from_dict(obj.get("Parameters"))
        return opcua(Properties,Parameters)

    def to_dict(self) -> dict:
        result: dict = {"Properties": to_class(OPCProperties, self.Properties),
                        "Parameters": to_class(OPCParameters, self.Parameters)}
        return result
