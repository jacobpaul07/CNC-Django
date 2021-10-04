from App.Json_Class.DtoUtilities import *
from App.Json_Class.EdgeDevice_dto import EdgeDevice
from dataclasses import dataclass
from typing import Any, List, Optional, TypeVar, Type, cast, Callable

@dataclass
class Edge:
    edgedevice: EdgeDevice

    @staticmethod
    def from_dict(obj: Any) -> 'Edge':
        assert isinstance(obj, dict)
        edgedevice = EdgeDevice.from_dict(obj.get("edge device"))
        return Edge(edgedevice)

    def to_dict(self) -> dict:
        result: dict = {}
        result["edge device"] = to_class(EdgeDevice, self.edgedevice)
        return result


def Edgefromdict(s: Any) -> Edge:
    return Edge.from_dict(s)