from dataclasses import dataclass
from App.Json_Class.DtoUtilities import *
from App.Json_Class.MQTTProperties_dto import MqttProperties
from App.Json_Class.OPCUAProperties import OPCProperties
from App.Json_Class.OPCUAParameters import OPCParameters


@dataclass
class mqtts:
    Properties: MqttProperties

    @staticmethod
    def from_dict(obj: Any) -> 'mqtts':
        assert isinstance(obj, dict)
        Properties = MqttProperties.from_dict(obj.get("Properties"))
        return mqtts(Properties)

    def to_dict(self) -> dict:
        result: dict = {"Properties": to_class(MqttProperties, self.Properties)}
        return result
