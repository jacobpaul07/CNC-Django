import datetime
import json
import App.globalsettings as gs
from rest_framework.views import APIView
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse

from App.CNC_Calculation.APQ import AvailabilityCalculation, ProductionCalculation, Quality, OeeCalculator
from App.OPCUA.index import readCalculation_file
from MongoDB_Main import Document as Doc
from App.CNC_Calculation.MachineApi import MachineApi
from App.OPCUA.ResultFormatter import DurationCalculatorFormatted1, Duration_Converter_Formatted


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

        chartDetails = [
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
        ]
        params = {k: v[0] for k, v in dict(request.GET).items()}
        print(params)
        fromdate = params["fromDate"]
        todate = params["toDate"]
        mode = params["mode"] if "mode" in params else ""
        deviceID = params["deviceID"] if "deviceID" in params else ""

        fromDate = datetime.datetime.strptime(fromdate, gs.OEE_MongoDBDateTimeFormat)
        toDate = datetime.datetime.strptime(todate, gs.OEE_MongoDBDateTimeFormat)

        oeereport = MachineApi.getOeeReport(fromdate=fromDate, todate=toDate)
        availabilityDocument = Doc().Read_Availability_Document(fromDate=fromDate, toDate=toDate)

        DownTimeDocument = Doc().DB_Read(col="DownTimeCode")
        QualityDocument = Doc().Read_Productivity_Document(startDateTime=fromDate, EndDateTime=toDate)
        print("Quality Document Length", len(QualityDocument))
        productionReportList = []
        index = 0
        for currentdatereport in oeereport:
            index = index + 1
            currentDate = datetime.datetime.strftime(currentdatereport["_id"], gs.OEE_OutputDateTimeFormat)
            firstData = currentdatereport["data"]
            ProductionPlan = firstData["ProductionPlan_Data"]

            productionList = list(filter(lambda x: (x["Category"] == "PRODUCTION_PLAN_TIME"), ProductionPlan))
            productionTime = 0 if len(productionList) == 0 else float(productionList[0]["InSeconds"])
            standardCycleList = list(filter(lambda x: (x["Category"] == "IDEAL_CYCLE_TIME"), ProductionPlan))
            shiftList = list(filter(lambda x: (x["Category"] == "SHIFT"), ProductionPlan))
            standardCycleTime = 0 if len(standardCycleList) == 0 else float(standardCycleList[0]["InSeconds"])

            ''' multiple operators and Jobs are not handled, need to be implemented in future'''

            for shifts in shiftList:
                shiftName = shifts["Name"]
                duration = shifts["InSeconds"]
                shiftStartTimeStr = shifts["ShiftStartTime"]
                shiftEndTimeStr = shifts["ShiftEndTime"]
                shiftStartTime = datetime.datetime.strptime(shiftStartTimeStr, gs.OEE_ExcelDateTimeFormat)
                shiftEndTime = datetime.datetime.strptime(shiftEndTimeStr, gs.OEE_ExcelDateTimeFormat)

                shiftStartTimeTz = datetime.datetime.strptime(shiftStartTimeStr, gs.OEE_ExcelDateTimeFormat).replace(
                    tzinfo=None)
                shiftEndTimeTz = datetime.datetime.strptime(shiftEndTimeStr, gs.OEE_ExcelDateTimeFormat).replace(
                    tzinfo=None)

                shiftAvailability = list(filter(lambda x: (x["StartTime"] >= shiftStartTimeTz or
                                                           x["StopTime"] <= shiftEndTimeTz), availabilityDocument))

                shiftCode = "-" if len(shiftAvailability) == 0 else shiftAvailability[0]["SID"]
                operatorCode = "-" if len(shiftAvailability) == 0 else shiftAvailability[0]["OID"]
                jobCode = "-" if len(shiftAvailability) == 0 else shiftAvailability[0]["JID"]

                QualityDocumentList = list(filter(lambda x: (
                        shiftStartTime <= x["timeStamp"] <= shiftEndTime), QualityDocument))

                goodCountList = list(filter(lambda x: (str(x["category"]).lower() == "good"), QualityDocumentList))
                badCountList = list(filter(lambda x: (str(x["category"]).lower() == "bad"), QualityDocumentList))

                goodProductionCount = len(goodCountList)
                badProductionCount = len(badCountList)
                totalProductionCount = int(goodProductionCount + badProductionCount)

                # Unplanned down duration begin
                unPlannedDownObject = list(filter(lambda x: (x["StartTime"] >= shiftStartTimeTz and
                                                             x["StopTime"] <= shiftEndTimeTz and
                                                             x["DownTimeCode"] == "" and x["Status"] == "Down"),
                                                  shiftAvailability))

                plannedDownObject = list(filter(lambda x: (x["StartTime"] >= shiftStartTimeTz and
                                                           x["StopTime"] <= shiftEndTimeTz and
                                                           x["DownTimeCode"] != "" and x["Status"] == "Down"),
                                                shiftAvailability))

                for plannedObj in plannedDownObject:
                    categoryList = list(
                        filter(lambda x: (x["DownCode"] == plannedObj["DownTimeCode"]), DownTimeDocument))
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

                runtimereport = list(filter(lambda x: (x["Status"] == "Running"), shiftAvailability))

                totalRunningDurationDelta = datetime.timedelta()
                for durationTime in runtimereport:
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

                Production_Planned_Time = float(duration)
                Total_Unplanned_Downtime = float(unPlannedDownDurationDelta.total_seconds())
                Machine_Utilized_Time: float = Production_Planned_Time - Total_Unplanned_Downtime
                availability = AvailabilityCalculation(Machine_Utilized_Time=Machine_Utilized_Time,
                                                       Production_Planned_Time=Production_Planned_Time)

                performance = ProductionCalculation(Standard_Cycle_Time=standardCycleTime,
                                                    Total_Produced_Components=totalProductionCount,
                                                    UtilisedTime_Seconds=Machine_Utilized_Time)

                quality = Quality(goodCount=goodProductionCount, totalCount=totalProductionCount)

                oee = OeeCalculator(AvailPercent=availability, PerformPercent=performance, QualityPercent=quality)

                expectedCount: int = int(Production_Planned_Time / standardCycleTime)
                plannedProductionTime, plannedProductionTimeFormatted = Duration_Converter_Formatted(
                    Production_Planned_Time)

                data = {
                    "sno": str(index),
                    "date": str(currentDate),
                    "shiftCode": str(shiftName),
                    "operatorCode": str(operatorCode),
                    "jobCode": str(jobCode),
                    "plannedProductionTime": str(duration),
                    "machineutilizeTime": str(totalRunningDurationStr),
                    "plannedProductionTimeFormatted": str(plannedProductionTimeFormatted),
                    "machineutilizeTimeFormatted": totalRunningDurationFormattedStr,
                    "availabilityRate": str(availability),
                    "performanceRate": str(performance),
                    "qualityRate": str(quality),
                    "oee": str(oee),
                    "expected": str(expectedCount),
                    "good": str(goodProductionCount),
                    "bad": str(badProductionCount),
                    "totalProduction": str(totalProductionCount),
                }

                productionReportList.append(data)

        # Final Result Object
        returnData = {
            "chartdetails": chartDetails,
            "data": productionReportList,
        }

        jsonResponse = json.dumps(returnData, indent=4)
        return HttpResponse(jsonResponse, "application/json")


class getoeereport(APIView):
    @staticmethod
    def get(request):
        params = {k: v[0] for k, v in dict(request.GET).items()}
        print(params)
        fromdate = params["fromDate"]
        todate = params["toDate"]
        mode = params["mode"] if "mode" in params else ""
        deviceID = params["deviceID"] if "deviceID" in params else ""
        fromDate = datetime.datetime.strptime(fromdate, gs.OEE_MongoDBDateTimeFormat)
        toDate = datetime.datetime.strptime(todate, gs.OEE_MongoDBDateTimeFormat)

        heatChartDetails = [
            {
                "from": 0,
                "to": 80,
                "name": "Below 80%",
                "color": "#E18484"
            },
            {
                "from": 81,
                "to": 99,
                "name": "81% to 99%",
                "color": "#F9C464"
            },
            {
                "from": 100,
                "to": 100,
                "name": "100%",
                "color": "#83F769"
            }
        ]

        colorJson = [
            {
                "name": "target",
                "color": "#9C97A6",
                "showAxis": False,
                "leftSide": False
            },
            {
                "name": "availability",
                "color": "#00FF00",
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
        ooeHourReport = Doc().HourIntervals_Document(fromDate=fromDate, toDate=toDate, col="LogsRawBackUp")
        DownTimeDocument = Doc().DB_Read(col="DownTimeCode")
        QualityDocument = Doc().Read_Quality_Document(fromDate=fromDate, toDate=toDate)
        downtimereport = MachineApi.getDownTimeReport(fromdate=fromDate, todate=toDate, status="Down")
        oeeReportList = []
        headMapList = []
        index = 0
        for currentdatereport in oeereport:
            index = index + 1
            currentDate: datetime.datetime = currentdatereport["_id"]
            currentDateStr = datetime.datetime.strftime(currentdatereport["_id"], gs.OEE_OutputDateTimeFormat)
            firstData = currentdatereport["data"]
            ProductionPlan = firstData["ProductionPlan_Data"]

            targetList = list(filter(lambda x: (x["Category"] == "TARGET_OEE"), ProductionPlan))
            productionList = list(filter(lambda x: (x["Category"] == "PRODUCTION_PLAN_TIME"), ProductionPlan))
            standardCycleList = list(filter(lambda x: (x["Category"] == "IDEAL_CYCLE_TIME"), ProductionPlan))

            targetPercent = 0 if len(targetList) == 0 else float(targetList[0]["InSeconds"])
            productionTime = 0 if len(productionList) == 0 else float(productionList[0]["InSeconds"])
            standardCycleTime = 0 if len(standardCycleList) == 0 else float(standardCycleList[0]["InSeconds"])

            oeeReportData = oeeReportGen(fromdate=fromdate,
                                         currentDateStr=currentDateStr,
                                         QualityDocument=QualityDocument,
                                         downtimereport=downtimereport,
                                         DownTimeDocument=DownTimeDocument,
                                         productionTime=productionTime,
                                         standardCycleTime=standardCycleTime,
                                         mode="date", fromtime=0, totime=0)

            data = {
                "sno": str(index),
                "date": str(currentDateStr),
                "target": str(targetPercent),
                "availability": oeeReportData["availability"],
                "performance": oeeReportData["performance"],
                "quality": oeeReportData["quality"],
                "oee": oeeReportData["oee"]
            }
            oeeReportList.append(data)

            # Heat Map Begins Here
            fromDateTime = datetime.datetime(year=currentDate.year, month=currentDate.month, day=currentDate.day,
                                             hour=0, minute=0, second=0)
            toDatetime = datetime.datetime(year=currentDate.year, month=currentDate.month, day=currentDate.day,
                                           hour=23, minute=59, second=59)
            tempTime = fromDateTime
            while tempTime < toDatetime:
                oldTemp = tempTime
                tempTime = tempTime + datetime.timedelta(hours=1)

                if tempTime > toDatetime:
                    tempTime = toDatetime

                tmpFromDateTime = oldTemp

                ''' APQ percentage calculated for particular hour '''

                # tmpToDateTime = tempTime
                # perHourDuration = 1 * 60 * 60
                # oeeHeatMapData = oeeReportGen(fromdate=0,
                #                               currentDateStr=currentDateStr,
                #                               QualityDocument=QualityDocument,
                #                               downtimereport=downtimereport,
                #                               DownTimeDocument=DownTimeDocument,
                #                               productionTime=perHourDuration,
                #                               standardCycleTime=standardCycleTime,
                #                               mode="hour",
                #                               fromtime=tmpFromDateTime,
                #                               totime=tmpToDateTime)

                ''' APQ percentage from History '''
                oeeHeatMapData = oeeHistoryHeatMap(fromTime=tmpFromDateTime, ooeHourReport=ooeHourReport)
                heatMapTimeFormatted = tmpFromDateTime.strftime("%I %p")

                # Heat Map Ends Here
                heatmap = {
                    "date": str(currentDate.date()),
                    "time": str(heatMapTimeFormatted),
                    "target": str(targetPercent),
                    "availability": oeeHeatMapData["availability"],
                    "performance": oeeHeatMapData["performance"],
                    "quality": oeeHeatMapData["quality"],
                    "oee": oeeHeatMapData["oee"]
                }
                headMapList.append(heatmap)

        returnData = {
            "heatchartdetails": heatChartDetails,
            "chartdetails": colorJson,
            "data": oeeReportList,
            "heatmap": headMapList
        }

        jsonResponse = json.dumps(returnData, indent=4, skipkeys=True)

        return HttpResponse(jsonResponse, "application/json")


class getdowntimereport(APIView):
    @staticmethod
    def get(request):

        params = {k: v[0] for k, v in dict(request.GET).items()}
        print(params)
        fromdate = params["fromDate"]
        todate = params["toDate"]
        mode = params["mode"] if "mode" in params else ""
        deviceID = params["deviceID"] if "deviceID" in params else ""

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

        fromDate = datetime.datetime.strptime(fromdate, gs.OEE_MongoDBDateTimeFormat)
        toDate = datetime.datetime.strptime(todate, gs.OEE_MongoDBDateTimeFormat)
        oeereport = MachineApi.getOeeReport(fromdate=fromDate, todate=toDate)
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
                "totalDownTime": "{}.{:02d}".format(totalDur.hour, totalDur.minute),
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

            productionTime = 0
            for currentdatereport in oeereport:
                firstData = currentdatereport["data"]
                ProductionPlan = firstData["ProductionPlan_Data"]
                productionList = list(filter(lambda x: (x["Category"] == "PRODUCTION_PLAN_TIME"), ProductionPlan))
                productionTime = 0 if len(productionList) == 0 else float(productionList[0]["InSeconds"])

            Production_Planned_Time = float(productionTime)
            Total_Unplanned_Downtime = float(unPlannedDownDurationDelta.total_seconds())
            Machine_Utilized_Time: float = Production_Planned_Time - Total_Unplanned_Downtime
            availability = AvailabilityCalculation(Machine_Utilized_Time=Machine_Utilized_Time,
                                                   Production_Planned_Time=Production_Planned_Time)
            availability_Absolute = abs(availability)
            availability_Str = "100" if availability_Absolute > 100 else str(availability_Absolute)

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
                "availability": str(availability_Str)
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


def oeeHistoryHeatMap(fromTime, ooeHourReport):
    fromTimeFormatted = datetime.datetime(year=fromTime.year, month=fromTime.month, day=fromTime.day,
                                          hour=fromTime.hour, minute=fromTime.minute, second=fromTime.second,
                                          tzinfo=datetime.timezone.utc)
    fromTimeStr = datetime.datetime.strftime(fromTimeFormatted, gs.OEE_DateHourFormat)
    rawDbLog = list(filter(lambda x: (
            datetime.datetime.strftime(x["data"]["currentTime"], gs.OEE_DateHourFormat) == fromTimeStr), ooeHourReport))

    if len(rawDbLog) == 0:
        data = {
            "date": str(fromTime),
            "availability": str("0"),
            "performance": str("0"),
            "quality": str("0"),
            "oee": str("0")
        }

    else:
        oeeObj = rawDbLog[0]["data"]["OeeArgs"]
        availability = str(oeeObj["availability"]).replace("%", "").strip()
        performance = str(oeeObj["performance"]).replace("%", "").strip()
        quality = str(oeeObj["quality"]).replace("%", "").strip()
        oee = str(oeeObj["OeePercentage"]).replace("%", "").strip()
        data = {
            "date": str(fromTime),
            "availability": availability,
            "performance": performance,
            "quality": quality,
            "oee": oee
        }
    return data


def oeeReportGen(fromdate, currentDateStr, QualityDocument, downtimereport, DownTimeDocument, productionTime,
                 standardCycleTime, mode, fromtime, totime):
    totalProductionCount = 0
    goodProductionCount = 0

    todayProductionList = list(filter(lambda x: (x["date"] == currentDateStr), QualityDocument))
    for production in todayProductionList:
        if production["category"] == "good":
            goodProductionCount = goodProductionCount + int(production["productioncount"])
        totalProductionCount = totalProductionCount + int(production["productioncount"])

    # Unplanned down duration begin
    if mode == "date":
        unPlannedDownObject = list(filter(lambda x: (
                datetime.datetime.strftime(x["StartTime"], gs.OEE_OutputDateTimeFormat) == fromdate and
                x["DownTimeCode"] == ""), downtimereport))

        plannedDownObject = list(filter(lambda x: (
                datetime.datetime.strftime(x["StartTime"], gs.OEE_OutputDateTimeFormat) == fromdate and
                x["DownTimeCode"] != ""), downtimereport))

    else:
        unPlannedDownObject = list(filter(lambda x: (x["StartTime"] >= fromtime and
                                                     x["StopTime"] <= totime and
                                                     x["DownTimeCode"] == ""), downtimereport))

        plannedDownObject = list(filter(lambda x: (x["StartTime"] >= fromtime and
                                                   x["StopTime"] <= totime and
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
        "date": str(currentDateStr),
        "availability": str(availability),
        "performance": str(performance),
        "quality": str(quality),
        "oee": str(oee)
    }
    return data
