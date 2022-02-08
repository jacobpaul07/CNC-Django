from dataclasses import dataclass
from App.Json_Class.DtoUtilities import *
from App.Json_Class.MTConnectParameters import MtConnectParameters
from App.Json_Class.OPCUAProperties import OPCProperties


@dataclass
class MtConnect:
    Properties: OPCProperties
    Parameters: MtConnectParameters

    @staticmethod
    def from_dict(obj: Any) -> 'MtConnect':
        assert isinstance(obj, dict)
        Properties = OPCProperties.from_dict(obj.get("Properties"))
        Parameters = MtConnectParameters.from_dict(obj.get("Parameters"))
        return MtConnect(Properties, Parameters)

    def to_dict(self) -> dict:
        result: dict = {"Properties": to_class(OPCProperties, self.Properties),
                        "Parameters": to_class(MtConnectParameters, self.Parameters)
                        }
        return result
