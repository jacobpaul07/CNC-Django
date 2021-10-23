from dataclasses import dataclass
from App.Json_Class.DtoUtilities import *
from App.CNC_Calculation.Downtime import Downtime
from App.CNC_Calculation.DowntimeGraph import DowntimeGraph
from App.CNC_Calculation.Graph import Graph
from App.CNC_Calculation.Oee import Oee
from App.CNC_Calculation.TotalProduced import TotalProduced


@dataclass
class LiveData:
    machine_id: str
    job_id: str
    operator_id: str
    shift_id: str
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
        running = Downtime.from_dict(obj.get("running"))
        downtime = Downtime.from_dict(obj.get("downtime"))
        total_produced = TotalProduced.from_dict(obj.get("totalProduced"))
        oee = Oee.from_dict(obj.get("oee"))
        current_production_graph = Graph.from_dict(obj.get("currentProductionGraph"))
        oee_graph = Graph.from_dict(obj.get("oeeGraph"))
        downtime_graph = from_list(DowntimeGraph.from_dict, obj.get("downtimeGraph"))

        return LiveData(machine_id, job_id, operator_id, shift_id, running, downtime, total_produced, oee,
                        current_production_graph, oee_graph, downtime_graph)

    def to_dict(self) -> dict:
        result: dict = {
            "machine_id": from_str(self.machine_id),
            "job_id": from_str(self.job_id),
            "operator_id": from_str(self.operator_id),
            "shift_id": from_str(self.shift_id),
            "running": to_class(Downtime, self.running),
            "downtime": to_class(Downtime, self.downtime),
            "total_produced": to_class(TotalProduced, self.total_produced),
            "oee": to_class(Oee, self.oee),
            "current_production_graph": to_class(Graph, self.current_production_graph),
            "oee_graph": to_class(Graph, self.oee_graph),
            "downtime_graph": from_list(lambda x: to_class(DowntimeGraph, x), self.downtime_graph),
        }
        return result
