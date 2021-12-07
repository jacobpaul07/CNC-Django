import datetime
import os
import sys
import threading
import time

from App.OPCUA.ResultFormatter import DurationCalculatorFormatted, productionCount_DBUpdater, productionCount_Log
from App.OPCUA.index import readCalculation_file, writeCalculation_file, readDownReasonCodeFile, readAvailabilityFile, \
    WriteAvailabilityFile, readQualityCategory, readProductionFile, writeProductionFile
from MongoDB_Main import Document as Doc
import App.globalsettings as gs


def downTimeParticularTimeDataUpdater(reasonCodeList, calculationData, availabilityJson, specificDate: datetime):
    try:

        readCalculationDataJson = calculationData
        recycleHour = int(readCalculationDataJson["RecycleTime"])
        downTimeDoc: list = Doc().getDowntimeDocumentForSpecificDate(RecycledHour=recycleHour,
                                                                     specificDate=specificDate)

        result = {
            "TotalDownTime": "",
            "TotalDownTImeFormatted": "",
            "TotalPlanned": "",
            "TotalPlannedFormatted": "",
            "TotalUnplanned": "",
            "TotalUnplannedFormatted": "",
            "PlannedDetails": [],
            "UnplannedDetails": []
        }

        # Only For Summary
        unPlannedList = list(filter(lambda x: (x["DownTimeCode"] == ""), downTimeDoc))
        PlannedList = list(filter(lambda x: (x["DownTimeCode"] != ""), downTimeDoc))

        totalUnPlannedDuration = datetime.timedelta()
        for doc in unPlannedList:
            if doc["Duration"] != "":
                docUnplannedDuration = datetime.datetime.strptime(doc["Duration"], gs.OEE_JsonTimeFormat)
                totalUnPlannedDuration = totalUnPlannedDuration + datetime.timedelta(hours=docUnplannedDuration.hour,
                                                                                     minutes=docUnplannedDuration.minute,
                                                                                     seconds=docUnplannedDuration.second)
        result["TotalUnplanned"] = str(totalUnPlannedDuration)
        result["TotalUnplannedFormatted"] = DurationCalculatorFormatted(str(totalUnPlannedDuration))

        reasonCodes = (list(str(x["DownTimeCode"]) for x in PlannedList))
        reasonCodesList = (list(set(reasonCodes)))
        plannedDocumentList = []
        UnplannedDocumentList = []
        totalPlannedTime = datetime.timedelta()
        totalUnPlannedTime = datetime.timedelta()
        for reasonCode in reasonCodesList:
            totalUnPlannedDuration = datetime.timedelta(hours=0, minutes=0, seconds=0, microseconds=0)
            reasonCodeData = list(filter(lambda x: (str(x["DownTimeCode"]) == reasonCode), PlannedList))
            for doc in reasonCodeData:
                if doc["Duration"] != "":
                    docPlannedDuration = datetime.datetime.strptime(str(doc["Duration"]), "%H:%M:%S.%f")
                    totalUnPlannedDuration = totalUnPlannedDuration + datetime.timedelta(
                        hours=docPlannedDuration.hour,
                        minutes=docPlannedDuration.minute,
                        seconds=docPlannedDuration.second)

            plannedReasonCodeDoc = list(filter(lambda x: (str(x["DownCode"]) == reasonCode and
                                                          str(x["Category"]) == "Planned DownTime"), reasonCodeList))

            unPlannedReasonCodeDoc = list(filter(lambda x: (str(x["DownCode"]) == reasonCode and
                                                            str(x["Category"]) == "UnPlanned DownTime"), reasonCodeList))

            if len(plannedReasonCodeDoc) > 0:
                PlannedDocument = {
                    "DownCode": str(reasonCode),
                    "DownReasons": plannedReasonCodeDoc[0]["DownCodeReason"],
                    "color": plannedReasonCodeDoc[0]["color"],
                    "ActiveHours": str(totalUnPlannedDuration),
                    "FormattedActiveHours": DurationCalculatorFormatted(str(totalUnPlannedDuration))
                }
                plannedDocumentList.append(PlannedDocument)
                totalPlannedTime = totalPlannedTime + totalUnPlannedDuration

            else:
                UnplannedDocument = {
                    "DownCode": str(reasonCode),
                    "DownReasons": unPlannedReasonCodeDoc[0]["DownCodeReason"],
                    "color": unPlannedReasonCodeDoc[0]["color"],
                    "ActiveHours": str(totalUnPlannedDuration),
                    "FormattedActiveHours": DurationCalculatorFormatted(str(totalUnPlannedDuration))
                }
                UnplannedDocumentList.append(UnplannedDocument)
                totalUnPlannedTime = totalUnPlannedTime + totalUnPlannedDuration

        result["UnplannedDetails"] = UnplannedDocumentList
        result["PlannedDetails"] = plannedDocumentList
        result["TotalPlanned"] = str(totalPlannedTime)
        result["TotalPlannedFormatted"] = DurationCalculatorFormatted(str(totalPlannedTime))
        result["TotalUnplanned"] = str(totalUnPlannedTime)
        result["TotalUnplannedFormatted"] = DurationCalculatorFormatted(str(totalUnPlannedTime))
        TotalPlanned = datetime.datetime.strptime(result["TotalPlanned"], gs.OEE_OutputTimeFormat)
        TotalUnplanned = datetime.datetime.strptime(result["TotalUnplanned"], gs.OEE_OutputTimeFormat)

        TotalPlannedDelta = datetime.timedelta(hours=TotalPlanned.hour,
                                               minutes=TotalPlanned.minute,
                                               seconds=TotalPlanned.second)
        TotalUnplannedDelta = datetime.timedelta(hours=TotalUnplanned.hour,
                                                 minutes=TotalUnplanned.minute,
                                                 seconds=TotalUnplanned.second)
        TotalDownTime = str(TotalPlannedDelta + TotalUnplannedDelta)
        TotalDownTImeFormatted = DurationCalculatorFormatted(TotalDownTime)

        result["TotalDownTime"] = TotalDownTime
        result["TotalDownTImeFormatted"] = TotalDownTImeFormatted

        readCalculationDataJsonNew = calculationData
        readCalculationDataJsonNew["Down"]["category"]["Planned"]["Details"] = result["PlannedDetails"]
        readCalculationDataJsonNew["Down"]["category"]["Planned"]["ActiveHours"] = result["TotalPlanned"]
        readCalculationDataJsonNew["Down"]["category"]["Planned"]["FormattedActiveHours"] = result[
            "TotalPlannedFormatted"]

        readCalculationDataJsonNew["Down"]["category"]["Unplanned"]["Details"] = result["UnplannedDetails"]
        readCalculationDataJsonNew["Down"]["category"]["Unplanned"]["ActiveHours"] = result["TotalUnplanned"]
        readCalculationDataJsonNew["Down"]["category"]["Unplanned"]["FormattedActiveHours"] = result[
            "TotalUnplannedFormatted"]

        # For full detailed
        for index, availObj in enumerate(availabilityJson):
            availStatus = availObj["Status"]
            availCycle = availObj["Cycle"]

            if availStatus != "Running" and availCycle == "Closed":
                startTime = availObj["StartTime"]
                endTime = availObj["StopTime"]

                startTime = startTime[:-3] + "000"
                endTime = endTime[:-3] + "000"

                dbDoc = list(filter(lambda x: (
                        x["Status"] == availStatus and
                        x["Cycle"] == availCycle and
                        str(x["StartTime"]) == startTime and
                        str(x["StopTime"] == endTime)), downTimeDoc))
                if len(dbDoc) > 0:
                    cDoc = dbDoc[0]
                    downCode = cDoc["DownTimeCode"]
                    docReasonCodeDoc = list(filter(lambda x: (str(x["DownCode"]) == downCode), reasonCodeList))
                    color = docReasonCodeDoc[0]["color"]
                    availabilityJson[index]["DownTimeCode"] = cDoc["DownTimeCode"]
                    availabilityJson[index]["Description"] = cDoc["Description"]
                    availabilityJson[index]["Category"] = cDoc["Category"]
                    availabilityJson[index]["color"] = color

        returnData = {
            "calculationData": readCalculationDataJsonNew,
            "availabilityJson": availabilityJson
        }
        return returnData

    except Exception as ex:
        print("Error in StandardOutput-Output.py", ex)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fileName = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fileName, exc_tb.tb_lineno)


def downTimeReasonUpdater():
    # Read DownCodeReason Json File
    reasonCodeList = readDownReasonCodeFile()
    # Read CalculationData Json File
    readCalculationDataJson = readCalculation_file()
    availabilityJson = readAvailabilityFile()
    specificDate = datetime.datetime.now()
    result = downTimeParticularTimeDataUpdater(reasonCodeList=reasonCodeList,
                                               calculationData=readCalculationDataJson,
                                               availabilityJson=availabilityJson,
                                               specificDate=specificDate)
    readCalculationDataJsonNew = result["calculationData"]
    print(readCalculationDataJsonNew)
    availabilityJsonNew = result["availabilityJson"]
    writeCalculation_file(jsonFileContent=readCalculationDataJsonNew)
    WriteAvailabilityFile(jsonContent=availabilityJsonNew)


def StartTimer():
    thread = threading.Thread(
        target=UpdateTimer,
        args=()
    )
    thread.start()


def totalDurationCalculator(t1: datetime, t2: datetime):
    t1_Delta = datetime.timedelta(hours=t1.hour,
                                  minutes=t1.minute,
                                  seconds=t1.second)

    t2_Delta = datetime.timedelta(hours=t2.hour,
                                  minutes=t2.minute,
                                  seconds=t2.second)

    TotalDuration_delta = t1_Delta + t2_Delta
    totalDurationDays = TotalDuration_delta.days
    if totalDurationDays != 0:
        TotalDuration_delta = TotalDuration_delta - datetime.timedelta(days=totalDurationDays)
    return TotalDuration_delta


def DurationCalculator(ActiveHours, LastUpdateTimeStamp, currentTimeStamp):
    try:
        # LastUpdateTime and Time Difference Calculation
        time_zero = datetime.datetime.strptime('00:00:00', gs.OEE_OutputTimeFormat)
        LastUpdateTime = datetime.datetime.strptime(LastUpdateTimeStamp, gs.OEE_JsonDateTimeFormat)
        LastUpdateTime = LastUpdateTime - datetime.timedelta(seconds=0)
        tempTime = currentTimeStamp - LastUpdateTime
        tempTimeDays = tempTime.days
        if tempTimeDays != 0:
            tempTime = tempTime - datetime.timedelta(days=tempTimeDays)
        temp = str(tempTime)
        timeDifference = temp.split('.')[0]
        t1 = datetime.datetime.strptime(ActiveHours, gs.OEE_OutputTimeFormat)
        t2 = datetime.datetime.strptime(timeDifference, gs.OEE_OutputTimeFormat)
        activeHours = str((t1 - time_zero + t2).time())
        activeHours_str = DurationCalculatorFormatted(activeHours)
        return activeHours, activeHours_str

    except Exception as ex:
        print("Error in DurationCalculator - MachineStatus.py", ex)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)


def UpdateTimer():
    try:
        currentTimeStamp = datetime.datetime.now()
        ''' Read CalculationData.json '''
        readCalculationDataJson = readCalculation_file()
        machine_Status = readCalculationDataJson["MachineStatus"]
        timestamp = readCalculationDataJson["LastUpdatedTime"]
        # Check the machine Status

        if machine_Status == "True":
            ActiveHours = readCalculationDataJson["Running"]["ActiveHours"]
        else:
            ActiveHours = readCalculationDataJson["Down"]["ActiveHours"]

        # Duration Calculator Function
        activeHours, activeHours_str = DurationCalculator(ActiveHours=ActiveHours,
                                                          LastUpdateTimeStamp=timestamp,
                                                          currentTimeStamp=currentTimeStamp)

        # Running & Down - Active Hrs Update
        if machine_Status == "True":
            readCalculationDataJson["Running"]["ActiveHours"] = activeHours
            readCalculationDataJson["Running"]["FormattedActiveHours"] = activeHours_str
        else:
            readCalculationDataJson["Down"]["ActiveHours"] = activeHours
            readCalculationDataJson["Down"]["FormattedActiveHours"] = activeHours_str
            readCalculationDataJson = PlannedUnplannedCalculation(readCalculationDataJson, currentTimeStamp)

        RunningActiveHrs = datetime.datetime.strptime(readCalculationDataJson["Running"]["ActiveHours"],
                                                      gs.OEE_OutputTimeFormat)
        DownActiveHrs = datetime.datetime.strptime(readCalculationDataJson["Down"]["ActiveHours"],
                                                   gs.OEE_OutputTimeFormat)

        # Total Duration Calculator Function
        TotalDuration = totalDurationCalculator(t1=RunningActiveHrs, t2=DownActiveHrs)
        readCalculationDataJson["TotalDuration"] = str(TotalDuration)
        readCalculationDataJson["LastUpdatedTime"] = str(currentTimeStamp)
        writeCalculation_file(jsonFileContent=readCalculationDataJson)

    except Exception as ex:
        print("Error in UpdateTimer - MachineStatus.py", ex)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

    time.sleep(1)

    thread = threading.Thread(
        target=StartTimer,
        args=()
    )
    thread.start()


def PlannedUnplannedCalculation(readCalculationDataJson, currentTimeStamp):
    timestamp = readCalculationDataJson["LastUpdatedTime"]
    DownReasonCode = readCalculationDataJson["DownTimeReasonCode"]
    if DownReasonCode != "0" and DownReasonCode != "":
        reasonCodeList = readDownReasonCodeFile()
        plannedDetails = list(filter(lambda x: (str(x["DownCode"]) == str(DownReasonCode) and
                                                str(x["Category"]) == "Planned DownTime"), reasonCodeList))

        unPlannedDetails = list(filter(lambda x: (str(x["DownCode"]) == str(DownReasonCode) and
                                                  str(x["Category"]) == "UnPlanned DownTime"), reasonCodeList))

        if len(unPlannedDetails) > 0:
            flag = "UnPlanned"
            ActiveHours = readCalculationDataJson["Down"]["category"]["Unplanned"]["ActiveHours"]
            PlannedDetailsCalculation(readCalculationDataJson, unPlannedDetails[0], currentTimeStamp, flag)
        elif len(plannedDetails) > 0:
            flag = "Planned"
            ActiveHours = readCalculationDataJson["Down"]["category"]["Planned"]["ActiveHours"]
            PlannedDetailsCalculation(readCalculationDataJson, plannedDetails[0], currentTimeStamp, flag)
        else:
            ActiveHours = readCalculationDataJson["Down"]["category"]["Unplanned"]["ActiveHours"]
            UnknownDetailsCalculation(readCalculationDataJson, currentTimeStamp)

        # Duration Calculator Function
        activeHours, activeHours_str = DurationCalculator(ActiveHours=ActiveHours,
                                                          LastUpdateTimeStamp=timestamp,
                                                          currentTimeStamp=currentTimeStamp)

        # Running & Down - Active Hrs Update
        if len(plannedDetails) > 0:
            readCalculationDataJson["Down"]["category"]["Planned"]["ActiveHours"] = activeHours
            readCalculationDataJson["Down"]["category"]["Planned"]["FormattedActiveHours"] = activeHours_str

        else:
            readCalculationDataJson["Down"]["category"]["Unplanned"]["ActiveHours"] = activeHours
            readCalculationDataJson["Down"]["category"]["Unplanned"]["FormattedActiveHours"] = activeHours_str

    return readCalculationDataJson


def PlannedDetailsCalculation(readCalculationDataJson, plannedDetails, currentTimeStamp, flag):
    reasonExist = False
    timestamp = readCalculationDataJson["LastUpdatedTime"]
    activeHours = "00:00:01"
    activeHours_str = "00h 00m 01s"
    if flag == "Planned":
        planned_object: list = readCalculationDataJson["Down"]["category"]["Planned"]["Details"]
    else:
        planned_object: list = readCalculationDataJson["Down"]["category"]["Unplanned"]["Details"]
    for obj in planned_object:
        if str(obj["DownCode"]) == str(plannedDetails["DownCode"]):
            ActiveHrs = obj["ActiveHours"]
            activeHours, activeHours_str = DurationCalculator(ActiveHours=ActiveHrs,
                                                              LastUpdateTimeStamp=timestamp,
                                                              currentTimeStamp=currentTimeStamp)
            obj["ActiveHours"] = activeHours
            obj["FormattedActiveHours"] = activeHours_str
            reasonExist = True

    if not reasonExist:
        newPlannedObject = {
            "DownCode": str(plannedDetails["DownCode"]),
            "DownReasons": plannedDetails["DownCodeReason"],
            "color": plannedDetails["color"],
            "ActiveHours": activeHours,
            "FormattedActiveHours": activeHours_str
        }
        planned_object.append(newPlannedObject)

    if flag == "Planned":
        readCalculationDataJson["Down"]["category"]["Planned"]["Details"] = planned_object
    else:
        readCalculationDataJson["Down"]["category"]["Unplanned"]["Details"] = planned_object

    return readCalculationDataJson


def UnknownDetailsCalculation(readCalculationDataJson, currentTimeStamp):
    reasonExist = False
    timestamp = readCalculationDataJson["LastUpdatedTime"]
    activeHours = "00:00:01"
    activeHours_str = "00h 00m 01s"

    unplanned_object: list = readCalculationDataJson["Down"]["category"]["Unplanned"]["Details"]

    for obj in unplanned_object:
        if str(obj["DownCode"]) == "Unplanned":
            ActiveHrs = obj["ActiveHours"]
            activeHours, activeHours_str = DurationCalculator(ActiveHours=ActiveHrs,
                                                              LastUpdateTimeStamp=timestamp,
                                                              currentTimeStamp=currentTimeStamp)
            obj["ActiveHours"] = activeHours
            obj["FormattedActiveHours"] = activeHours_str
            reasonExist = True

    if not reasonExist:
        newPlannedObject = {
            "DownCode": "Unplanned",
            "DownReasons": "Unplanned",
            "color": "#bc07ed",
            "ActiveHours": activeHours,
            "FormattedActiveHours": activeHours_str
        }
        unplanned_object.append(newPlannedObject)

    readCalculationDataJson["Down"]["category"]["Unplanned"]["Details"] = unplanned_object
    return readCalculationDataJson


def machineRunningStatus_Updater(data, ProductionPlan_Data, currentTime):
    thread = threading.Thread(target=UpdateAvailabilityJsonFile, args=(data, currentTime))
    thread.start()

    currentDate = str(datetime.datetime.today().date())
    MachineID = data["MachineID"]
    JobID = data["JobID"]
    OperatorID = data["OperatorID"]
    ShiftID = data["ShiftID"]
    Machine_Status = data["PowerOn_Status"]
    DownTime_ReasonCode = data["DownTime_ReasonCode"]
    readCalculationDataJson = readCalculation_file()
    readCalculationDataJson["MachineId"] = MachineID
    readCalculationDataJson["jobID"] = JobID
    readCalculationDataJson["operatorID"] = OperatorID
    readCalculationDataJson["shiftID"] = ShiftID
    readCalculationDataJson["MachineStatus"] = Machine_Status
    readCalculationDataJson["DownTimeReasonCode"] = DownTime_ReasonCode
    readCalculationDataJson["CurrentDate"] = currentDate

    if Machine_Status == "True":
        readCalculationDataJson = productionCount_Updater(data, readCalculationDataJson, ProductionPlan_Data,
                                                          currentTime)
    writeCalculation_file(readCalculationDataJson)


def productionCount_Updater(data, readCalculationDataJson, ProductionPlan_Data, currentTime):
    LastUpdateTime = str(datetime.datetime.strptime(str(currentTime), gs.OEE_JsonDateTimeFormat))
    totalSecondsOfNow = datetime.timedelta(hours=currentTime.hour,
                                           minutes=currentTime.minute,
                                           seconds=currentTime.second)

    ProductionIdealCycleObject = list(filter(lambda x: (x["Category"] == "IDEAL_CYCLE_TIME"), ProductionPlan_Data))
    cycleTime: int = int(float(ProductionIdealCycleObject[0]["InSeconds"]))
    ProductionLastUpdateTime = readCalculationDataJson["ProductionLastUpdateTime"]
    # print(ProductionLastUpdateTime)
    ProductionLastUpdateTime_dt = datetime.datetime.strptime(ProductionLastUpdateTime, gs.OEE_JsonDateTimeFormat)
    ProductionLastUpdateTime_Seconds = datetime.timedelta(hours=ProductionLastUpdateTime_dt.hour,
                                                          minutes=ProductionLastUpdateTime_dt.minute,
                                                          seconds=ProductionLastUpdateTime_dt.second)
    difference = totalSecondsOfNow - ProductionLastUpdateTime_Seconds
    # print("IDEAL-TIME Difference:", abs(difference.total_seconds()))
    timeDifference = abs(difference.total_seconds())
    if timeDifference >= cycleTime:

        readCalculationDataJson["ProductionLastUpdateTime"] = LastUpdateTime
        QC = data["QualityCode"]
        # read the QualityCategory File
        qualityCategory = readQualityCategory()
        qualityDoc = list(filter(lambda x: (str(x["qualityCode"]) == str(QC)), qualityCategory))

        MachineID = readCalculationDataJson["MachineId"]
        JobID = readCalculationDataJson["jobID"]
        OperatorID = readCalculationDataJson["operatorID"]
        ShiftID = readCalculationDataJson["shiftID"]

        ''' Future Implementations'''
        # Have to change the CalculationData.json for Multiple categories in QualityCode
        if len(qualityDoc) == 0:
            readCalculationDataJson["badCount"] = readCalculationDataJson["badCount"] + 1
            writeProductionLog(QC=QC, category="bad", count=1, currentTime=currentTime)
            # function to send production count --> mongoDB
        else:
            writeProductionLog(QC=QC, category=qualityDoc[0]["category"], count=1, currentTime=currentTime)
            productionCount_Log(MID=MachineID, SID=ShiftID, JID=JobID, OID=OperatorID,
                                Category=str(qualityDoc[0]["category"]).lower(),
                                TimeStamp=currentTime, QualityCode=QC)

            if str(qualityDoc[0]["category"]).lower() == "good":
                readCalculationDataJson["goodCount"] = readCalculationDataJson["goodCount"] + 1
                currentDate = str(readCalculationDataJson["CurrentDate"])
                productionCount_DBUpdater(category="good", date=currentDate, qualityCode="1",
                                          qualityId="ID001")
            else:
                readCalculationDataJson["badCount"] = readCalculationDataJson["badCount"] + 1
                currentDate = str(readCalculationDataJson["CurrentDate"])
                productionCount_DBUpdater(category="bad", date=currentDate, qualityCode="2",
                                          qualityId="ID002")

    return readCalculationDataJson


def writeProductionLog(QC, category, count, currentTime):
    productionJson: list = readProductionFile()
    newProduction = {
        "productionTime": str(currentTime),
        "category": category,
        "count": count,
        "qualityCode": QC
    }
    productionJson.append(newProduction)
    writeProductionFile(productionJson)


def getSeconds_fromTimeDifference(timestamp_str):
    UpdatedTime = datetime.datetime.strptime(timestamp_str, gs.OEE_OutputTimeFormat)
    result = datetime.timedelta(hours=UpdatedTime.hour,
                                minutes=UpdatedTime.minute,
                                seconds=UpdatedTime.second).total_seconds()
    return result


def UpdateAvailabilityJsonFile(parameter, currentTime):
    timestamp = currentTime
    StartTime = timestamp.strftime(gs.OEE_JsonDateTimeFormat)
    # Read DownCodeReason Json File
    runningColor = "#C8F3BF"
    unPlannedColor = "#F8425F"
    availabilityJson: list = readAvailabilityFile()

    if parameter["PowerOn_Status"] == "False":
        reasonCode = parameter["DownTime_ReasonCode"]
        reasonCodeList = readDownReasonCodeFile()
        reasonCodeDoc = list(filter(lambda x: (str(x["DownCode"]) == reasonCode), reasonCodeList))

        if len(reasonCodeDoc) == 0:
            reasonCode = ""
            reasonDescription = "Unplanned"
            color = unPlannedColor
        else:
            reasonDescription = reasonCodeDoc[0]["DownCodeReason"]
            color = reasonCodeDoc[0]["color"]

        if len(availabilityJson) == 0:
            availabilityJson = [{
                "MID": parameter["MachineID"], "PowerOnStatus": "OFF", "StartTime": StartTime,
                "StopTime": "", "Duration": "", "Status": "Down", "Cycle": "Open",
                "DownTimeCode": reasonCode, "Description": reasonDescription, "Category": "", "color": color}]

            WriteAvailabilityFile(availabilityJson)
        else:
            responseObject = FindAndUpdateOpenDocument(availabilityJson=availabilityJson,
                                                       cycleStatus="Open",
                                                       runningStatus="Running",
                                                       timestamp=timestamp
                                                       )

            availabilityJson = responseObject["availabilityJson"]
            documentFound = responseObject["cycleDocumentIsAvailable"]
            if documentFound is True:
                availabilityDoc = {
                    "MID": parameter["MachineID"], "PowerOnStatus": "OFF", "StartTime": StartTime,
                    "StopTime": "", "Duration": "", "Status": "Down", "Cycle": "Open",
                    "DownTimeCode": reasonCode, "Description": reasonDescription, "Category": "", "color": color}

                availabilityJson.append(availabilityDoc)
                WriteAvailabilityFile(availabilityJson)
    else:

        if len(availabilityJson) == 0:
            availabilityJson = [{
                "MID": parameter["MachineID"], "PowerOnStatus": "ON", "StartTime": StartTime,
                "StopTime": "", "Duration": "", "Status": "Running", "Cycle": "Open",
                "DownTimeCode": "", "Description": "", "Category": "", "color": runningColor}]

            WriteAvailabilityFile(availabilityJson)
        else:

            responseObject = FindAndUpdateOpenDocument(availabilityJson=availabilityJson,
                                                       cycleStatus="Open",
                                                       runningStatus="Down",
                                                       timestamp=timestamp)

            availabilityJson = responseObject["availabilityJson"]
            documentFound = responseObject["cycleDocumentIsAvailable"]

            if documentFound is True:
                availabilityDoc = {
                    "MID": parameter["MachineID"], "PowerOnStatus": "ON", "StartTime": StartTime,
                    "StopTime": "", "Duration": "", "Status": "Running", "Cycle": "Open",
                    "DownTimeCode": "", "Description": "", "Category": "", "color": runningColor}

                availabilityJson.append(availabilityDoc)
                WriteAvailabilityFile(availabilityJson)


def FindAndUpdateOpenDocument(availabilityJson, cycleStatus, runningStatus, timestamp):
    currentCycleIndex = 0
    currentCycleDoc = None

    for i, obj in enumerate(availabilityJson):
        # obj = availabilityJson[i]
        if obj["Cycle"] == cycleStatus and obj["Status"] == runningStatus:
            currentCycleIndex = i
            currentCycleDoc = obj

    cycleDocumentIsAvailable = currentCycleDoc is not None
    if cycleDocumentIsAvailable:
        tempEndTime = timestamp
        tempStartTime = currentCycleDoc["StartTime"]
        tempStartTime_datetime = datetime.datetime.strptime(str(tempStartTime), gs.OEE_JsonDateTimeFormat)

        tempDuration = tempEndTime - tempStartTime_datetime
        tempTimeDays = tempDuration.days
        if tempTimeDays != 0:
            tempDuration = tempDuration - datetime.timedelta(days=tempTimeDays)

        tempDurationStr = str(tempDuration)

        currentCycleDoc["StopTime"] = str(tempEndTime)
        currentCycleDoc["Duration"] = str(tempDurationStr)
        currentCycleDoc["Cycle"] = "Closed"
        availabilityJson[currentCycleIndex] = currentCycleDoc

    returnObject = {
        "availabilityJson": availabilityJson,
        "cycleDocumentIsAvailable": cycleDocumentIsAvailable
    }

    return returnObject
