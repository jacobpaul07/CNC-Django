from typing import Optional, List


class CurrentProductionGraphDatum:
    name: str
    color: str
    type: Optional[str]
    show_axis: bool
    left_side: bool
    data: List[float]

    def __init__(self, name: str, color: str, type: Optional[str], show_axis: bool, left_side: bool, data: List[float]) -> None:
        self.name = name
        self.color = color
        self.type = type
        self.show_axis = show_axis
        self.left_side = left_side
        self.data = data


class Graph:
    data: List[CurrentProductionGraphDatum]
    categories: List[int]

    def __init__(self, data: List[CurrentProductionGraphDatum], categories: List[int]) -> None:
        self.data = data
        self.categories = categories


class DowntimeDatum:
    name: str
    value: str
    color: str
    description: str

    def __init__(self, name: str, value: str, color: str, description: str) -> None:
        self.name = name
        self.value = value
        self.color = color
        self.description = description


class Downtime:
    active_hours: str
    data: List[DowntimeDatum]

    def __init__(self, active_hours: str, data: List[DowntimeDatum]) -> None:
        self.active_hours = active_hours
        self.data = data


class DowntimeGraphDatum:
    x: str
    y: List[float]
    description: str

    def __init__(self, x: str, y: List[float], description: str) -> None:
        self.x = x
        self.y = y
        self.description = description


class DowntimeGraph:
    name: str
    color: str
    data: List[DowntimeGraphDatum]

    def __init__(self, name: str, color: str, data: List[DowntimeGraphDatum]) -> None:
        self.name = name
        self.color = color
        self.data = data


class Fullfiled:
    current_run_time: str
    total_produced: str
    good: str
    bad: str

    def __init__(self, current_run_time: str, total_produced: str, good: str, bad: str) -> None:
        self.current_run_time = current_run_time
        self.total_produced = total_produced
        self.good = good
        self.bad = bad


class Scheduled:
    run_time: str
    expected_count: str
    production_rate: str

    def __init__(self, run_time: str, expected_count: str, production_rate: str) -> None:
        self.run_time = run_time
        self.expected_count = expected_count
        self.production_rate = production_rate


class Oee:
    scheduled: Scheduled
    fullfiled: Fullfiled
    availability: str
    performance: str
    quality: str
    target_oee: str
    oee: str

    def __init__(self, scheduled: Scheduled, fullfiled: Fullfiled, availability: str, performance: str, quality: str, target_oee: str, oee: str) -> None:
        self.scheduled = scheduled
        self.fullfiled = fullfiled
        self.availability = availability
        self.performance = performance
        self.quality = quality
        self.target_oee = target_oee
        self.oee = oee


class TotalProduced:
    total: str
    data: List[DowntimeDatum]

    def __init__(self, total: str, data: List[DowntimeDatum]) -> None:
        self.total = total
        self.data = data


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

    def __init__(self, machine_id: str, job_id: str, operator_id: str, shift_id: str, running: Downtime, downtime: Downtime, total_produced: TotalProduced, oee: Oee, current_production_graph: Graph, oee_graph: Graph, downtime_graph: List[DowntimeGraph]) -> None:
        self.machine_id = machine_id
        self.job_id = job_id
        self.operator_id = operator_id
        self.shift_id = shift_id
        self.running = running
        self.downtime = downtime
        self.total_produced = total_produced
        self.oee = oee
        self.current_production_graph = current_production_graph
        self.oee_graph = oee_graph
        self.downtime_graph = downtime_graph
