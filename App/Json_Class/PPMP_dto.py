from dataclasses import dataclass
from typing import Any, Optional, List, TypeVar, Callable, Type, cast
from App.Json_Class.PPMPProperties_dto import PPMPPropertiess
from App.Json_Class.DtoUtilities import *
from App.Json_Class.Stations_dto import Stations


@dataclass
class Ppmps:
    Properties: PPMPPropertiess
    Station: List[Stations]

    @staticmethod
    def from_dict(obj: Any) -> 'Ppmps':
        assert isinstance(obj, dict)
        PPMPProperties = PPMPPropertiess.from_dict(obj.get("Properties"))
        Station = from_list(Stations.from_dict, obj.get("Station"))
        return Ppmps(PPMPProperties, Station)

    def to_dict(self) -> dict:
        result: dict = {"Properties": to_class(PPMPPropertiess, self.Properties),
                        "Station": from_list(lambda x: to_class(Stations, x), self.Station)}
        return result

