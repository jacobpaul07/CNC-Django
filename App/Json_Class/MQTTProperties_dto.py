from dataclasses import dataclass
from App.Json_Class.DtoUtilities import *
from App.Json_Class.OPCMeasurementTags_dto import MeasurementTags


@dataclass
class MqttProperties:
    Enable: str
    subscriptionTopic: str
    serverIpAddress: str
    serverPort: str

    
    @staticmethod
    def from_dict(obj: Any) -> 'MqttProperties':
        assert isinstance(obj, dict)
        Enable = from_str(obj.get("Enable"))
        subscriptionTopic = from_str(obj.get("subscriptionTopic"))
        serverIpAddress = from_str(obj.get("serverIpAddress"))
        serverPort = from_str(obj.get("serverPort"))
        return MqttProperties(Enable, subscriptionTopic, serverIpAddress, serverPort)

    def to_dict(self) -> dict:
        result: dict = {"Enable": from_str(self.Enable),
                        "subscriptionTopic": from_str(self.subscriptionTopic),
                        "serverIpAddress": from_str(self.serverIpAddress),
                        "serverPort": from_str(self.serverPort),

                        }
        return result
