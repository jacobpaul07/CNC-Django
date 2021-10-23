from typing import Optional, List

from App.CNC_Calculation.CurrentProductionGraphDatum import CurrentProductionGraphDatum
from App.Json_Class.DtoUtilities import *
from dataclasses import dataclass


@dataclass
class Graph:
    data: List[CurrentProductionGraphDatum]
    categories: List[int]

    @staticmethod
    def from_dict(obj: Any) -> 'Graph':
        assert isinstance(obj, dict)
        data = from_list(CurrentProductionGraphDatum.from_dict, obj.get("data"))
        categories = from_list(int, obj.get("categories"))

        return Graph(data, categories)

    def to_dict(self) -> dict:
        result: dict = {
            "data": from_list(lambda x: to_class(CurrentProductionGraphDatum, x), self.data),
            "categories": from_list(lambda x: to_class(int, x), self.categories),
        }
        return result
