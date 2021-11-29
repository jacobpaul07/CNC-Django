import datetime
import json
import App.globalsettings as gs
from rest_framework.views import APIView
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse

from App.CNC_Calculation.APQ import AvailabilityCalculation, ProductionCalculation, Quality, OeeCalculator
from App.OPCUA.index import readCalculation_file
from MongoDB_Main import Document as Doc
from App.CNC_Calculation.MachineApi import MachineApi
from App.OPCUA.ResultFormatter import DurationCalculatorFormatted1


class getmachineid(APIView):
    @staticmethod
    def get(request):
        readCalculationDataJson = readCalculation_file()

        defaultData = {
            "machineID": readCalculationDataJson["MachineId"]
        }
        jsonResponse = json.dumps(defaultData, indent=4)
        return HttpResponse(jsonResponse, "application/json")


class getproductionreport(APIView):
    @staticmethod
    def get(request):
        # fromdate = request.GET.get("fromDate")
        # todate = request.GET.get("toDate")

        productionReport = {
            "chartdetails": [
                {
                    "name": "good",
                    "color": "#68C455",
                    "showAxis": True,
                    "leftSide": False
                },
                {
                    "name": "bad",
                    "color": "#F8425F",
                    "showAxis": True,
                    "leftSide": False
                },
                {
                    "name": "totalproduction",
                    "color": "#7D30FA",
                    "showAxis": True,
                    "leftSide": False
                },
                {
                    "name": "expected",
                    "color": "#2C203F",
                    "showAxis": True,
                    "leftSide": False
                }
            ],
            "data": [
                {
                    "sno": 1,
                    "date": "2021-11-01",
                    "shiftCode": "SH001",
                    "operatorCode": "OP001",
                    "jobCode": "BC001",
                    "plannedProductionTime": "20",
                    "machineutilizeTime": "18",
                    "plannedProductionTimeFormatted": "20h",
                    "machineutilizeTimeFormatted": "18h",
                    "availabilityRate": "81",
                    "performanceRate": "50",
                    "qualityRate": "80",
                    "oee": "72",
                    "expected": "300",
                    "good": "300",
                    "bad": "300",
                    "totalProduction": "600"
                },
                {
                    "sno": 2,
                    "date": "2021-11-01",
                    "shiftCode": "SH002",
                    "operatorCode": "OP002",
                    "jobCode": "BC002",
                    "plannedProductionTime": "20",
                    "machineutilizeTime": "18",
                    "plannedProductionTimeFormatted": "20h",
                    "machineutilizeTimeFormatted": "18h",
                    "availabilityRate": "81",
                    "performanceRate": "50",
                    "qualityRate": "80",
                    "oee": "85",
                    "expected": "300",
                    "good": "300",
                    "bad": "300",
                    "totalProduction": "600"
                },
                {
                    "sno": 3,
                    "date": "2021-11-02",
                    "shiftCode": "SH001",
                    "operatorCode": "OP001",
                    "jobCode": "BC001",
                    "plannedProductionTime": "20",
                    "machineutilizeTime": "18",
                    "plannedProductionTimeFormatted": "20h",
                    "machineutilizeTimeFormatted": "18h",
                    "availabilityRate": "81",
                    "performanceRate": "50",
                    "qualityRate": "80",
                    "oee": "100",
                    "expected": "300",
                    "good": "150",
                    "bad": "150",
                    "totalProduction": "300"
                },
                {
                    "sno": 3,
                    "date": "2021-11-03",
                    "shiftCode": "SH001",
                    "operatorCode": "OP001",
                    "jobCode": "BC001",
                    "plannedProductionTime": "20",
                    "machineutilizeTime": "18",
                    "plannedProductionTimeFormatted": "20h",
                    "machineutilizeTimeFormatted": "18h",
                    "availabilityRate": "81",
                    "performanceRate": "50",
                    "qualityRate": "80",
                    "oee": "72",
                    "expected": "300",
                    "good": "150",
                    "bad": "150",
                    "totalProduction": "300"
                },
                {
                    "sno": 3,
                    "date": "2021-11-04",
                    "shiftCode": "SH001",
                    "operatorCode": "OP001",
                    "jobCode": "BC001",
                    "plannedProductionTime": "20",
                    "machineutilizeTime": "18",
                    "plannedProductionTimeFormatted": "20h",
                    "machineutilizeTimeFormatted": "18h",
                    "availabilityRate": "81",
                    "performanceRate": "50",
                    "qualityRate": "80",
                    "oee": "72",
                    "expected": "300",
                    "good": "150",
                    "bad": "150",
                    "totalProduction": "300"
                },
                {
                    "sno": 3,
                    "date": "2021-11-05",
                    "shiftCode": "SH001",
                    "operatorCode": "OP001",
                    "jobCode": "BC001",
                    "plannedProductionTime": "20",
                    "machineutilizeTime": "18",
                    "plannedProductionTimeFormatted": "20h",
                    "machineutilizeTimeFormatted": "18h",
                    "availabilityRate": "81",
                    "performanceRate": "50",
                    "qualityRate": "80",
                    "oee": "72",
                    "expected": "300",
                    "good": "150",
                    "bad": "150",
                    "totalProduction": "300"
                },
                {
                    "sno": 3,
                    "date": "2021-11-06",
                    "shiftCode": "SH001",
                    "operatorCode": "OP001",
                    "jobCode": "BC001",
                    "plannedProductionTime": "20",
                    "machineutilizeTime": "18",
                    "plannedProductionTimeFormatted": "20h",
                    "machineutilizeTimeFormatted": "18h",
                    "availabilityRate": "81",
                    "performanceRate": "50",
                    "qualityRate": "80",
                    "oee": "72",
                    "expected": "300",
                    "good": "150",
                    "bad": "150",
                    "totalProduction": "300"
                }
            ]
        }
        # fromDate = datetime.datetime.strptime(fromdate, gs.OEE_MongoDBDateTimeFormat)
        # toDate = datetime.datetime.strptime(todate, gs.OEE_MongoDBDateTimeFormat)
        #
        # productionreport = MachineApi.getProductionReport(MachineID="MID-01", fromdate=fromDate, todate=toDate)
        #
        # productionreportlist = []
        # for index, prodObj in enumerate(productionreport):
        #     data = {
        #         "sno": str(index + 1),
        #         "date": prodObj["Timestamp"],
        #         "shiftCode": prodObj["shiftID"],
        #         "operatorCode": prodObj["operatorID"],
        #         "jobCode": prodObj["jobID"],
        #         "plannedProductionTime": prodObj["running"],
        #         "machineutilizeTime": prodObj["running"]["activeHours"],
        #         "plannedProductionTimeFormatted": prodObj["oee"]["scheduled"]["runTime"],
        #         "machineutilizeTimeFormatted": prodObj["oee"]["scheduled"]["runTime"],
        #         "availabilityRate": prodObj["oee"]["availability"],
        #         "performanceRate": prodObj["oee"]["performance"],
        #         "oee": prodObj["oee"]["oee"],
        #         "expected": prodObj["oee"]["scheduled"]["expectedCount"],
        #         "good": prodObj["oee"]["fullfiled"]["good"],
        #         "bad": prodObj["oee"]["fullfiled"]["bad"],
        #         "totalProduction": prodObj["oee"]["fullfiled"]["totalProduced"],
        #     }
        #     productionreportlist.append(data)
        #
        # returnData = {
        #     "chartdetails": colorJson,
        #     "data": productionreportlist
        # }

        jsonResponse = json.dumps(productionReport, indent=4)
        return HttpResponse(jsonResponse, "application/json")


class getoeereport(APIView):
    @staticmethod
    def get(request):
        fromdate = request.GET.get("fromDate")
        todate = request.GET.get("toDate")
        fromDate = datetime.datetime.strptime(fromdate, gs.OEE_MongoDBDateTimeFormat)
        toDate = datetime.datetime.strptime(todate, gs.OEE_MongoDBDateTimeFormat)

        colorJson = [
            {
                "name": "availability",
                "color": "#FFFFFF",
                "showAxis": True,
                "leftSide": True
            },
            {
                "name": "performance",
                "color": "#F8425F",
                "showAxis": False,
                "leftSide": False
            },
            {
                "name": "quality",
                "color": "#68C455",
                "showAxis": False,
                "leftSide": False
            },
            {
                "name": "oee",
                "color": "#7D30FA",
                "showAxis": True,
                "leftSide": False
            }
        ]

        oeereport = MachineApi.getOeeReport(fromdate=fromDate, todate=toDate)
        DownTimeDocument = Doc().DB_Read(col="DownTimeCode")
        QualityDocument = Doc().Read_Quality_Document(fromDate=fromDate, toDate=toDate)
        downtimereport = MachineApi.getDownTimeReport(fromdate=fromDate, todate=toDate, status="Down")
        oeeReportList = []
        index = 0
        for currentdatereport in oeereport:
            index = index + 1
            currentDate = datetime.datetime.strftime(currentdatereport["_id"], gs.OEE_OutputDateTimeFormat)
            firstData = currentdatereport["data"]
            ProductionPlan = firstData["ProductionPlan_Data"]

            targetList = list(filter(lambda x: (x["Category"] == "TARGET_OEE"), ProductionPlan))
            productionList = list(filter(lambda x: (x["Category"] == "PRODUCTION_PLAN_TIME"), ProductionPlan))
            standardCycleList = list(filter(lambda x: (x["Category"] == "IDEAL_CYCLE_TIME"), ProductionPlan))

            targetPercent = 0 if len(targetList) == 0 else float(targetList[0]["InSeconds"])
            productionTime = 0 if len(productionList) == 0 else float(productionList[0]["InSeconds"])
            standardCycleTime = 0 if len(standardCycleList) == 0 else float(standardCycleList[0]["InSeconds"])

            totalProductionCount = 0
            goodProductionCount = 0

            todayProductionList = list(filter(lambda x: (x["date"] == currentDate), QualityDocument))
            for production in todayProductionList:
                if production["category"] == "good":
                    goodProductionCount = goodProductionCount + int(production["productioncount"])
                totalProductionCount = totalProductionCount + int(production["productioncount"])

            # Unplanned down duration begin
            unPlannedDownObject = list(filter(lambda x: (datetime.datetime.strftime(x["StartTime"],
                                                                                    gs.OEE_OutputDateTimeFormat) == fromdate and
                                                         x["DownTimeCode"] == ""), downtimereport))

            plannedDownObject = list(filter(lambda x: (datetime.datetime.strftime(x["StartTime"],
                                                                                  gs.OEE_OutputDateTimeFormat) == fromdate and
                                                       x["DownTimeCode"] != ""), downtimereport))

            for plannedObj in plannedDownObject:
                categoryList = list(filter(lambda x: (x["DownCode"] == plannedObj["DownTimeCode"]), DownTimeDocument))
                if len(categoryList) > 0:
                    if categoryList[0]["Category"] == "UnPlanned DownTime":
                        unPlannedDownObject.append(plannedObj)

            unPlannedDownDurationDelta = datetime.timedelta()
            for durationTime in unPlannedDownObject:
                unPlannedDurationTimeStr = durationTime["Duration"]
                unPlannedDurationDelta = datetime.datetime.strptime(unPlannedDurationTimeStr, gs.OEE_JsonTimeFormat)
                unPlannedDownDurationDelta = unPlannedDownDurationDelta + datetime.timedelta(
                    hours=unPlannedDurationDelta.hour,
                    minutes=unPlannedDurationDelta.minute,
                    seconds=unPlannedDurationDelta.second)
            # Unplanned down duration end

            Production_Planned_Time = float(productionTime)
            Total_Unplanned_Downtime = float(unPlannedDownDurationDelta.total_seconds())
            Machine_Utilized_Time: float = Production_Planned_Time - Total_Unplanned_Downtime
            availability = AvailabilityCalculation(Machine_Utilized_Time=Machine_Utilized_Time,
                                                   Production_Planned_Time=Production_Planned_Time)

            performance = ProductionCalculation(Standard_Cycle_Time=standardCycleTime,
                                                Total_Produced_Components=totalProductionCount,
                                                UtilisedTime_Seconds=Machine_Utilized_Time)

            quality = Quality(goodCount=goodProductionCount, totalCount=totalProductionCount)

            oee = OeeCalculator(AvailPercent=availability, PerformPercent=performance, QualityPercent=quality)

            data = {
                "sno": str(index),
                "date": str(currentDate),
                "target": str(targetPercent),
                "availability": str(availability),
                "performance": str(performance),
                "quality": str(quality),
                "oee": str(oee)
            }
            oeeReportList.append(data)

        returnData = {
            "chartdetails": colorJson,
            "data": oeeReportList
        }

        jsonResponse = json.dumps(returnData, indent=4, skipkeys=True)

        print(jsonResponse)
        return HttpResponse(jsonResponse, "application/json")


class getdowntimereport(APIView):
    @staticmethod
    def get(request):
        DownTimeDocument = Doc().DB_Read(col="DownTimeCode")
        colorJson = [
            {
                "name": "Planned DownTime",
                "color": "#7D30FA",
                "showAxis": True,
                "leftSide": False
            },
            {
                "name": "UnPlanned DownTime",
                "color": "#F8425F",
                "showAxis": True,
                "leftSide": False
            }]

        fromdate = request.GET.get("fromDate")
        todate = request.GET.get("toDate")

        fromDate = datetime.datetime.strptime(fromdate, gs.OEE_MongoDBDateTimeFormat)
        toDate = datetime.datetime.strptime(todate, gs.OEE_MongoDBDateTimeFormat)

        downtimereport = MachineApi.getDownTimeReport(fromdate=fromDate, todate=toDate, status="Down")
        runtimereport = MachineApi.getDownTimeReport(fromdate=fromDate, todate=toDate, status="Running")
        reasonCodes = (list(str(x["DownTimeCode"]) for x in downtimereport))
        reasonCodesList = (list(set(reasonCodes)))
        index = 0
        downdatareportList = []
        for obj in reasonCodesList:
            index += 1
            downId = obj
            downObject = list(filter(lambda x: (x["DownTimeCode"] == downId), downtimereport))
            downName = downObject[0]["Description"]

            categoryList = list(filter(lambda x: (x["DownCode"] == downId), DownTimeDocument))
            category = "UnPlanned DownTime" if len(categoryList) == 0 else categoryList[0]["Category"]
            percentage = "80"
            totalDurationDelta = datetime.timedelta()

            for durationTime in downObject:
                durationTimeStr = durationTime["Duration"]
                durationDelta = datetime.datetime.strptime(durationTimeStr, gs.OEE_JsonTimeFormat)
                totalDurationDelta = totalDurationDelta + datetime.timedelta(hours=durationDelta.hour,
                                                                             minutes=durationDelta.minute,
                                                                             seconds=durationDelta.second)

            totalDurationStr = str(totalDurationDelta)
            totalDur = datetime.datetime.strptime(totalDurationStr, gs.OEE_OutputTimeFormat)
            totalDurationFormattedStr = DurationCalculatorFormatted1(durationStr=totalDurationStr)
            downId = "0" if downId == "" else downId
            data = {
                "sno": int(index),
                "downId": downId,
                "downName": downName,
                "downDescription": downName,
                "category": category,
                "totalDownTimeFormatted": totalDurationFormattedStr,
                "totalDownTime": "{}.{}".format(totalDur.hour, totalDur.minute),
                "percentage": percentage
            }
            downdatareportList.append(data)

        downDates = (list(
            datetime.datetime.strftime(x["StartTime"], gs.OEE_OutputDateTimeFormat) for x in downtimereport))

        downDatesList = (list(set(downDates)))
        index = 0
        datewisereportList = []
        for obj in downDatesList:
            index += 1
            downDateStr = obj

            # total down duration begin
            totalDownObject = list(filter(lambda x: (
                    datetime.datetime.strftime(x["StartTime"],
                                               gs.OEE_OutputDateTimeFormat) == downDateStr),
                                          downtimereport))
            totalDownDurationDelta = datetime.timedelta()
            for durationTime in totalDownObject:
                totalDurationTimeStr = durationTime["Duration"]
                totalDurationDelta = datetime.datetime.strptime(totalDurationTimeStr, gs.OEE_JsonTimeFormat)
                totalDownDurationDelta = totalDownDurationDelta + datetime.timedelta(hours=totalDurationDelta.hour,
                                                                                     minutes=totalDurationDelta.minute,
                                                                                     seconds=totalDurationDelta.second)
            totalDownDurationStr = str(totalDownDurationDelta)
            totalDurationFormattedStr = DurationCalculatorFormatted1(durationStr=totalDownDurationStr)
            # total down duration end

            # planned down duration begin
            TempPlannedDownObject = list(filter(lambda x: (datetime.datetime.strftime(x["StartTime"],
                                                                                      gs.OEE_OutputDateTimeFormat) == downDateStr and
                                                           x["DownTimeCode"] != ""), downtimereport))

            plannedDownObject = []
            for plannedObj in TempPlannedDownObject:
                categoryList = list(filter(lambda x: (x["DownCode"] == plannedObj["DownTimeCode"]), DownTimeDocument))
                if len(categoryList) > 0:
                    if categoryList[0]["Category"] == "Planned DownTime":
                        plannedDownObject.append(plannedObj)

            plannedDownDurationDelta = datetime.timedelta()
            for durationTime in plannedDownObject:
                plannedDurationTimeStr = durationTime["Duration"]
                plannedDurationDelta = datetime.datetime.strptime(plannedDurationTimeStr, gs.OEE_JsonTimeFormat)
                plannedDownDurationDelta = plannedDownDurationDelta + datetime.timedelta(
                    hours=plannedDurationDelta.hour,
                    minutes=plannedDurationDelta.minute,
                    seconds=plannedDurationDelta.second)
            plannedDownDurationStr = str(plannedDownDurationDelta)
            plannedDurationFormattedStr = DurationCalculatorFormatted1(durationStr=plannedDownDurationStr)
            # planned down duration end

            # Unplanned down duration begin
            unPlannedDownObject = list(filter(lambda x: (datetime.datetime.strftime(x["StartTime"],
                                                                                    gs.OEE_OutputDateTimeFormat) == downDateStr and
                                                         x["DownTimeCode"] == ""), downtimereport))

            TempPlannedDownObject = list(filter(lambda x: (datetime.datetime.strftime(x["StartTime"],
                                                                                      gs.OEE_OutputDateTimeFormat) == downDateStr and
                                                           x["DownTimeCode"] != ""), downtimereport))

            for plannedObj in TempPlannedDownObject:
                categoryList = list(filter(lambda x: (x["DownCode"] == plannedObj["DownTimeCode"]), DownTimeDocument))
                if len(categoryList) > 0:
                    if categoryList[0]["Category"] == "UnPlanned DownTime":
                        unPlannedDownObject.append(plannedObj)

            unPlannedDownDurationDelta = datetime.timedelta()
            for durationTime in unPlannedDownObject:
                unPlannedDurationTimeStr = durationTime["Duration"]
                unPlannedDurationDelta = datetime.datetime.strptime(unPlannedDurationTimeStr, gs.OEE_JsonTimeFormat)
                unPlannedDownDurationDelta = unPlannedDownDurationDelta + datetime.timedelta(
                    hours=unPlannedDurationDelta.hour,
                    minutes=unPlannedDurationDelta.minute,
                    seconds=unPlannedDurationDelta.second)
            unPlannedDownDurationStr = str(unPlannedDownDurationDelta)
            unPlannedDurationFormattedStr = DurationCalculatorFormatted1(durationStr=unPlannedDownDurationStr)
            # Unplanned down duration end

            # Running duration begin
            runningObject = list(filter(lambda x: (datetime.datetime.strftime(x["StartTime"],
                                                                              gs.OEE_OutputDateTimeFormat) == downDateStr),
                                        runtimereport))

            totalRunningDurationDelta = datetime.timedelta()
            for durationTime in runningObject:
                runningDurationTimeStr = durationTime["Duration"]
                runningDurationDelta = datetime.datetime.strptime(runningDurationTimeStr,
                                                                  gs.OEE_JsonTimeFormat)
                totalRunningDurationDelta = totalRunningDurationDelta + datetime.timedelta(
                    hours=runningDurationDelta.hour,
                    minutes=runningDurationDelta.minute,
                    seconds=runningDurationDelta.second)
            totalRunningDurationStr = str(totalRunningDurationDelta)
            totalRunningDurationFormattedStr = DurationCalculatorFormatted1(durationStr=totalRunningDurationStr)
            # Running duration end

            machineRunning = datetime.datetime.strptime(totalRunningDurationStr, gs.OEE_OutputTimeFormat)
            plannedDownTime = datetime.datetime.strptime(plannedDownDurationStr, gs.OEE_OutputTimeFormat)
            unPlannedDownTime = datetime.datetime.strptime(unPlannedDownDurationStr, gs.OEE_OutputTimeFormat)
            totalDownTime = datetime.datetime.strptime(totalDownDurationStr, gs.OEE_OutputTimeFormat)

            dateWiseData = {
                "sno": index,
                "date": downDateStr,
                "machineRunningFormatted": totalRunningDurationFormattedStr,
                "machineRunning": "{}.{}".format(machineRunning.hour, machineRunning.minute),
                "plannedDownTimeFormatted": plannedDurationFormattedStr,
                "plannedDownTime": "{}.{}".format(plannedDownTime.hour, plannedDownTime.minute),
                "unPlannedDownTimeFormatted": unPlannedDurationFormattedStr,
                "unPlannedDownTime": "{}.{}".format(unPlannedDownTime.hour, unPlannedDownTime.minute),
                "totalDownTimeFormatted": totalDurationFormattedStr,
                "totalDownTime": "{}.{}".format(totalDownTime.hour, totalDownTime.minute),
                "availability": "90"
            }
            datewisereportList.append(dateWiseData)

        # Final Result Object
        returnData = {
            "chartdetails": colorJson,
            "data": downdatareportList,
            "datewise": datewisereportList
        }

        jsonResponse = json.dumps(returnData, indent=4)
        return HttpResponse(jsonResponse, "application/json")
