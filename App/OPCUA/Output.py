from App.OPCUA.JsonClass import *


def StandardOutput(result, availability: str, performance: str, quality: str, targetOee: str, OeePercentage: str,
                   OutputArgs):

    machine_id = result["MachineID"]
    job_id = result["JobID"]
    operator_id = result["OperatorID"]
    shift_id = result["ShiftID"]

    TotalDuration = float(OutputArgs["TotalDuration"])
    RunningDuration = float(OutputArgs["RunningDuration"])
    RunDur = round(RunningDuration/60, 2)
    if TotalDuration == 0:
        RunningPercentage = 0
    else:
        RunningPercentage = round(RunningDuration/TotalDuration*100, 2)

    DownDuration = float(OutputArgs["DownDuration"])
    DownDur = round(DownDuration / 60, 2)

    if TotalDuration == 0:
        DownPercentage = 0
    else:
        DownPercentage = round(DownDuration/TotalDuration*100, 2)

    # Running
    runningValue: str = str(RunningPercentage)
    runningDescription: str = "total {} Hrs running".format(RunDur)
    plannedValue: str = "0"
    plannedDescription: str = "total 0 Hrs planned down"
    unplannedValue: str = str(DownPercentage)
    unplannedDescription: str = "total {} Hrs Unplanned down".format(DownDur)

    machineRunningData = [
        {"name": "running", "value": runningValue, "color": "#68C455", "description": runningDescription},
        {"name": "planned", "value": plannedValue, "color": "#7D30FA", "description": plannedDescription},
        {"name": "unplanning", "value": unplannedValue, "color": "#F8425F", "description": unplannedDescription}
    ]

    myRunningTime: List[DowntimeDatum] = []
    for runningObj in machineRunningData:
        myRunningTime.append(DowntimeDatum.from_dict(runningObj))

    runningActiveHours = OutputArgs["RunningDurationFormatted"]
    running: Downtime = Downtime(active_hours=runningActiveHours, data=myRunningTime)

    # DownTime
    machineDownData = [
        {"name": "Lunch", "value": "33", "color": "#7D30FA", "description": "total 30 mins Lunch"},
        {"name": "Tea Break", "value": "33", "color": "#F8425F", "description": "total 30 mins Tea break"},
        {"name": "Unplanned Down Time", "value": "33", "color": "#F8B53A",
         "description": "Total 30 mins mechanical down time"}
    ]

    myDownTime: List[DowntimeDatum] = []
    for downObj in machineDownData:
        myDownTime.append(DowntimeDatum.from_dict(downObj))

    downtimeActiveHours = OutputArgs["DownTimeDurationFormatted"]
    downtime: Downtime = Downtime(active_hours=downtimeActiveHours, data=myDownTime)

    # TotalProduced
    TotalProducedCount = OutputArgs["TotalProducedTotal"]
    GoodCount = OutputArgs["GoodCount"]
    BadCount = OutputArgs["BadCount"]

    if TotalProducedCount == 0:
        GoodPercentage = 0
        BadPercentage = 0
    else:
        GoodPercentage = round(GoodCount/TotalProducedCount*100, 2)
        BadPercentage = round(BadCount/TotalProducedCount*100, 2)

    machineProducedData = [
        {"name": "Good", "value": str(GoodPercentage), "color": "#7D30FA", "description": "7000 tons"},
        {"name": "Bad", "value": str(BadPercentage), "color": "#F8425F", "description": "3000 tons"}
    ]

    myTotalProduction: List[DowntimeDatum] = []
    for totalObj in machineProducedData:
        myTotalProduction.append(DowntimeDatum.from_dict(totalObj))

    totalProduced: TotalProduced = TotalProduced(total=str(OutputArgs["TotalProducedTotal"]), data=myTotalProduction)

    # OEE
    oeeRunTime: str = "1380 minutes"
    oeeExpectedCount: str = "1380"
    oeeProductionRate: str = "1/ minute"
    oeeScheduled: Scheduled = Scheduled(run_time=oeeRunTime,
                                        expected_count=oeeExpectedCount,
                                        production_rate=oeeProductionRate)

    oee_current_run_time: str = "{} minutes".format(str(TotalDuration))
    oee_total_produced: str = str(TotalProducedCount)
    oee_good: str = str(GoodCount)
    oee_bad: str = str(BadCount)
    oeeFullFiled: Fullfiled = Fullfiled(current_run_time=oee_current_run_time,
                                        total_produced=oee_total_produced,
                                        good=oee_good,
                                        bad=oee_bad)

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
        oee=oeePercentage)

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

    myCurrentProduction: List[CurrentProductionGraphDatum] = []
    for currentObj in currentProductionGraphData:
        myCurrentProduction.append(CurrentProductionGraphDatum.from_dict(currentObj))

    currentProductionGraphCategories: List = [1, 2, 3, 4, 5, 6, 7, 8]

    current_production_graph: Graph = Graph(
        data=myCurrentProduction,
        categories=currentProductionGraphCategories
    )

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

    myGraphData: List[CurrentProductionGraphDatum] = []
    for graphObj in oee_graph_data:
        myGraphData.append(CurrentProductionGraphDatum.from_dict(graphObj))

    oeeGraphCategories: List = [1, 2, 3, 4, 5, 6, 7, 8]

    oee_graph: Graph = Graph(
        data=myGraphData,
        categories=oeeGraphCategories
    )

    # Down Time Production

    # Down Time Production - Running

    DTObjectRunningName: str = "Running"
    DTObjectRunningColor: str = "#C8F3BF"
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

    myDTGraphData: List[DowntimeGraphDatum] = []
    for DTGraphObj in DTRunningData:
        myDTGraphData.append(DowntimeGraphDatum.from_dict(DTGraphObj))

    DTObjectRunning: DowntimeGraph = DowntimeGraph(name=DTObjectRunningName,
                                                   color=DTObjectRunningColor,
                                                   data=myDTGraphData)

    # Down Time Production - Planned
    DTObjectPlannedName: str = "Planned"
    DTObjectPlannedColor: str = "#7D30FA"
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

    myDTPlannedGraphData: List[DowntimeGraphDatum] = []
    for DTPlannedGraphObj in DTPlannedData:
        myDTPlannedGraphData.append(DowntimeGraphDatum.from_dict(DTPlannedGraphObj))

    DTObjectPlanned: DowntimeGraph = DowntimeGraph(name=DTObjectPlannedName,
                                                   color=DTObjectPlannedColor,
                                                   data=myDTPlannedGraphData)

    # Down Time Production - UnPlanned
    DTObjectUnPlannedName: str = "UnPlanned"
    DTObjectUnPlannedColor: str = "#F8425F"
    DTUnPlannedData = [
        {
            "x": 'down',
            "y": [12, 12.30],
            "description": "30 mins down for undefined reason"
        },
    ]

    myDTUnPlannedGraphData: List[DowntimeGraphDatum] = []
    for DTUnPlannedGraphObj in DTUnPlannedData:
        myDTUnPlannedGraphData.append(DowntimeGraphDatum.from_dict(DTUnPlannedGraphObj))

    DTObjectUnPlanned: DowntimeGraph = DowntimeGraph(name=DTObjectUnPlannedName,
                                                     color=DTObjectUnPlannedColor,
                                                     data=myDTUnPlannedGraphData)

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
                                        )

    dumpedOutput = OutputLiveData.to_dict()
    return dumpedOutput

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
