import os
import sys
from typing import List
import datetime

from App.CNC_Calculation.APQ import Quality, OeeCalculator, Productivity
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
    availabilityJson = closeAvailabilityDocument(availabilityDoc=availabilityJson, currentTime=currentTime)

    # running
    runningData = list(filter(lambda x: (str(x["Status"]) == "Running"), availabilityJson))

    runningObject: DowntimeGraph = createDowntimeObject(runningData, "Running", "#C8F3BF")
    downTimeChartData.append(runningObject)

    # unPlanned down
    unPlannedData = list(filter(lambda x: (str(x["Status"]) == "Down"
                                           and str(x["DownTimeCode"]) == ""), availabilityJson))

    if len(unPlannedData):
        unPlannedObject: DowntimeGraph = createDowntimeObject(unPlannedData, "UnPlanned", "#F8425F")
        downTimeChartData.append(unPlannedObject)

    # planned Objects
    PlannedData = list(filter(lambda x: (str(x["Status"]) == "Down"
                                         and str(x["DownTimeCode"]) != ""), availabilityJson))
    reasonCodes = (list(str(x["DownTimeCode"]) for x in PlannedData))
    reasonCodesList = (list(set(reasonCodes)))

    for reasonCode in reasonCodesList:
        reasonData = list(filter(lambda x: (str(x["Status"]) == "Down"
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

    currentProductionData: Graph = Graph([])

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

    # recycleTime: int = Calculation_Data["RecycleTime"]
    recycleDate = datetime.datetime.strptime(Calculation_Data["RecycledDate"], '%Y-%m-%d %H:%M:%S.%f')
    fromDatetime = datetime.datetime(year=recycleDate.year,
                                     month=recycleDate.month,
                                     day=recycleDate.day,
                                     hour=recycleDate.hour,
                                     minute=recycleDate.minute,
                                     second=0
                                     )

    toDatetime = currentTime
    tempTime = fromDatetime

    while tempTime < toDatetime:
        oldTemp = tempTime
        tempTime = tempTime + datetime.timedelta(hours=1)

        currentSlotProduction = list(filter(lambda x: (
                oldTemp <= datetime.datetime.strptime(x["productionTime"], "%Y-%m-%d %H:%M:%S.%f") <= tempTime
        ), productionFile))
        totalCount: float = 0
        for qualityNameObj in qualityNameList:

            qualityName = qualityNameObj["name"]
            qualityCode = qualityNameObj["code"]

            listOfProductions = list(filter(lambda x: (x["qualityCode"] == str(qualityCode)), currentSlotProduction))
            productionCount = len(listOfProductions)

            for idx, productionCat in enumerate(productionCategoriesList):
                if productionCat.name == str(qualityName):
                    productionCategoriesList[idx].data.append([tempTime, float(productionCount)])

            totalCount = totalCount + productionCount

        for idx, productionCat in enumerate(productionCategoriesList):
            if productionCat.name == "Total Production":
                productionCategoriesList[idx].data.append([tempTime, float(totalCount)])

    currentProductionData.data = productionCategoriesList

    return currentProductionData


def currentOeeGraph(Calculation_Data, currentTime, DisplayArgs, ProductionPlan_Data):
    try:
        availabilityDoc = readAvailabilityFile()
        productionFile = readProductionFile()

        currentOeeData: Graph = Graph([])

        oeeCategoriesList: list[CurrentProductionGraphDatum] = []

        dataLabels = [
            {"category": "Availability", "color": "#4BC2BE", "showAxis": "True", "IsLeftSide": "True"},
            {"category": "Performance", "color": "#F8425F", "showAxis": "False", "IsLeftSide": "False"},
            {"category": "Quality", "color": "#68C455", "showAxis": "False", "IsLeftSide": "False"},
            {"category": "OEE", "color": "#7D30FA", "showAxis": "True", "IsLeftSide": "False"}
        ]

        for Label in dataLabels:
            productionCategory: CurrentProductionGraphDatum = CurrentProductionGraphDatum(
                name=Label["category"],
                color=Label["color"],
                show_axis=True if Label["showAxis"] == "True" else False,
                left_side=True if Label["IsLeftSide"] == "True" else False,
                data=[],
                type="line"
            )
            oeeCategoriesList.append(productionCategory)

        recycleDate = datetime.datetime.strptime(Calculation_Data["RecycledDate"], '%Y-%m-%d %H:%M:%S.%f')
        fromDatetime = datetime.datetime(year=recycleDate.year,
                                         month=recycleDate.month,
                                         day=recycleDate.day,
                                         hour=recycleDate.hour,
                                         minute=recycleDate.minute,
                                         second=0)

        toDatetime = currentTime
        tempTime = fromDatetime

        availabilityDoc = closeAvailabilityDocument(availabilityDoc=availabilityDoc, currentTime=currentTime)
        while tempTime < toDatetime:
            oldTemp = tempTime
            tempTime = tempTime + datetime.timedelta(hours=1)

            if tempTime > toDatetime:
                tempTime = toDatetime

            # Availability filter
            perHourDuration = 1 * 60 * 60
            currentSlotAvailability = list(filter(lambda x: (
                    oldTemp >= datetime.datetime.strptime(x["StartTime"], "%Y-%m-%d %H:%M:%S.%f")
                    and datetime.datetime.strptime(x["StopTime"], "%Y-%m-%d %H:%M:%S.%f") <= tempTime
                    and x["Status"] == "Running"
            ), availabilityDoc))

            # Production Filter
            currentSlotProduction = list(filter(lambda x: (
                    oldTemp <= datetime.datetime.strptime(x["productionTime"], "%Y-%m-%d %H:%M:%S.%f") <= tempTime
            ), productionFile))
            listOfGoodProductions = list(filter(lambda x: (x["category"] == str("good")), currentSlotProduction))

            # OEE Calculations
            runningDurationDelta = datetime.timedelta(hours=0, minutes=0, seconds=0)
            for availObj in currentSlotAvailability:
                availabilityDuration = datetime.datetime.strptime(str(availObj["Duration"]), "%H:%M:%S.%f")
                runningDurationDelta = runningDurationDelta + datetime.timedelta(hours=availabilityDuration.hour,
                                                                                 minutes=availabilityDuration.minute,
                                                                                 seconds=availabilityDuration.second,
                                                                                 )
            runningDuration: float = runningDurationDelta.total_seconds()
            if runningDuration > perHourDuration:
                rageDuration = tempTime - oldTemp
                runningDuration = rageDuration.total_seconds()
            ProductionIdealCycleObject = list(
                filter(lambda x: (x["Category"] == "IDEAL_CYCLE_TIME"), ProductionPlan_Data))
            cycleTime: int = int(ProductionIdealCycleObject[0]["InSeconds"])
            availabilityPercent = round((runningDuration / perHourDuration) * 100, 2)
            productivityPercent = Productivity(cycleTime, len(currentSlotProduction), runningDuration)
            qualityPercent = Quality(len(listOfGoodProductions), len(currentSlotProduction))
            oeePercent = OeeCalculator(availabilityPercent, productivityPercent, qualityPercent)

            oeeCategoriesList[0].data.append([tempTime, float(availabilityPercent)])
            oeeCategoriesList[1].data.append([tempTime, float(productivityPercent)])
            oeeCategoriesList[2].data.append([tempTime, float(qualityPercent)])
            oeeCategoriesList[3].data.append([tempTime, float(oeePercent)])

        currentOeeData.data = oeeCategoriesList
        return currentOeeData

    except Exception as ex:
        print("Error in currentOeeGraph-Output.py", ex)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fileName = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fileName, exc_tb.tb_lineno)


def closeAvailabilityDocument(availabilityDoc,currentTime):
    for index, availableObj in enumerate(availabilityDoc):
        if availableObj["Cycle"] == "Open":
            startTime = datetime.datetime.strptime(availableObj["StartTime"], "%Y-%m-%d %H:%M:%S.%f")
            stopTime = datetime.datetime.strftime(currentTime, "%Y-%m-%d %H:%M:%S.%f")
            Duration = currentTime - startTime
            Duration_fmt = str(Duration)
            availabilityDoc[index]["Duration"] = Duration_fmt
            availabilityDoc[index]["StopTime"] = stopTime
            availabilityDoc[index]["Cycle"] = "Closed"

    return availabilityDoc


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
        current_production_graph: Graph = currentProductionGraph(Calculation_Data=Calculation_Data,
                                                                 currentTime=currentTime,
                                                                 DisplayArgs=DisplayArgs)

        # OEE Graph
        oee_graph: Graph = currentOeeGraph(Calculation_Data=Calculation_Data,
                                           currentTime=currentTime,
                                           DisplayArgs=DisplayArgs,
                                           ProductionPlan_Data=ProductionPlan_Data
                                           )
        # Down Time Production
        newDownTimeGraph: List[DowntimeGraph] = downTimeGraphData(currentTime=currentTime)

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
