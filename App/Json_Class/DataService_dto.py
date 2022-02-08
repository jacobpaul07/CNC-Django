from dataclasses import dataclass
from App.Json_Class.DtoUtilities import *
from App.Json_Class.MQTT_dto import mqtts
from App.Json_Class.OPCUA_dto import opcua
from App.Json_Class.MTConnect_dto import MtConnect


@dataclass
class DataServices:
    MQTT: mqtts
    OPCUA: opcua
    MTConnect: MtConnect

    @staticmethod
    def from_dict(obj: Any) -> 'DataServices':
        assert isinstance(obj, dict)
        MQTT = mqtts.from_dict(obj.get("MQTT"))
        OPCUA = opcua.from_dict(obj.get("OPCUA"))
        MTConnect = MtConnect.from_dict(obj.get("MTConnect"))
        return DataServices(MQTT, OPCUA, MTConnect)

    def to_dict(self) -> dict:
        result: dict = {
            "MQTT": to_class(mqtts, self.MQTT),
            "OPCUA": to_class(opcua, self.OPCUA),
            "MTConnect": to_class(MtConnect, self.MTConnect)}
        return result
