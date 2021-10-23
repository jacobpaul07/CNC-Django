import datetime
from MongoDB_Main import Document as Doc


def resultFormatter(Data):
    HEADERS = ["CycleStart_Status", "DownTime_ReasonCode", "DownTime_Status", "EmgStop_Status", "IdealCycleTime",
               "JobID", "MachineID", "OperatorID", "PowerOn_Status", "ProductionStart", "QualityCode", "ShiftID"]
    # Result dictionary
    result = {}
    for index, header in enumerate(HEADERS):
        result[header] = Data["value"][index]["value"]
    return result


def PowerOnStatus(Time):
    startPowerStatus = {"MID": "MD-01", "PowerOnStatus": "ON", "StartTime": Time,
                        "StopTime": "", "Duration": "", "Status": "Running", "Cycle": "Open",
                        "DownTimeCode": "", "Description": "", "Category": ""}
    return startPowerStatus


def PowerOffStatus(Time):
    stopPowerStatus = {"MID": "MD-01", "PowerOnStatus": "OFF", "StartTime": Time,
                       "StopTime": "", "Duration": "", "Status": "Down", "Cycle": "Open",
                       "DownTimeCode": "", "Description": "", "Category": ""}
    return stopPowerStatus


def dataValidation(data):
    col = "Availability"
    currentTime = datetime.datetime.now()
    if data["PowerOn_Status"] == "True":
        downOpenData = Doc().ReadDBQuery(col=col, query={"Status": "Down", "Cycle": "Open"})
        RunningOpenData = Doc().ReadDBQuery(col=col, query={"Status": "Running", "Cycle": "Open"})

        # If PreviousPowerDown is not there and PreviousPowerON is not there then do an INSERT
        if downOpenData is None and RunningOpenData is None:
            startTime = currentTime
            startPowerStatus = PowerOnStatus(startTime)
            Doc().DB_Write(col=col, data=startPowerStatus)
            return startPowerStatus

        elif downOpenData:
            print("data exists")
            tempEndTime = currentTime
            tempStartTime = downOpenData['StartTime']
            object_id = downOpenData['_id']
            tempDuration = str(tempEndTime - tempStartTime)

            updateQuery = ({"$set": {"StopTime": tempEndTime,
                                     "Duration": tempDuration,
                                     "Cycle": "Closed"}})

            Doc().UpateDBQuery(col=col, query=updateQuery, object_id=object_id)

            startPowerStatus = PowerOnStatus(tempEndTime)
            Doc().DB_Write(data=startPowerStatus, col=col)

            return startPowerStatus

    elif data["PowerOn_Status"] == "False":
        tempEndTime = currentTime
        RunningOpenData = Doc().ReadDBQuery(col=col, query={"Status": "Down", "Cycle": "Open"})
        downOpenData = Doc().ReadDBQuery(col=col, query={"Status": "Running", "Cycle": "Open"})

        if downOpenData is None and RunningOpenData is None:
            print("No data exists")
            stopPowerStatus = PowerOffStatus(tempEndTime)
            Doc().DB_Write(col=col, data=stopPowerStatus)

            return stopPowerStatus

        elif downOpenData:
            tempStartTime = downOpenData['StartTime']
            object_id = downOpenData['_id']
            tempDuration = tempEndTime - tempStartTime
            duration_temp_str = str(tempDuration)
            print(duration_temp_str)

            updateQuery = {"$set": {"StopTime": tempEndTime,
                                    "Duration": duration_temp_str,
                                    "Cycle": "Closed"}}
            Doc().UpateDBQuery(col=col, query=updateQuery, object_id=object_id)

            stopPowerStatus = PowerOffStatus(tempEndTime)
            Doc().DB_Write(data=stopPowerStatus, col=col)

            return stopPowerStatus
