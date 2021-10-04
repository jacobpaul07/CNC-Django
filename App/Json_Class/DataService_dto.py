from dataclasses import dataclass
from App.Json_Class.DtoUtilities import *
from App.Json_Class.MQTTs_dto import mqtts
from App.Json_Class.OPCUA_dto import opcua


@dataclass
class DataServices:
    MQTT: mqtts
    OPCUA: opcua

    @staticmethod
    def from_dict(obj: Any) -> 'DataServices':
        assert isinstance(obj, dict)
        MQTT = mqtts.from_dict(obj.get("MQTT"))
        OPCUA = opcua.from_dict(obj.get("OPCUA"))
        return DataServices(MQTT, OPCUA)

    def to_dict(self) -> dict:
        result: dict = {"MQTT": to_class(mqtts, self.MQTT),"OPCUA": to_class(opcua, self.OPCUA)}
        return result
