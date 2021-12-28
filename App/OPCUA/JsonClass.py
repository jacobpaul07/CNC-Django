# To use this code, make sure you
#
#     import json
#
# and then, to convert JSON from a string, do
#
#     result = live_data_from_dict(json.loads(json_string))

from dataclasses import dataclass
from typing import List, Optional, Any, TypeVar, Callable, Type, cast, Union
from datetime import datetime
import dateutil.parser


T = TypeVar("T")


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_bool(x: Any) -> bool:
    assert isinstance(x, bool)
    return x


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def from_float(x: Any) -> float:
    assert isinstance(x, (float, int)) and not isinstance(x, bool)
    return float(x)


def from_str1(x: Any) -> str:
    assert isinstance(x, (str, str)) and not isinstance(x, bool)
    return str(x)


def from_none(x: Any) -> Any:
    assert x is None
    return x


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except:
            pass
    assert False


def to_float(x: Any) -> float:
    assert isinstance(x, float)
    return x


def to_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


def from_datetime(x: Any) -> datetime:
    return dateutil.parser.parse(x)


@dataclass
class MachineStatusInfo:
    name: str
    color: str
    statusType: str

    @staticmethod
    def from_dict(obj: Any) -> 'MachineStatusInfo':
        assert isinstance(obj, dict)
        name = from_str(obj.get("name"))
        color = from_str(obj.get("color"))
        statusType = from_str(obj.get("statusType"))
        return MachineStatusInfo(name, color, statusType)

    def to_dict(self) -> dict:
        result: dict = {"name": from_str(self.name),
                        "color": from_str(self.color),
                        "statusType": from_str(self.statusType)}
        return result


@dataclass
class CurrentProductionGraphDatum:
    name: str
    color: str
    show_axis: bool
    left_side: bool
    data: List[List[Union[datetime, float]]]
    type: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'CurrentProductionGraphDatum':
        assert isinstance(obj, dict)
        name = from_str(obj.get("name"))
        color = from_str(obj.get("color"))
        show_axis = from_bool(obj.get("showAxis"))
        left_side = from_bool(obj.get("leftSide"))
        data = from_list(lambda x: from_list(lambda x: from_union([from_float, from_datetime], x), x), obj.get("data"))
        type = from_union([from_none, from_str], obj.get("type"))
        return CurrentProductionGraphDatum(name, color, show_axis, left_side, data, type)

    def to_dict(self) -> dict:
        result: dict = {}
        result["name"] = from_str(self.name)
        result["color"] = from_str(self.color)
        result["showAxis"] = from_bool(self.show_axis)
        result["leftSide"] = from_bool(self.left_side)
        result["data"] = from_list(lambda x: from_list(lambda x: from_union([from_float, lambda x: x.isoformat()], x), x), self.data)
        result["type"] = from_union([from_none, from_str], self.type)
        return result


@dataclass
class Graph:
    data: List[CurrentProductionGraphDatum]

    @staticmethod
    def from_dict(obj: Any) -> 'Graph':
        assert isinstance(obj, dict)
        data = from_list(CurrentProductionGraphDatum.from_dict, obj.get("data"))
        return Graph(data)

    def to_dict(self) -> dict:
        result: dict = {}
        result["data"] = from_list(lambda x: to_class(CurrentProductionGraphDatum, x), self.data)
        return result


@dataclass
class DowntimeDatum:
    name: str
    value: str
    color: str
    description: str

    @staticmethod
    def from_dict(obj: Any) -> 'DowntimeDatum':
        assert isinstance(obj, dict)
        name = from_str(obj.get("name"))
        value = from_str(obj.get("value"))
        color = from_str(obj.get("color"))
        description = from_str(obj.get("description"))
        return DowntimeDatum(name, value, color, description)

    def to_dict(self) -> dict:
        result: dict = {"name": from_str(self.name),
                        "value": float(from_str(self.value)),
                        "color": from_str(self.color),
                        "description": from_str(self.description)}
        return result


@dataclass
class Downtime:
    active_hours: str
    data: List[DowntimeDatum]

    @staticmethod
    def from_dict(obj: Any) -> 'Downtime':
        assert isinstance(obj, dict)
        active_hours = from_str(obj.get("activeHours"))
        data = from_list(DowntimeDatum.from_dict, obj.get("data"))
        return Downtime(active_hours, data)

    def to_dict(self) -> dict:
        result: dict = {}
        result["activeHours"] = from_str(self.active_hours)
        result["data"] = from_list(lambda x: to_class(DowntimeDatum, x), self.data)
        return result


@dataclass
class DowntimeGraphDatum:
    x: str
    y: List[datetime]
    description: str

    @staticmethod
    def from_dict(obj: Any) -> 'DowntimeGraphDatum':
        assert isinstance(obj, dict)
        x = from_str(obj.get("x"))
        y = from_list(from_datetime, obj.get("y"))
        description = from_str(obj.get("description"))
        return DowntimeGraphDatum(x, y, description)

    def to_dict(self) -> dict:
        result: dict = {}
        result["x"] = from_str(self.x)
        result["y"] = from_list(lambda x: x.isoformat(), self.y)
        result["description"] = from_str(self.description)
        return result


@dataclass
class DowntimeGraph:
    name: str
    color: str
    statusType: str
    data: List[DowntimeGraphDatum]

    @staticmethod
    def from_dict(obj: Any) -> 'DowntimeGraph':
        assert isinstance(obj, dict)
        name = from_str(obj.get("name"))
        color = from_str(obj.get("color"))
        statusType = from_str(obj.get("statusType"))
        data = from_list(DowntimeGraphDatum.from_dict, obj.get("data"))
        return DowntimeGraph(name, color, statusType, data)

    def to_dict(self) -> dict:
        result: dict = {}
        result["name"] = from_str(self.name)
        result["color"] = from_str(self.color)
        result["statusType"] = from_str(self.statusType)
        result["data"] = from_list(lambda x: to_class(DowntimeGraphDatum, x), self.data)
        return result


@dataclass
class Fullfiled:
    current_run_time: str
    total_produced: str
    good: str
    bad: str

    @staticmethod
    def from_dict(obj: Any) -> 'Fullfiled':
        assert isinstance(obj, dict)
        current_run_time = from_str(obj.get("currentRunTime"))
        total_produced = from_str(obj.get("totalProduced"))
        good = from_str(obj.get("good"))
        bad = from_str(obj.get("bad"))
        return Fullfiled(current_run_time, total_produced, good, bad)

    def to_dict(self) -> dict:
        result: dict = {}
        result["currentRunTime"] = from_str(self.current_run_time)
        result["totalProduced"] = from_str(self.total_produced)
        result["good"] = from_str(self.good)
        result["bad"] = from_str(self.bad)
        return result


@dataclass
class Scheduled:
    run_time: str
    expected_count: str
    production_rate: str

    @staticmethod
    def from_dict(obj: Any) -> 'Scheduled':
        assert isinstance(obj, dict)
        run_time = from_str(obj.get("runTime"))
        expected_count = from_str(obj.get("expectedCount"))
        production_rate = from_str(obj.get("productionRate"))
        return Scheduled(run_time, expected_count, production_rate)

    def to_dict(self) -> dict:
        result: dict = {}
        result["runTime"] = from_str(self.run_time)
        result["expectedCount"] = from_str(self.expected_count)
        result["productionRate"] = from_str(self.production_rate)
        return result


@dataclass
class Oee:
    scheduled: Scheduled
    fullfiled: Fullfiled
    availability: str
    performance: str
    quality: str
    target_oee: str
    oee: str

    @staticmethod
    def from_dict(obj: Any) -> 'Oee':
        assert isinstance(obj, dict)
        scheduled = Scheduled.from_dict(obj.get("scheduled"))
        fullfiled = Fullfiled.from_dict(obj.get("fullfiled"))
        availability = from_str(obj.get("availability"))
        performance = from_str(obj.get("performance"))
        quality = from_str(obj.get("quality"))
        target_oee = from_str(obj.get("targetOee"))
        oee = from_str(obj.get("oee"))
        return Oee(scheduled, fullfiled, availability, performance, quality, target_oee, oee)

    def to_dict(self) -> dict:
        result: dict = {}
        result["scheduled"] = to_class(Scheduled, self.scheduled)
        result["fullfiled"] = to_class(Fullfiled, self.fullfiled)
        result["availability"] = from_str(self.availability)
        result["performance"] = from_str(self.performance)
        result["quality"] = from_str(self.quality)
        result["targetOee"] = from_str(self.target_oee)
        result["oee"] = from_str(self.oee)
        return result


@dataclass
class TotalProduced:
    total: str
    expected: str
    data: List[DowntimeDatum]

    @staticmethod
    def from_dict(obj: Any) -> 'TotalProduced':
        assert isinstance(obj, dict)
        total = from_str(obj.get("total"))
        expected = from_str(obj.get("expected"))
        data = from_list(DowntimeDatum.from_dict, obj.get("data"))
        return TotalProduced(total, expected, data)

    def to_dict(self) -> dict:
        result: dict = {}
        result["total"] = from_str(self.total)
        result["expected"] = from_str(self.expected)
        result["data"] = from_list(lambda x: to_class(DowntimeDatum, x), self.data)
        return result


@dataclass
class LiveData:
    machine_id: str
    job_id: str
    operator_id: str
    shift_id: str
    powerOnStatus: str
    machineStatus: MachineStatusInfo
    running: Downtime
    downtime: Downtime
    total_produced: TotalProduced
    oee: Oee
    current_production_graph: Graph
    oee_graph: Graph
    downtime_graph: List[DowntimeGraph]

    @staticmethod
    def from_dict(obj: Any) -> 'LiveData':
        assert isinstance(obj, dict)
        machine_id = from_str(obj.get("machineID"))
        job_id = from_str(obj.get("jobID"))
        operator_id = from_str(obj.get("operatorID"))
        shift_id = from_str(obj.get("shiftID"))
        powerOnStatus = from_str(obj.get("powerOnStatus"))
        machineStatus = from_str(obj.get("machineStatus"))
        running = Downtime.from_dict(obj.get("running"))
        downtime = Downtime.from_dict(obj.get("downtime"))
        total_produced = TotalProduced.from_dict(obj.get("totalProduced"))
        oee = Oee.from_dict(obj.get("oee"))
        current_production_graph = Graph.from_dict(obj.get("currentProductionGraph"))
        oee_graph = Graph.from_dict(obj.get("oeeGraph"))
        downtime_graph = from_list(DowntimeGraph.from_dict, obj.get("downtimeGraph"))
        return LiveData(machine_id, job_id, operator_id, shift_id, powerOnStatus, machineStatus, running, downtime, total_produced, oee,
                        current_production_graph, oee_graph, downtime_graph)

    def to_dict(self) -> dict:
        result: dict = {"machineID": from_str(self.machine_id),
                        "jobID": from_str(self.job_id),
                        "operatorID": from_str(self.operator_id),
                        "shiftID": from_str(self.shift_id),
                        "powerOnStatus": from_str(self.powerOnStatus),
                        "machineStatus": to_class(MachineStatusInfo, self.machineStatus),
                        "running": to_class(Downtime, self.running),
                        "downtime": to_class(Downtime, self.downtime),
                        "totalProduced": to_class(TotalProduced, self.total_produced),
                        "oee": to_class(Oee, self.oee),
                        "currentProductionGraph": to_class(Graph, self.current_production_graph),
                        "oeeGraph": to_class(Graph, self.oee_graph),
                        "downtimeGraph": from_list(lambda x: to_class(DowntimeGraph, x), self.downtime_graph)}
        return result


def from_dict(s: Any) -> LiveData:
    return LiveData.from_dict(s)


def to_dict(x: LiveData) -> Any:
    return to_class(LiveData, x)


def LiveData_fromDict(s: Any) -> LiveData:
    return LiveData.from_dict(s)

