import os
import sys
from typing import List
import datetime
from App.CNC_Calculation.MachineStatus import getSeconds_fromTimeDifference
from App.OPCUA.JsonClass import Scheduled, Fullfiled, DowntimeGraph, DowntimeGraphDatum, Graph, DowntimeDatum, Downtime, \
    TotalProduced, Oee, CurrentProductionGraphDatum, LiveData
from App.OPCUA.index import readAvailabilityFile, readDownReasonCodeFile, readProductionFile, readQualityCategory


def RunningHour_Data(Calculation_Data):
    machineRunningData = []
    RunningActiveHrs = getSeconds_fromTimeDifference(Calculation_Data["Running"]["ActiveHours"])
    PlannedActiveHrs = getSeconds_fromTimeDifference(Calculation_Data["Down"]["category"]["Planned"]["ActiveHours"])
    UnPlannedActiveHrs = getSeconds_fromTimeDifference(Calculation_Data["Down"]["category"]["Unplanned"]["ActiveHours"])

    RunningActiveHrs_formatted = Calculation_Data["Running"]["FormattedActiveHours"]
    PlannedActiveHrs_formatted = Calculation_Data["Down"]["category"]["Planned"]["FormattedActiveHours"]
    UnPlannedActiveHrs_formatted = Calculation_Data["Down"]["category"]["Unplanned"]["FormattedActiveHours"]

    TotalRunningHrs = RunningActiveHrs + PlannedActiveHrs + UnPlannedActiveHrs
    if TotalRunningHrs > 0:
        RunningActiveHrs_Percent = round(RunningActiveHrs / TotalRunningHrs * 100, 2)
        PlannedActiveHrs_Percent = round(PlannedActiveHrs / TotalRunningHrs * 100, 2)
        UnPlannedActiveHrs_Percent = round(UnPlannedActiveHrs / TotalRunningHrs * 100, 2)
    else:
        RunningActiveHrs_Percent = 0
        PlannedActiveHrs_Percent = 0
        UnPlannedActiveHrs_Percent = 0

    if RunningActiveHrs > 0:
        running_Object = {"name": "running", "value": str(RunningActiveHrs_Percent), "color": "#68C455",
                          "description": "total {} Hrs running".format(RunningActiveHrs_formatted)}
        machineRunningData.append(running_Object)

    if PlannedActiveHrs > 0:
        planned_Object = {"name": "planned", "value": str(PlannedActiveHrs_Percent), "color": "#7D30FA",
                          "description": "total {} Hrs planned down".format(PlannedActiveHrs_formatted)}
        machineRunningData.append(planned_Object)

    if UnPlannedActiveHrs > 0:
        unplanned_Object = {"name": "unplanning", "value": str(UnPlannedActiveHrs_Percent), "color": "#F8425F",
                            "description": "total {} Hrs Unplanned down".format(UnPlannedActiveHrs_formatted)}
        machineRunningData.append(unplanned_Object)

    if len(machineRunningData) == 0:
        unplanned_Object = {"name": "running", "value": "100", "color": "#68C455",
                            "description": "total 0 Hrs running"}
        machineRunningData.append(unplanned_Object)

    return machineRunningData


def UnplannedDownHour_Data(Calculation_Data):
    machineDownData = []

    downActiveHrs = getSeconds_fromTimeDifference(Calculation_Data["Down"]["ActiveHours"])
    unPlannedActiveHrs = getSeconds_fromTimeDifference(Calculation_Data["Down"]["category"]["Unplanned"]["ActiveHours"])

    unPlannedActiveHrs_formatted = Calculation_Data["Down"]["category"]["Unplanned"]["FormattedActiveHours"]

    plannedDetails = []
    plannedDetailsObject = Calculation_Data["Down"]["category"]["Planned"]["Details"]

    for detail in plannedDetailsObject:
        if downActiveHrs > 0:
            obj = {
                "name": detail["DownReasons"],
                "percent": round(getSeconds_fromTimeDifference(detail["ActiveHours"]) / downActiveHrs * 100, 2),
                "color": detail["color"],
                "formattedActiveHrs": detail["FormattedActiveHours"]
            }
            plannedDetails.append(obj)

    if downActiveHrs > 0:
        unPlannedPercent = round(unPlannedActiveHrs / downActiveHrs * 100, 2)
    else:
        unPlannedPercent = 0

    if unPlannedActiveHrs > 0:
        unPlanned_Object = {"name": "Unplanned Down Time", "value": str(unPlannedPercent), "color": "#F8B53A",
                            "description": "total {} Hrs UnPlanned".format(unPlannedActiveHrs_formatted)}
        machineDownData.append(unPlanned_Object)

    for plannedData in plannedDetails:
        unPlanned_Object = {
            "name": plannedData["name"],
            "value": str(plannedData["percent"]),
            "color": plannedData["color"],
            "description": "total {0} Hrs {1}".format(plannedData["formattedActiveHrs"], plannedData["name"])
        }
        machineDownData.append(unPlanned_Object)

    if len(machineDownData) == 0:
        empty_Object = {"name": "Down Time", "value": "100", "color": "#F8425F",
                        "description": "Total 0 mins unplanned time"}
        machineDownData.append(empty_Object)

    return machineDownData


def goodBad_Data(Calculation_Data):
    machineProducedData = []
    goodCount = Calculation_Data["goodCount"]
    badCount = Calculation_Data["badCount"]
    totalProducedCount = badCount + goodCount

    if totalProducedCount == 0:
        goodPercentage = 0
        badPercentage = 0
    else:
        goodPercentage = round(goodCount / totalProducedCount * 100, 2)
        badPercentage = round(badCount / totalProducedCount * 100, 2)

    if goodCount > 0:
        goodObj = {"name": "Good", "value": str(goodPercentage),
                   "color": "#7D30FA", "description": "{}".format(goodCount)}
        machineProducedData.append(goodObj)

    if badCount > 0:
        badObj = {"name": "Bad", "value": str(badPercentage),
                  "color": "#F8425F", "description": "{}".format(badCount)}
        machineProducedData.append(badObj)

    if len(machineProducedData) == 0:
        noObj = {"name": "Good", "value": "100", "color": "#7D30FA", "description": "0"}
        machineProducedData.append(noObj)

    return machineProducedData


def ScheduledData(ProductionPlan_Data):
    ProductionPlanObject = list(filter(lambda x: (x["Category"] == "PRODUCTION_PLAN_TIME"), ProductionPlan_Data))
    ProductionIdealCycleObject = list(filter(lambda x: (x["Category"] == "IDEAL_CYCLE_TIME"), ProductionPlan_Data))

    PlannedRunTime: int = int(ProductionPlanObject[0]["InSeconds"])
    PlannedRunTimeInMinutes: int = int(PlannedRunTime / 60)
    cycleTime: int = int(ProductionIdealCycleObject[0]["InSeconds"])
    cycleTime_inMinutes: int = int(cycleTime / 60)
    expectedCount: int = int(PlannedRunTime / cycleTime)

    oeeRunTime: str = "{} minutes".format(PlannedRunTimeInMinutes)
    oeeExpectedCount: str = str(expectedCount)
    oeeProductionRate: str = "{0}/ minute".format(cycleTime_inMinutes)

    # Scheduled
    oeeScheduled: Scheduled = Scheduled(run_time=oeeRunTime,
                                        expected_count=oeeExpectedCount,
                                        production_rate=oeeProductionRate)
    return oeeScheduled


def FulfilledData(Calculation_Data):
    TotalDuration = getSeconds_fromTimeDifference(Calculation_Data["TotalDuration"])
    goodCount = Calculation_Data["goodCount"]
    badCount = Calculation_Data["badCount"]
    TotalProducedCount = goodCount + badCount
    TotalDuration_Minutes: int = int(int(TotalDuration) / 60)
    oee_current_run_time: str = "{} minutes".format(str(TotalDuration_Minutes))
    oee_total_produced: str = str(TotalProducedCount)
    oee_good: str = str(goodCount)
    oee_bad: str = str(badCount)
    oeeFullFiled: Fullfiled = Fullfiled(current_run_time=oee_current_run_time,
                                        total_produced=oee_total_produced,
                                        good=oee_good,
                                        bad=oee_bad)
    return oeeFullFiled


def OeeData(ProductionPlan_Data, Calculation_Data, OeeArgs):
    oeeScheduled = ScheduledData(ProductionPlan_Data)
    oeeFullFiled: Fullfiled = FulfilledData(Calculation_Data)
    oeeAvailability: str = OeeArgs["availability"]
    oeePerformance: str = OeeArgs["performance"]
    oeeQuality: str = OeeArgs["quality"]
    oeeTargetOee: str = OeeArgs["targetOee"]
    oeePercentage: str = OeeArgs["OeePercentage"]

    oee: Oee = Oee(
        scheduled=oeeScheduled,
        fullfiled=oeeFullFiled,
        availability=oeeAvailability,
        performance=oeePerformance,
        quality=oeeQuality,
        target_oee=oeeTargetOee,
        oee=oeePercentage)
    return oee


def downTimeGraphData(currentTime):
    downTimeChartData: list[DowntimeGraph] = []
    availabilityJson = readAvailabilityFile()
    reasonCodeList: list = readDownReasonCodeFile()

    # Current Status
    currentRunningData = list(filter(lambda x: (str(x["Cycle"]) == "Open"), availabilityJson))
    currentStartTime = datetime.datetime.strptime(str(currentRunningData[0]["StartTime"]), "%Y-%m-%d %H:%M:%S.%f")
    currentStopTime = datetime.datetime.strptime(str(currentTime), "%Y-%m-%d %H:%M:%S.%f")
    currentDuration = currentStopTime - currentStartTime
    currentDuration_str = str(currentDuration)

    currentRunningData[0]["StopTime"] = currentStopTime
    currentRunningData[0]["Duration"] = currentDuration_str

    if currentRunningData[0]["Status"] == "Running":
        currentRunningObject: DowntimeGraph = createDowntimeObject(currentRunningData, "Running", "#C8F3BF")
        downTimeChartData.append(currentRunningObject)

    else:
        RunningReasonCodeDoc = list(filter(
            lambda x: (str(x["DownCode"]) == str(currentRunningData[0]["DownTimeCode"])), reasonCodeList)
        )
        if len(RunningReasonCodeDoc) == 0:
            currentRunningObject: DowntimeGraph = createDowntimeObject(currentRunningData, "UnPlanned", "#F8425F")
            downTimeChartData.append(currentRunningObject)
        else:
            runningPlannedName = RunningReasonCodeDoc[0]["DownCodeReason"]
            runningPlannedColor = RunningReasonCodeDoc[0]["color"]
            currentRunningObject: DowntimeGraph = createDowntimeObject(
                currentRunningData, runningPlannedName, runningPlannedColor)
            downTimeChartData.append(currentRunningObject)

    # running
    runningData = list(filter(lambda x: (str(x["Status"]) == "Running"
                                         and str(x["Cycle"]) == "Closed"), availabilityJson))

    runningObject: DowntimeGraph = createDowntimeObject(runningData, "Running", "#C8F3BF")
    downTimeChartData.append(runningObject)

    # unPlanned down
    unPlannedData = list(filter(lambda x: (str(x["Status"]) == "Down"
                                           and str(x["Cycle"]) == "Closed"
                                           and str(x["DownTimeCode"]) == ""), availabilityJson))

    unPlannedObject: DowntimeGraph = createDowntimeObject(unPlannedData, "UnPlanned", "#F8425F")
    downTimeChartData.append(unPlannedObject)

    # planned Objects
    PlannedData = list(filter(lambda x: (str(x["Status"]) == "Down"
                                         and str(x["Cycle"]) == "Closed"
                                         and str(x["DownTimeCode"]) != ""), availabilityJson))
    reasonCodes = (list(str(x["DownTimeCode"]) for x in PlannedData))
    reasonCodesList = (list(set(reasonCodes)))

    for reasonCode in reasonCodesList:

        reasonData = list(filter(lambda x: (str(x["Status"]) == "Down"
                                            and str(x["Cycle"]) == "Closed"
                                            and str(x["DownTimeCode"]) == str(reasonCode)), PlannedData))
        reasonCodeDoc = list(filter(lambda x: (str(x["DownCode"]) == reasonCode), reasonCodeList))

        plannedName = reasonCodeDoc[0]["DownCodeReason"]
        plannedColor = reasonCodeDoc[0]["color"]

        PlannedObject: DowntimeGraph = createDowntimeObject(reasonData, plannedName, plannedColor)
        downTimeChartData.append(PlannedObject)

    return downTimeChartData


def createDowntimeObject(downData, downtimeName, color):

    downTimeObject: DowntimeGraph = DowntimeGraph(name=downtimeName,
                                                  color=color,
                                                  data=[])

    downTimeObjectDetailArray: list[DowntimeGraphDatum] = []
    for downObj in downData:
        startTime = datetime.datetime.strptime(str(downObj["StartTime"]), "%Y-%m-%d %H:%M:%S.%f")
        stopTime = datetime.datetime.strptime(str(downObj["StopTime"]), "%Y-%m-%d %H:%M:%S.%f")
        duration = datetime.datetime.strptime(str(downObj["Duration"]), "%H:%M:%S.%f")
        newObj: DowntimeGraphDatum = DowntimeGraphDatum(
            x="down",
            y=[startTime, stopTime],
            description="{} hrs {} mins running ".format(duration.hour, duration.minute))
        downTimeObjectDetailArray.append(newObj)

    downTimeObject.data = downTimeObjectDetailArray

    return downTimeObject


def currentProductionGraph(Calculation_Data, currentTime, DisplayArgs):

    productionFile = readProductionFile()
    qualityCategories = readQualityCategory()

    currentProductionData: Graph = Graph([], [])
    categories: List[datetime] = []
    productionCategoriesList: list[CurrentProductionGraphDatum] = []
    totalProductionQualityCodesList = list(x["qualityCode"] for x in productionFile)
    totalProductionQualityList = list(set(totalProductionQualityCodesList))
    qualityNameList: list[object] = []
    # list of categories append into main list
    for QualityCode in totalProductionQualityList:
        qualityCategory = list(filter(lambda x: (x["qualityCode"] == str(QualityCode)), qualityCategories))

        productionCategory: CurrentProductionGraphDatum = CurrentProductionGraphDatum(
            name=qualityCategory[0]["category"],
            color=qualityCategory[0]["color"],
            show_axis=True if qualityCategory[0]["showAxis"] == "True" else False,
            left_side=True if qualityCategory[0]["IsLeftSide"] == "True" else False,
            data=[],
            type="line"
        )
        productionCategoriesList.append(productionCategory)
        qualityNameList.append(
            {
                "name": qualityCategory[0]["category"],
                "code": qualityCategory[0]["qualityCode"]
            }
        )

    # Total production
    totalProductionCategory: CurrentProductionGraphDatum = CurrentProductionGraphDatum(
        name="Total Production",
        color="#68C455",
        show_axis=False,
        left_side=False,
        data=[],
        type="line"
    )
    productionCategoriesList.append(totalProductionCategory)

    recycleTime: int = Calculation_Data["RecycleTime"]
    recycleDate = datetime.datetime.strptime(Calculation_Data["RecycledDate"], "%Y-%m-%d")
    fromDatetime = datetime.datetime(year=recycleDate.year,
                                     month=recycleDate.month,
                                     day=recycleDate.day,
                                     hour=recycleTime,
                                     minute=0,
                                     second=0
                                     )
    toDatetime = currentTime
    tempTime = fromDatetime
    categories.append(fromDatetime)
    totalCount: float = 0

    while tempTime < toDatetime:
        oldTemp = tempTime
        tempTime = tempTime + datetime.timedelta(hours=1)
        categories.append(tempTime)

        currentSlotProduction = list(filter(lambda x: (
                oldTemp <= datetime.datetime.strptime(x["productionTime"], "%Y-%m-%d %H:%M:%S.%f") <= tempTime
        ), productionFile))

        for qualityNameObj in qualityNameList:

            qualityName = qualityNameObj["name"]
            qualityCode = qualityNameObj["code"]

            listOfProductions = list(filter(lambda x: (x["qualityCode"] == str(qualityCode)), currentSlotProduction))
            productionCount = len(listOfProductions)

            for idx, productionCat in enumerate(productionCategoriesList):
                if productionCat.name == str(qualityName):
                    productionCategoriesList[idx].data.append(float(productionCount))

            totalCount = totalCount + productionCount

        for idx, productionCat in enumerate(productionCategoriesList):
            if productionCat.name == "Total Production":
                productionCategoriesList[idx].data.append(float(totalCount))

    currentProductionData.categories = categories
    currentProductionData.data = productionCategoriesList

    return currentProductionData


def StandardOutput(result, OeeArgs, ProductionPlan_Data, Calculation_Data, OutputArgs, DisplayArgs):
    try:
        currentTime: datetime = datetime.datetime.now()
        machine_id = result["MachineID"]
        job_id = result["JobID"]
        operator_id = result["OperatorID"]
        shift_id = result["ShiftID"]

        # Running
        machineRunningData = RunningHour_Data(Calculation_Data=Calculation_Data)
        myRunningTime: List[DowntimeDatum] = []
        for runningObj in machineRunningData:
            myRunningTime.append(DowntimeDatum.from_dict(runningObj))

        runningActiveHours = OutputArgs["RunningDurationFormatted"]
        running: Downtime = Downtime(active_hours=runningActiveHours, data=myRunningTime)

        # DownTime
        machineDownData = UnplannedDownHour_Data(Calculation_Data=Calculation_Data)
        myDownTime: List[DowntimeDatum] = []
        for downObj in machineDownData:
            myDownTime.append(DowntimeDatum.from_dict(downObj))

        downtimeActiveHours = OutputArgs["DownTimeDurationFormatted"]
        downtime: Downtime = Downtime(active_hours=downtimeActiveHours, data=myDownTime)

        # TotalProduced
        machineProducedData = goodBad_Data(Calculation_Data=Calculation_Data)
        myTotalProduction: List[DowntimeDatum] = []
        for totalObj in machineProducedData:
            myTotalProduction.append(DowntimeDatum.from_dict(totalObj))

        totalProduced: TotalProduced = TotalProduced(total=str(OutputArgs["TotalProducedTotal"]),
                                                     data=myTotalProduction)

        # OEE
        oee: Oee = OeeData(ProductionPlan_Data, Calculation_Data, OeeArgs)
        # Current Production Graph
        currentProductionGraph(Calculation_Data=Calculation_Data,
                               currentTime=currentTime,
                               DisplayArgs=DisplayArgs)
        # Current Production Graph
        # currentProductionGraphData = [
        #     {
        #         "name": "Quality Product",
        #         "color": "#00FF00",
        #         "type": 'line',
        #         "showAxis": True,
        #         "leftSide": True,
        #         "data": [50, 100, 150, 200, 250, 300, 350, 460]
        #     },
        #     {
        #         "name": "Waster Product",
        #         "color": "#0000FF",
        #         "type": 'line',
        #         "showAxis": False,
        #         "leftSide": False,
        #         "data": [10, 29, 37, 36, 44, 45, 50, 58]
        #     },
        #     {
        #         "name": "Bad Product",
        #         "color": "#FF0000",
        #         "type": 'line',
        #         "showAxis": True,
        #         "leftSide": False,
        #         "data": [50, 29, 37, 36, 44, 45, 50, 58]
        #     }
        # ]

        # myCurrentProduction: List[CurrentProductionGraphDatum] = []
        # for currentObj in currentProductionGraphData:
        #     myCurrentProduction.append(CurrentProductionGraphDatum.from_dict(currentObj))
        #
        # currentProductionGraphCategories: List = [1, 2, 3, 4, 5, 6, 7, 8]

        current_production_graph: Graph = currentProductionGraph(Calculation_Data, currentTime, DisplayArgs)

        # OEE Graph
        oee_graph_data = [
            {
                "name": "Availability",
                "color": "#87CEEB",
                "showAxis": True,
                "leftSide": True,
                "data": [50, 100, 150, 200, 250, 300, 350, 460]
            },
            {
                "name": "Performance",
                "color": "#FF0000",
                "showAxis": False,
                "leftSide": False,
                "data": [10, 29, 37, 36, 44, 45, 50, 58]
            },
            {
                "name": "Quality",
                "color": "#00FF00",
                "showAxis": False,
                "leftSide": False,
                "data": [50, 29, 37, 36, 44, 45, 50, 58]
            },
            {
                "name": "OEE %",
                "color": "#0000FF",
                "showAxis": True,
                "leftSide": False,
                "data": [
                    20.0,
                    29.0,
                    37.0,
                    36.0,
                    44.0,
                    45.0,
                    50.0,
                    58.0
                ]
            }
        ]

        myGraphData: List[CurrentProductionGraphDatum] = []
        for graphObj in oee_graph_data:
            myGraphData.append(CurrentProductionGraphDatum.from_dict(graphObj))
        oeeGraphCategories: List[datetime] = []
        for i in range(6):
            myTime = datetime.datetime(year=2021,
                                       month=11,
                                       day=1,
                                       hour=i,
                                       minute=0,
                                       second=0)
            oeeGraphCategories.append(myTime)

        oee_graph: Graph = Graph(
            data=myGraphData,
            categories=oeeGraphCategories
        )

        # Down Time Production
        newDownTimeGraph: List[DowntimeGraph] = downTimeGraphData(currentTime)

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
                                            downtime_graph=newDownTimeGraph)

        dumpedOutput = OutputLiveData.to_dict()
        return dumpedOutput

    except Exception as ex:
        print("Error in StandardOutput-Output.py", ex)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fileName = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fileName, exc_tb.tb_lineno)
