import datetime
import os
import sys
import threading
import time
from App.OPCUA.ResultFormatter import DurationCalculatorFormatted
from App.OPCUA.index import readCalculation_file, writeCalculation_file, readDownReasonCodeFile, readAvailabilityFile, \
    WriteAvailabilityFile, readQualityCategory, readProductionFile, writeProductionFile
from MongoDB_Main import Document as Doc


def downTimeReasonUpdater():
    # Read DownCodeReason Json File
    reasonCodeList = readDownReasonCodeFile()
    # Read CalculationData Json File
    readCalculationDataJson = readCalculation_file()

    RecycleTime = int(readCalculationDataJson["RecycleTime"])
    downTimeDoc: list = Doc().getDowntimeDocument(RecycleTime)

    result = {
        "TotalDownTime": "",
        "TotalDownTImeFormatted": "",
        "TotalPlanned": "",
        "TotalPlannedFormatted": "",
        "TotalUnplanned": "",
        "TotalUnplannedFormatted": "",
        "PlannedDetails": []
    }
    unPlannedList = list(filter(lambda x: (x["DownTimeCode"] == ""), downTimeDoc))
    PlannedList = list(filter(lambda x: (x["DownTimeCode"] != ""), downTimeDoc))

    totalUnPlannedDuration = datetime.timedelta()
    for doc in unPlannedList:
        docUnplannedDuration = datetime.datetime.strptime(doc["Duration"], "%H:%M:%S.%f")
        totalUnPlannedDuration = totalUnPlannedDuration + datetime.timedelta(hours=docUnplannedDuration.hour,
                                                                             minutes=docUnplannedDuration.minute,
                                                                             seconds=docUnplannedDuration.second)
    result["TotalUnplanned"] = str(totalUnPlannedDuration)
    result["TotalUnplannedFormatted"] = DurationCalculatorFormatted(str(totalUnPlannedDuration))

    reasonCodes = (list(str(x["DownTimeCode"]) for x in PlannedList))
    reasonCodesList = (list(set(reasonCodes)))
    plannedDocumentList = []
    totalPlannedTime = datetime.timedelta()
    for reasonCode in reasonCodesList:
        totalUnPlannedDuration = datetime.timedelta(hours=0, minutes=0, seconds=0, microseconds=0)
        reasonCodeData = list(filter(lambda x: (str(x["DownTimeCode"]) == reasonCode), PlannedList))
        for doc in reasonCodeData:
            docPlannedDuration = datetime.datetime.strptime(doc["Duration"], "%H:%M:%S.%f")
            totalUnPlannedDuration = totalUnPlannedDuration + datetime.timedelta(hours=docPlannedDuration.hour,
                                                                                 minutes=docPlannedDuration.minute,
                                                                                 seconds=docPlannedDuration.second)

        reasonCodeDoc = list(filter(lambda x: (str(x["DownCode"]) == reasonCode), reasonCodeList))
        PlannedDocument = {
            "DownCode": str(reasonCode),
            "DownReasons": reasonCodeDoc[0]["DownCodeReason"],
            "color": reasonCodeDoc[0]["color"],
            "ActiveHours": str(totalUnPlannedDuration),
            "FormattedActiveHours": DurationCalculatorFormatted(str(totalUnPlannedDuration))
        }
        plannedDocumentList.append(PlannedDocument)
        totalPlannedTime = totalPlannedTime + totalUnPlannedDuration

    result["PlannedDetails"] = plannedDocumentList
    result["TotalPlanned"] = str(totalPlannedTime)
    result["TotalPlannedFormatted"] = DurationCalculatorFormatted(str(totalPlannedTime))
    TotalPlanned = datetime.datetime.strptime(result["TotalPlanned"], "%H:%M:%S")
    TotalUnplanned = datetime.datetime.strptime(result["TotalUnplanned"], "%H:%M:%S")

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

    readCalculationDataJsonNew = readCalculation_file()
    readCalculationDataJsonNew["Down"]["category"]["Planned"]["Details"] = result["PlannedDetails"]
    readCalculationDataJsonNew["Down"]["category"]["Planned"]["ActiveHours"] = result["TotalPlanned"]
    readCalculationDataJsonNew["Down"]["category"]["Planned"]["FormattedActiveHours"] = result["TotalPlannedFormatted"]

    readCalculationDataJsonNew["Down"]["category"]["Unplanned"]["ActiveHours"] = result["TotalUnplanned"]
    readCalculationDataJsonNew["Down"]["category"]["Unplanned"]["FormattedActiveHours"] = result[
        "TotalUnplannedFormatted"]
    writeCalculation_file(jsonFileContent=readCalculationDataJsonNew)


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
    return TotalDuration_delta


def DurationCalculator(ActiveHours, LastUpdateTimeStamp, currentTimeStamp):
    # LastUpdateTime and Time Difference Calculation
    LastUpdateTime = datetime.datetime.strptime(LastUpdateTimeStamp, '%Y-%m-%d %H:%M:%S.%f')
    # LastUpdateTime = LastUpdateTime - datetime.timedelta(seconds=1)
    temp = str(currentTimeStamp - LastUpdateTime)

    timeDifference = temp.split('.')[0]
    t1 = datetime.datetime.strptime(ActiveHours, '%H:%M:%S')
    t2 = datetime.datetime.strptime(timeDifference, '%H:%M:%S')
    time_zero = datetime.datetime.strptime('00:00:00', '%H:%M:%S')
    activeHours = str((t1 - time_zero + t2).time())
    activeHours_str = DurationCalculatorFormatted(activeHours)
    return activeHours, activeHours_str


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

        RunningActiveHrs = datetime.datetime.strptime(readCalculationDataJson["Running"]["ActiveHours"], "%H:%M:%S")
        DownActiveHrs = datetime.datetime.strptime(readCalculationDataJson["Down"]["ActiveHours"], "%H:%M:%S")

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
        plannedDetails = list(filter(lambda x: (str(x["DownCode"]) == str(DownReasonCode)), reasonCodeList))

        if len(plannedDetails) == 0:
            ActiveHours = readCalculationDataJson["Down"]["category"]["Unplanned"]["ActiveHours"]
        else:
            ActiveHours = readCalculationDataJson["Down"]["category"]["Planned"]["ActiveHours"]
            PlannedDetailsCalculation(readCalculationDataJson, plannedDetails[0], currentTimeStamp)

        # Duration Calculator Function
        activeHours, activeHours_str = DurationCalculator(ActiveHours=ActiveHours,
                                                          LastUpdateTimeStamp=timestamp,
                                                          currentTimeStamp=currentTimeStamp)

        # Running & Down - Active Hrs Update
        if len(plannedDetails) == 0:
            readCalculationDataJson["Down"]["category"]["Unplanned"]["ActiveHours"] = activeHours
            readCalculationDataJson["Down"]["category"]["Unplanned"]["FormattedActiveHours"] = activeHours_str
        else:
            readCalculationDataJson["Down"]["category"]["Planned"]["ActiveHours"] = activeHours
            readCalculationDataJson["Down"]["category"]["Planned"]["FormattedActiveHours"] = activeHours_str

    return readCalculationDataJson


def PlannedDetailsCalculation(readCalculationDataJson, plannedDetails, currentTimeStamp):
    reasonExist = False
    timestamp = readCalculationDataJson["LastUpdatedTime"]
    activeHours = "00:00:01"
    activeHours_str = "00h 00m 01s"

    planned_object: list = readCalculationDataJson["Down"]["category"]["Planned"]["Details"]
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

    readCalculationDataJson["Down"]["category"]["Planned"]["Details"] = planned_object
    return readCalculationDataJson


def machineRunningStatus_Updater(data, ProductionPlan_Data):
    thread = threading.Thread(target=UpdateAvailabilityJsonFile, args=[data])
    thread.start()

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
    if Machine_Status == "True":
        readCalculationDataJson = productionCount_Updater(data, readCalculationDataJson, ProductionPlan_Data)
    writeCalculation_file(readCalculationDataJson)


def productionCount_Updater(data, readCalculationDataJson, ProductionPlan_Data):
    currentTime: datetime = datetime.datetime.now()
    LastUpdateTime = str(datetime.datetime.strptime(str(currentTime), '%Y-%m-%d %H:%M:%S.%f'))
    totalSecondsOfNow = datetime.timedelta(hours=currentTime.hour,
                                           minutes=currentTime.minute,
                                           seconds=currentTime.second).total_seconds()

    ProductionIdealCycleObject = list(filter(lambda x: (x["Category"] == "IDEAL_CYCLE_TIME"), ProductionPlan_Data))
    cycleTime: int = int(ProductionIdealCycleObject[0]["InSeconds"])
    ProductionLastUpdateTime = readCalculationDataJson["ProductionLastUpdateTime"]
    # print(ProductionLastUpdateTime)
    ProductionLastUpdateTime_dt = datetime.datetime.strptime(ProductionLastUpdateTime, "%Y-%m-%d %H:%M:%S.%f")
    ProductionLastUpdateTime_Seconds = datetime.timedelta(hours=ProductionLastUpdateTime_dt.hour,
                                                          minutes=ProductionLastUpdateTime_dt.minute,
                                                          seconds=ProductionLastUpdateTime_dt.second).total_seconds()
    difference = totalSecondsOfNow - ProductionLastUpdateTime_Seconds
    print("IDEAL-TIME Difference:", difference)

    if difference >= cycleTime:

        readCalculationDataJson["ProductionLastUpdateTime"] = LastUpdateTime
        QC = data["QualityCode"]
        # read the QualityCategory File
        qualityCategory = readQualityCategory()
        qualityDoc = list(filter(lambda x: (str(x["qualityCode"]) == str(QC)), qualityCategory))

        ''' Future Implementations'''
        # Have to change the CalculationData.json for Multiple categories in QualityCode
        if len(qualityDoc) == 0:
            readCalculationDataJson["badCount"] = readCalculationDataJson["badCount"] + 1
            writeProductionLog(QC=QC, category="bad", count=1, currentTime=currentTime)
        else:
            writeProductionLog(QC=QC, category=qualityDoc[0]["category"], count=1, currentTime=currentTime)
            if qualityDoc[0]["category"] == "good":
                readCalculationDataJson["goodCount"] = readCalculationDataJson["goodCount"] + 1
            else:
                readCalculationDataJson["badCount"] = readCalculationDataJson["badCount"] + 1

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
    UpdatedTime = datetime.datetime.strptime(timestamp_str, '%H:%M:%S')
    result = datetime.timedelta(hours=UpdatedTime.hour,
                                minutes=UpdatedTime.minute,
                                seconds=UpdatedTime.second).total_seconds()
    return result


def UpdateAvailabilityJsonFile(parameter):
    timestamp = datetime.datetime.now()
    StartTime = timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")
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
        tempStartTime_datetime = datetime.datetime.strptime(str(tempStartTime), '%Y-%m-%d %H:%M:%S.%f')

        tempDuration = str(tempEndTime - tempStartTime_datetime)
        currentCycleDoc["StopTime"] = str(tempEndTime)
        currentCycleDoc["Duration"] = str(tempDuration)
        currentCycleDoc["Cycle"] = "Closed"
        availabilityJson[currentCycleIndex] = currentCycleDoc

    returnObject = {
        "availabilityJson": availabilityJson,
        "cycleDocumentIsAvailable": cycleDocumentIsAvailable
    }

    return returnObject
