import datetime
import json
import App.globalsettings as gs
from rest_framework.views import APIView
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse

from App.CNC_Calculation.APQ import AvailabilityCalculation
from App.OPCUA.index import readCalculation_file
from MongoDB_Main import Document as Doc
from App.CNC_Calculation.MachineApi import MachineApi
from App.OPCUA.ResultFormatter import DurationCalculatorFormatted, DurationCalculatorFormatted1


class getmachineid(APIView):
    @staticmethod
    def get(request):
        readCalculationDataJson = readCalculation_file()

        defaultData = {
            "machineID": readCalculationDataJson["MachineId"]
        }
        jsonResponse = json.dumps(defaultData, indent=4)
        return HttpResponse(jsonResponse, "application/json")

# class getproductionreport(APIView):
#     @staticmethod
#     def get(request):
#         fromdate = request.GET.get("fromDate")
#         todate = request.GET.get("toDate")
#
#         colorJson = [
#             {
#                 "name": "good",
#                 "color": "#68C455",
#                 "showAxis": "true",
#                 "leftSide": "false"
#             },
#             {
#                 "name": "bad",
#                 "color": "#F8425F",
#                 "showAxis": "true",
#                 "leftSide": "false"
#             },
#             {
#                 "name": "totalproduction",
#                 "color": "#7D30FA",
#                 "showAxis": "true",
#                 "leftSide": "false"
#             }]
#
#         fromDate = datetime.datetime.strptime(fromdate, gs.OEE_MongoDBDateTimeFormat)
#         toDate = datetime.datetime.strptime(todate, gs.OEE_MongoDBDateTimeFormat)
#
#         productionreport = MachineApi.getProductionReport(MachineID="MID-01", fromdate=fromDate, todate=toDate)
#
#         productionreportlist = []
#         for index, prodObj in enumerate(productionreport):
#             data = {
#                 "sno": str(index + 1),
#                 "date": prodObj["Timestamp"],
#                 "shiftCode": prodObj["shiftID"],
#                 "operatorCode": prodObj["operatorID"],
#                 "jobCode": prodObj["jobID"],
#                 "plannedProductionTime": prodObj["running"],
#                 "machineutilizeTime": prodObj["running"]["activeHours"],
#                 "plannedProductionTimeFormatted": prodObj["oee"]["scheduled"]["runTime"],
#                 "machineutilizeTimeFormatted": prodObj["oee"]["scheduled"]["runTime"],
#                 "availabilityRate": prodObj["oee"]["availability"],
#                 "performanceRate": prodObj["oee"]["performance"],
#                 "oee": prodObj["oee"]["oee"],
#                 "expected": prodObj["oee"]["scheduled"]["expectedCount"],
#                 "good": prodObj["oee"]["fullfiled"]["good"],
#                 "bad": prodObj["oee"]["fullfiled"]["bad"],
#                 "totalProduction": prodObj["oee"]["fullfiled"]["totalProduced"],
#             }
#             productionreportlist.append(data)
#
#         returnData = {
#             "chartdetails": colorJson,
#             "data": productionreportlist
#         }
#
#         jsonResponse = json.dumps(returnData, indent=4)
#         print(jsonResponse)
#         return HttpResponse(jsonResponse, "application/json")
#
#


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
                "showAxis": "True",
                "leftSide": "True"
            },
            {
                "name": "performance",
                "color": "#F8425F",
                "showAxis": "False",
                "leftSide": "False"
            },
            {
                "name": "quality",
                "color": "#68C455",
                "showAxis": "False",
                "leftSide": "False"
            },
            {
                "name": "oee",
                "color": "#7D30FA",
                "showAxis": "True",
                "leftSide": "False"
            }
        ]

        oeereport = MachineApi.getOeeReport(fromdate=fromDate)
        ProductionPlan = oeereport["ProductionPlan_Data"]

        targetList = list(filter(lambda x: (x["Category"] == "TARGET_OEE"), ProductionPlan))
        productionList = list(filter(lambda x: (x["Category"] == "PRODUCTION_PLAN_TIME"), ProductionPlan))
        standardCycleList = list(filter(lambda x: (x["Category"] == "IDEAL_CYCLE_TIME"), ProductionPlan))

        targetPercent = targetList[0]["InSeconds"]
        productionTime = productionList[0]["InSeconds"]
        standardCycleTime = standardCycleList[0]["InSeconds"]

        DownTimeDocument = Doc().DB_Read(col="DownTimeCode")
        downtimereport = MachineApi.getDownTimeReport(fromdate=fromDate, todate=toDate, status="Down")

        # Unplanned down duration begin
        unPlannedDownObject = list(filter(lambda x: (datetime.datetime.strftime(x["StartTime"],
                                                                                gs.OEE_OutputDateTimeFormat) == fromdate and
                                                     x["DownTimeCode"] == ""), downtimereport))

        TempPlannedDownObject = list(filter(lambda x: (datetime.datetime.strftime(x["StartTime"],
                                                                                  gs.OEE_OutputDateTimeFormat) == fromdate and
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
            unPlannedDownDurationDelta = unPlannedDownDurationDelta + datetime.timedelta(hours=unPlannedDurationDelta.hour,
                                                                                         minutes=unPlannedDurationDelta.minute,
                                                                                         seconds=unPlannedDurationDelta.second)
        # Unplanned down duration end
        
        Production_Planned_Time = float(productionTime)
        Total_Unplanned_Downtime = float(unPlannedDownDurationDelta.total_seconds())
        Machine_Utilized_Time: float = Production_Planned_Time - Total_Unplanned_Downtime
        availability = AvailabilityCalculation(Machine_Utilized_Time=Machine_Utilized_Time,
                                               Production_Planned_Time=Production_Planned_Time)



        # oeereportlist = []
        # for index, downObj in enumerate(oeereport):
        #     data = {
        #         "sno": str(index + 1),
        #         "date": oeeObj["Timestamp"],
        #         "target": oeeObj["oee"]["targetOee"],
        #         "availability": oeeObj["oee"]["availability"],
        #         "performance": oeeObj["oee"]["performance"],
        #         "quality": oeeObj["oee"]["quality"],
        #         "oee": oeeObj["oee"]["oee"]
        #     }
        #     oeereportlist.append(data)
        #
        # returnData = {
        #     "chartdetails": colorJson,
        #     "data": oeereportlist
        # }
        #
        # jsonResponse = json.dumps(returnData, indent=4)

        # print(jsonResponse)
        return HttpResponse("jsonResponse", "application/json")



class getdowntimereport(APIView):
    @staticmethod
    def get(request):
        DownTimeDocument = Doc().DB_Read(col="DownTimeCode")
        colorJson = [
            {
                "name": "Planned Downtime",
                "color": "#7D30FA",
                "showAxis": "true",
                "leftSide": "false"
            },
            {
                "name": "Unplanned Downtime",
                "color": "#F8425F",
                "showAxis": "true",
                "leftSide": "false"
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
            category = "Unplanned Downtime" if len(categoryList) == 0 else categoryList[0]["Category"]
            percentage = "80"
            totalDurationDelta = datetime.timedelta()

            for durationTime in downObject:
                durationTimeStr = durationTime["Duration"]
                durationDelta = datetime.datetime.strptime(durationTimeStr, gs.OEE_JsonTimeFormat)
                totalDurationDelta = totalDurationDelta + datetime.timedelta(hours=durationDelta.hour,
                                                                             minutes=durationDelta.minute,
                                                                             seconds=durationDelta.second)

            totalDurationStr = str(totalDurationDelta)
            totalDurationFormattedStr = DurationCalculatorFormatted1(durationStr=totalDurationStr)
            downId = "0" if downId == "" else downId
            data = {
                "sno": str(index),
                "downId": downId,
                "downName": downName,
                "downDescription": downName,
                "category": category,
                "totalDownTimeFormatted": totalDurationFormattedStr,
                "totalDownTime": totalDurationStr,
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
            totalDownObject = list(filter(lambda x: (datetime.datetime.strftime(x["StartTime"],
                                                                                gs.OEE_OutputDateTimeFormat) == downDateStr), downtimereport))
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
                                                                                      gs.OEE_OutputDateTimeFormat) == downDateStr and x["DownTimeCode"] != ""), downtimereport))

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
                plannedDownDurationDelta = plannedDownDurationDelta + datetime.timedelta(hours=plannedDurationDelta.hour,
                                                                                       minutes=plannedDurationDelta.minute,
                                                                                       seconds=plannedDurationDelta.second)
            plannedDownDurationStr = str(plannedDownDurationDelta)
            plannedDurationFormattedStr = DurationCalculatorFormatted1(durationStr=plannedDownDurationStr)
            # planned down duration end

            # Unplanned down duration begin
            unPlannedDownObject = list(filter(lambda x: (datetime.datetime.strftime(x["StartTime"],
                                                                                    gs.OEE_OutputDateTimeFormat) == downDateStr and x["DownTimeCode"] == ""), downtimereport))

            TempPlannedDownObject = list(filter(lambda x: (datetime.datetime.strftime(x["StartTime"],
                                                                                      gs.OEE_OutputDateTimeFormat) == downDateStr and x["DownTimeCode"] != ""), downtimereport))

            for plannedObj in TempPlannedDownObject:
                categoryList = list(filter(lambda x: (x["DownCode"] == plannedObj["DownTimeCode"]), DownTimeDocument))
                if len(categoryList) > 0:
                    if categoryList[0]["Category"] == "UnPlanned DownTime":
                        unPlannedDownObject.append(plannedObj)

            unPlannedDownDurationDelta = datetime.timedelta()
            for durationTime in unPlannedDownObject:
                unPlannedDurationTimeStr = durationTime["Duration"]
                unPlannedDurationDelta = datetime.datetime.strptime(unPlannedDurationTimeStr, gs.OEE_JsonTimeFormat)
                unPlannedDownDurationDelta = unPlannedDownDurationDelta + datetime.timedelta(hours=unPlannedDurationDelta.hour,
                                                                                         minutes=unPlannedDurationDelta.minute,
                                                                                         seconds=unPlannedDurationDelta.second)
            unPlannedDownDurationStr = str(unPlannedDownDurationDelta)
            unPlannedDurationFormattedStr = DurationCalculatorFormatted1(durationStr=unPlannedDownDurationStr)
            # Unplanned down duration end

            # Running duration begin
            runningObject = list(filter(lambda x: (datetime.datetime.strftime(x["StartTime"],
                                                                              gs.OEE_OutputDateTimeFormat) == downDateStr), runtimereport))


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

            dateWiseData = {
                "sno": str(index),
                "date": downDateStr,
                "machineRunningFormatted": totalRunningDurationFormattedStr,
                "machineRunning": totalRunningDurationStr,
                "plannedDownTimeFormatted": plannedDurationFormattedStr,
                "plannedDownTime": plannedDownDurationStr,
                "unPlannedDownTimeFormatted": unPlannedDurationFormattedStr,
                "unPlannedDownTime": unPlannedDownDurationStr,
                "totalDownTimeFormatted": totalDurationFormattedStr,
                "totalDownTime": totalDownDurationStr,
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
