from dataclasses import dataclass
from App.Json_Class.DtoUtilities import *


@dataclass
class CurrentProductionGraphDatum:
    name: str
    color: str
    types: str
    show_axis: bool
    left_side: bool
    data: List[float]

    @staticmethod
    def from_dict(obj: Any) -> 'CurrentProductionGraphDatum':
        assert isinstance(obj, dict)
        name = from_str(obj.get("name"))
        color = from_str(obj.get("color"))
        types = from_str(obj.get("type"))
        show_axis = from_bool(obj.get("showAxis"))
        left_side = from_bool(obj.get("leftSide"))
        data = from_list(float, obj.get("data"))

        return CurrentProductionGraphDatum(name,color,types,show_axis,left_side,data,)

    def to_dict(self) -> dict:
        result: dict = {
            "name": from_str(self.name),
            "color": from_str(self.color),
            "type": from_str(self.types),
            "showAxis": from_bool(self.show_axis),
            "leftSide": from_bool(self.left_side),
            "data": from_list(lambda x: to_class(float, x), self.data)
        }
        return result

