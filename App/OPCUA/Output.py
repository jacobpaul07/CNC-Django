import json
from App.OPCUA.JsonClass import *


def StandardOutput(result, availability, performance, quality, targetOee, OeePercentage, OutputArgs):
    # HEADERS = ["CycleStart_Status", "DownTime_ReasonCode", "DownTime_Status", "EmgStop_Status", "IdealCycleTime",
    #            "JobID", "MachineID", "OperatorID", "PowerOn_Status", "ProductionStart", "QualityCode", "ShiftID"]
    # # Result dictionary
    # result = {}
    # for index, header in enumerate(HEADERS):
    #     result[header] = Data[index]["value"]

    machine_id = result["MachineID"]
    job_id = result["JobID"]
    operator_id = result["OperatorID"]
    shift_id = result["ShiftID"]

    # Running
    runningValue: str = "70"
    runningDescription: str = "total 7 Hrs running"
    plannedValue: str = "20"
    plannedDescription: str = "total 2 Hrs planned down"
    unplannedValue: str = "10"
    unplannedDescription: str = "total 2 Hrs planned down"

    machineRunningData = [
        {"name": "running", "value": runningValue, "color": "#348f07", "description": runningDescription},
        {"name": "planned", "value": plannedValue, "color": "#1d0aa8", "description": plannedDescription},
        {"name": "unplanning", "value": unplannedValue, "color": "#e80505", "description": unplannedDescription}
    ]

    machineRunningDataDumped = json.dumps(machineRunningData)
    machineRunningDataLoaded = json.loads(machineRunningDataDumped)

    runningActiveHours = "3h"
    runningData: List[DowntimeDatum] = machineRunningDataLoaded
    running: Downtime = Downtime(active_hours=runningActiveHours, data=runningData).__dict__

    # DownTime
    machineDownData = [
        {"name": "Lunch", "value": 33, "color": "#7D30FA", "description": "total 30 mins Lunch"},
        {"name": "Tea Break", "value": 33, "color": "#F8425F", "description": "total 30 mins Tea break"},
        {"name": "Mechanical Breakdown", "value": 33, "color": "#F8B53A",
         "description": "Total 30 mins mechanical down time"}
    ]

    machineDowntimeDataDumped = json.dumps(machineDownData)
    machineDowntimeDataLoaded = json.loads(machineDowntimeDataDumped)

    downtimeActiveHours = "4h"
    downtimeData: List[DowntimeDatum] = machineDowntimeDataLoaded
    downtime: Downtime = Downtime(active_hours=downtimeActiveHours, data=downtimeData).__dict__

    # TotalProduced
    TotalProducedCount = OutputArgs["TotalProducedTotal"]
    GoodCount = OutputArgs["GoodCount"]
    BadCount = OutputArgs["BadCount"]

    GoodPercentage = round(GoodCount/TotalProducedCount*100, 3)
    BadPercentage = round(BadCount/TotalProducedCount*100, 3)
    machineProducedData = [
        {"name": "Good", "value": GoodPercentage, "color": "#7D30FA", "description": "7000 tons"},
        {"name": "Bad", "value": BadPercentage, "color": "#F8425F", "description": "3000 tons"}
    ]

    machineTotalProducedDataDumped = json.dumps(machineProducedData)
    machineTotalProducedDataLoaded = json.loads(machineTotalProducedDataDumped)
    totalProducedData: List[DowntimeDatum] = machineTotalProducedDataLoaded
    totalProduced: TotalProduced = TotalProduced(total=OutputArgs["TotalProducedTotal"], data=totalProducedData).__dict__

    # OEE
    oeeRunTime: str = "675.00 minutes"
    oeeExpectedCount: str = "675"
    oeeProductionRate: str = "1"
    oeeScheduled: Scheduled = Scheduled(run_time=oeeRunTime,
                                        expected_count=oeeExpectedCount,
                                        production_rate=oeeProductionRate).__dict__

    oee_current_run_time: str = "269 minutes"
    oee_total_produced: str = "4940.00 tons"
    oee_good: str = "4915.30"
    oee_bad: str = "24.70"
    oeeFullFiled: Fullfiled = Fullfiled(current_run_time=oee_current_run_time,
                                        total_produced=oee_total_produced,
                                        good=oee_good,
                                        bad=oee_bad).__dict__

    oeeAvailability: str = availability
    oeePerformance: str = performance
    oeeQuality: str = quality
    oeeTargetOee: str = targetOee
    oeePercentage: str = OeePercentage
    oee: Oee = Oee(
        scheduled=oeeScheduled,
        fullfiled=oeeFullFiled,
        availability=oeeAvailability,
        performance=oeePerformance,
        quality=oeeQuality,
        target_oee=oeeTargetOee,
        oee=oeePercentage).__dict__

    # Current Production Graph
    currentProductionGraphData = [
        {
            "name": "Quality Product",
            "color": "#00FF00",
            "type": 'line',
            "showAxis": True,
            "leftSide": True,
            "data": [50, 100, 150, 200, 250, 300, 350, 460]
        },
        {
            "name": "Waster Product",
            "color": "#0000FF",
            "type": 'line',
            "showAxis": False,
            "leftSide": False,
            "data": [10, 29, 37, 36, 44, 45, 50, 58]
        },
        {
            "name": "Bad Product",
            "color": "#FF0000",
            "type": 'line',
            "showAxis": True,
            "leftSide": False,
            "data": [50, 29, 37, 36, 44, 45, 50, 58]
        }
    ]

    currentProductionDataDumped = json.dumps(currentProductionGraphData)
    currentProductionDataLoaded = json.loads(currentProductionDataDumped)
    currentProductionData: List[CurrentProductionGraphDatum] = currentProductionDataLoaded
    currentProductionGraphCategories: List = [1, 2, 3, 4, 5, 6, 7, 8]

    current_production_graph: Graph = Graph(
        data=currentProductionData,
        categories=currentProductionGraphCategories
    ).__dict__

    # OEE Graph
    oee_graph_data = [
        {
            "name": "Availability",
            "color": "#87CEEB",
            "showAxis": True,
            "leftSide": True,
            "data": [1.4, 2, 2.5, 1.5, 2.5, 2.8, 3.8, 4.6]
        },
        {
            "name": "Performance",
            "color": "#FF0000",
            "showAxis": False,
            "leftSide": False,
            "data": [20, 29, 37, 36, 44, 45, 50, 58]
        },
        {
            "name": "Quality",
            "color": "#00FF00",
            "showAxis": False,
            "leftSide": False,
            "data": [20, 29, 37, 36, 44, 45, 50, 58]
        },
        {
            "name": "OEE %",
            "color": "#0000FF",
            "showAxis": True,
            "leftSide": False,
            "data": [20, 29, 37, 36, 44, 45, 50, 58]
        }
    ]

    oeeGraphDataDumped = json.dumps(oee_graph_data)
    oeeGraphDataLoaded = json.loads(oeeGraphDataDumped)
    oeeGraphData: List[CurrentProductionGraphDatum] = oeeGraphDataLoaded
    oeeGraphCategories: List = [1, 2, 3, 4, 5, 6, 7, 8]

    oee_graph: Graph = Graph(
        data=oeeGraphData,
        categories=oeeGraphCategories
    ).__dict__

    # Down Time Production

    # Down Time Production - Running

    DTObjectRunningName: str = "Running"
    DTObjectRunningColor: str = "#00FF00"
    DTRunningData = [
        {
            "x": 'down',
            "y": [6, 7],
            "description": "1hr Machine Running"
        },
        {
            "x": 'down',
            "y": [8, 10],
            "description": "2hr Machine Running"
        },
        {
            "x": 'down',
            "y": [12, 16],
            "description": "4hr Machine Running"
        },
    ]

    DTRunningDataDumped = json.dumps(DTRunningData)
    DTRunningDataLoaded = json.loads(DTRunningDataDumped)
    DTObjectRunningData: List[DowntimeGraphDatum] = DTRunningDataLoaded

    DTObjectRunning: DowntimeGraph = DowntimeGraph(name=DTObjectRunningName,
                                                   color=DTObjectRunningColor,
                                                   data=DTObjectRunningData).__dict__

    # Down Time Production - Planned
    DTObjectPlannedName: str = "Planned"
    DTObjectPlannedColor: str = "#FFFF00"
    DTPlannedData = [
        {
            "x": 'down',
            "y": [7, 7.10],
            "description": "10 mins Tea Break"
        },
        {
            "x": 'down',
            "y": [9, 9.30],
            "description": "30 mins Breakfast"
        },
    ]

    DTPlannedDataDumped = json.dumps(DTPlannedData)
    DTPlannedDataLoaded = json.loads(DTPlannedDataDumped)
    DTObjectPlannedData: List[DowntimeGraphDatum] = DTPlannedDataLoaded

    DTObjectPlanned: DowntimeGraph = DowntimeGraph(name=DTObjectPlannedName,
                                                   color=DTObjectPlannedColor,
                                                   data=DTObjectPlannedData).__dict__

    # Down Time Production - UnPlanned
    DTObjectUnPlannedName: str = "UnPlanned"
    DTObjectUnPlannedColor: str = "#FF0000"
    DTUnPlannedData = [
        {
            "x": 'down',
            "y": [12, 12.30],
            "description": "30 mins down for undefined reason"
        },
    ]

    DTUnPlannedDataDumped = json.dumps(DTUnPlannedData)
    DTUnPlannedDataLoaded = json.loads(DTUnPlannedDataDumped)
    DTObjectUnPlannedData: List[DowntimeGraphDatum] = DTUnPlannedDataLoaded

    DTObjectUnPlanned: DowntimeGraph = DowntimeGraph(name=DTObjectUnPlannedName,
                                                     color=DTObjectUnPlannedColor,
                                                     data=DTObjectPlannedData).__dict__

    downTimeProduction: List = [DTObjectRunning, DTObjectPlanned, DTObjectUnPlanned]
    downtimegraph: List[DowntimeGraph] = downTimeProduction
    # Final Output
    OutputLiveData: LiveData = LiveData(machine_id=machine_id,
                                        job_id=job_id,
                                        operator_id=operator_id,
                                        shift_id=shift_id,
                                        running=running,
                                        downtime=downtime,
                                        total_produced=totalProduced,
                                        oee=oee,
                                        current_production_graph=current_production_graph,
                                        oee_graph=oee_graph,
                                        downtime_graph=downtimegraph
                                        ).__dict__

    # Result = json.dumps(OutputLiveData)
    # print(Result)

    return OutputLiveData

#
# Data = {
#     "topic": "test",
#     "partition": 0,
#     "offset": 221,
#     "timestamp": {"$numberLong": "1634567314354"},
#     "timestamp_type": 0,
#     "key": "null",
#     "value": [
#         {"DisplayName": "CycleStart_Status", "value": "True", "timestamp": "2021-10-18T02:28:34_PM"},
#         {"DisplayName": "DownTime_ReasonCode", "value": 10, "timestamp": "2021-10-18T02:28:34_PM"},
#         {"DisplayName": "DownTime_Status", "value": "True", "timestamp": "2021-10-18T02:28:34_PM"},
#         {"DisplayName": "EmgStop_Status", "value": "True", "timestamp": "2021-10-18T02:28:34_PM"},
#         {"DisplayName": "IdealCycleTime", "value": 180, "timestamp": "2021-10-18T02:28:34_PM"},
#         {"DisplayName": "JobID", "value": 500, "timestamp": "2021-10-18T02:28:34_PM"},
#         {"DisplayName": "MachineID", "value": 1002, "timestamp": "2021-10-18T02:28:34_PM"},
#         {"DisplayName": "OperatorID", "value": 1001, "timestamp": "2021-10-18T02:28:34_PM"},
#         {"DisplayName": "PowerOn_Status", "value": "False", "timestamp": "2021-10-18T02:28:34_PM"},
#         {"DisplayName": "ProductionStart", "value": "False", "timestamp": "2021-10-18T02:28:34_PM"},
#         {"DisplayName": "QualityCode", "value": 1005, "timestamp": "2021-10-18T02:28:34_PM"},
#         {"DisplayName": "ShiftID", "value": 1, "timestamp": "2021-10-18T02:28:34_PM"}
#     ],
#     "headers": [],
#     "checksum": {"$numberLong": "3052508005"},
#     "serialized_key_size": -1, "serialized_value_size": 1055,
#     "serialized_header_size": -1,
#     "dateTime": "2021-10-18T14:28:34.402+00:00"
# }
# availability = "12"
# performance = "13"
# quality = "14"
# targetOee = "15"
# OeePercentage = "16"
# print(StandardOutput(Data, availability, performance, quality, targetOee, OeePercentage))
