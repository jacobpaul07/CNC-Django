import json
import threading
import time

from App.OPCUA.ResultFormatter import Duration_Calculator, Duration_Converter, DurationCalculatorFormatted
import datetime

from App.OPCUA.index import readCalculation_file, write_json_file, writeCalculation_file


def GenericProperty(readDB, otherDB, currentTime, path, otherPath):
    readCalculationDataJson = readCalculation_file()
    machine_Status = readCalculationDataJson["MachineStatus"]
    timestamp = readCalculationDataJson["LastUpdatedTime"]

    # Check the machine Status
    if machine_Status == "True":
        ActiveHours = readCalculationDataJson["Running"]["ActiveHours"]
    else:
        ActiveHours = readCalculationDataJson["Down"]["ActiveHours"]

    durationOld = Duration_Calculator(readDB["TotalDuration"])
    oldTimestamp = readDB["Timestamp"]
    difOldTimestamp = datetime.datetime.strptime(oldTimestamp, '%Y-%m-%d %H:%M:%S.%f')
    durationNew_Str = str(currentTime - difOldTimestamp)
    durationNew = Duration_Calculator(durationNew_Str)
    totalDur = durationOld + durationNew
    totalDuration = Duration_Converter(totalDur * 60)
    readDB["TotalDuration"] = str(totalDuration)
    readDB["Timestamp"] = str(currentTime)
    otherDB["Timestamp"] = str(currentTime)
    a_file = open(path, "w")
    json.dump(readDB, a_file, indent=4)
    b_file = open(otherPath, "w")
    json.dump(otherDB, b_file, indent=4)

    return 0


def machineStatus(returnData, Running_Json, Down_Json):
    readCalculationDataJson = readCalculation_file()
    currentTime = datetime.datetime.now()
    runningPath = "./App/JsonDataBase/Running.json"
    downPath = "./App/JsonDataBase/Down.json"

    if returnData["PowerOn_Status"] == "True":
        # readDB = Doc().ReadDBQuery(col=col, query=query)
        returnValue = GenericProperty(readDB=Running_Json,
                                      otherDB=Down_Json,
                                      currentTime=currentTime,
                                      path=runningPath,
                                      otherPath=downPath)
        return returnValue

    elif returnData["PowerOn_Status"] == "False":
        # readDB = Doc().ReadDBQuery(col="Down", query=query)
        returnValue = GenericProperty(readDB=Down_Json,
                                      otherDB=Running_Json,
                                      currentTime=currentTime,
                                      path=downPath,
                                      otherPath=runningPath)
        return returnValue


def StartTimer():

    thread = threading.Thread(
        target=UpdateTimer,
        args=()
    )
    thread.start()


def UpdateTimer():
    try:
        currentTimeStamp = datetime.datetime.now()
        readCalculationDataJson = readCalculation_file()
        machine_Status = readCalculationDataJson["MachineStatus"]
        timestamp = readCalculationDataJson["LastUpdatedTime"]

        # Check the machine Status

        if machine_Status == "True":
            ActiveHours = readCalculationDataJson["Running"]["ActiveHours"]
        else:
            ActiveHours = readCalculationDataJson["Down"]["ActiveHours"]

        # LastUpdateTime and Time Difference Calculation
        LastUpdateTime = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
        LastUpdateTime = LastUpdateTime - datetime.timedelta(seconds=1)

        temp = str(currentTimeStamp - LastUpdateTime)

        timeDifference = temp.split('.')[0]
        t1 = datetime.datetime.strptime(ActiveHours, '%H:%M:%S')
        t2 = datetime.datetime.strptime(timeDifference, '%H:%M:%S')
        time_zero = datetime.datetime.strptime('00:00:00', '%H:%M:%S')


        activeHours = str((t1 - time_zero + t2).time())
        activeHours_str = DurationCalculatorFormatted(activeHours)

        # Running & Down - Active Hrs Update

        if machine_Status == "True":
            readCalculationDataJson["Running"]["ActiveHours"] = activeHours
            readCalculationDataJson["Running"]["FormattedActiveHours"] = activeHours_str

        else:
            readCalculationDataJson["Down"]["ActiveHours"] = activeHours
            readCalculationDataJson["Down"]["FormattedActiveHours"] = activeHours_str

        RunningActiveHrs = datetime.datetime.strptime(readCalculationDataJson["Running"]["ActiveHours"], "%H:%M:%S")
        DownActiveHrs = datetime.datetime.strptime(readCalculationDataJson["Down"]["ActiveHours"], "%H:%M:%S")
        RunningActiveHrs_Delta = datetime.timedelta(hours=RunningActiveHrs.hour,
                                                    minutes=RunningActiveHrs.minute,
                                                    seconds=RunningActiveHrs.second)

        DownActiveHrs_Delta = datetime.timedelta(hours=DownActiveHrs.hour,
                                                 minutes=DownActiveHrs.minute,
                                                 seconds=DownActiveHrs.second)

        TotalDuration = RunningActiveHrs_Delta + DownActiveHrs_Delta
        readCalculationDataJson["TotalDuration"] = str(TotalDuration)
        readCalculationDataJson["LastUpdatedTime"] = str(currentTimeStamp)
        writeCalculation_file(jsonFileContent=readCalculationDataJson)
    except Exception as ex:
        print("File Error", ex)

    time.sleep(1)

    thread = threading.Thread(
        target=StartTimer,
        args=()
    )
    thread.start()


def machineRunningStatus_Updater(data):

    MachineID = data["MachineID"]
    JobID = data["JobID"]
    OperatorID = data["OperatorID"]
    ShiftID = data["ShiftID"]
    Machine_Status = data["PowerOn_Status"]

    readCalculationDataJson = readCalculation_file()
    readCalculationDataJson["MachineId"] = MachineID
    readCalculationDataJson["jobID"] = JobID
    readCalculationDataJson["operatorID"] = OperatorID
    readCalculationDataJson["shiftID"] = ShiftID
    readCalculationDataJson["MachineStatus"] = Machine_Status

    QC = data["QualityCode"]
    if QC == 1001 or QC == 1003 or QC == 1005 or QC == 1:
        readCalculationDataJson["goodCount"] = readCalculationDataJson["goodCount"] + 1

    elif QC == 1002 or QC == 1004 or QC == 1006 or QC == 2:
        readCalculationDataJson["badCount"] = readCalculationDataJson["badCount"] + 1

    writeCalculation_file(readCalculationDataJson)


def getSeconds_fromTimeDifference(timestamp_str):
    UpdatedTime = datetime.datetime.strptime(timestamp_str, '%H:%M:%S')
    result = datetime.timedelta(hours=UpdatedTime.hour,
                                minutes=UpdatedTime.minute,
                                seconds=UpdatedTime.second).total_seconds()

    return result

