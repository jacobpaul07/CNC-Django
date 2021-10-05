from dataclasses import dataclass
from typing import List, Any, Optional
from App.Json_Class.EdgeDeviceProperties_dto import EdgeDeviceProperties
from App.Json_Class.DtoUtilities import *
from App.Json_Class.DataService_dto import DataServices
from App.Json_Class.Services_dto import Services

@dataclass
class EdgeDevice:
    properties: EdgeDeviceProperties
    DataService: DataServices
    Service: Services

    @staticmethod
    def from_dict(obj: Any) -> 'EdgeDevice':
        assert isinstance(obj, dict)
        properties = EdgeDeviceProperties.from_dict(obj.get("properties"))
        DataService = DataServices.from_dict(obj.get("DataService"))
        Service = Services.from_dict(obj.get("Services"))

        return EdgeDevice(properties, DataService, Service)

    def to_dict(self) -> dict:
        result: dict = {"properties": to_class(EdgeDeviceProperties, self.properties),
                        "DataService": to_class(DataServices, self.DataService),
                        "Services": to_class(Services, self.Service)}
        return result
