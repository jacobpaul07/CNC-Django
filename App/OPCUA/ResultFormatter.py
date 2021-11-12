import datetime
import json

from MongoDB_Main import Document as Doc


def resultFormatter(Data):
    HEADERS = ["CycleStart_Status", "DownTime_ReasonCode", "DownTime_Status", "EmgStop_Status", "IdealCycleTime",
               "JobID", "MachineID", "OperatorID", "PowerOn_Status", "ProductionStart", "QualityCode", "ShiftID"]
    # Result dictionary
    result = {}
    for index, header in enumerate(HEADERS):
        result[header] = Data["value"][index]["value"]
    return result


def MachineStatus(Time):
    status = {
        "MachineId": "MID-01",
        "Timestamp": Time,
        "TotalDuration": "00:00:00.00",
        "badCount": 1,
        "goodCount": 1
    }
    return status


def PowerOnStatus(Time, data):
    startPowerStatus = {"MID": data["MachineID"], "PowerOnStatus": "ON", "StartTime": Time,
                        "StopTime": "", "Duration": "", "Status": "Running", "Cycle": "Open",
                        "DownTimeCode": "", "Description": "", "Category": ""}
    return startPowerStatus


def PowerOffStatus(Time, data):
    try:
        with open("./App/JsonDataBase/DownReasonCode.json", 'r') as file:
            reasonCodeList = json.load(file)
            file.close()

        DownTimeCode = data["DownTime_ReasonCode"]
        reasonCodeData = list(filter(lambda x: (str(x["DownCode"]) == str(DownTimeCode)), reasonCodeList))
        if len(reasonCodeData) == 0:
            reasonCode = ""
            reasonDescription = ""
        else:
            reasonCode = reasonCodeData[0]["DownCode"]
            reasonDescription = reasonCodeData[0]["DownCodeReason"]

        stopPowerStatus = {"MID": data["MachineID"], "PowerOnStatus": "OFF", "StartTime": Time,
                           "StopTime": "", "Duration": "", "Status": "Down", "Cycle": "Open",
                           "DownTimeCode": reasonCode, "Description": reasonDescription, "Category": ""}

        return stopPowerStatus

    except Exception as ex:
        print('Error in ResultFormatter', ex)


def dataValidation(data: dict, currentTime):

    col = "Availability"

    if data["PowerOn_Status"] == "True":
        downOpenData = Doc().ReadDBQuery(col=col, query={"Status": "Down", "Cycle": "Open"})
        RunningOpenData = Doc().ReadDBQuery(col=col, query={"Status": "Running", "Cycle": "Open"})

        # If PreviousPowerDown is not there and PreviousPowerON is not there then do an INSERT
        if downOpenData is None and RunningOpenData is None:
            startTime = currentTime
            startPowerStatus = PowerOnStatus(Time=startTime, data=data)
            Doc().DB_Write(col=col, data=startPowerStatus)
            return startPowerStatus

        elif downOpenData:
            tempEndTime = currentTime
            tempStartTime = downOpenData['StartTime']
            object_id = downOpenData['_id']
            tempDuration = str(tempEndTime - tempStartTime)
            updateQuery = ({"$set": {"StopTime": tempEndTime,
                                     "Duration": tempDuration,
                                     "Cycle": "Closed",
                                     }})

            Doc().UpdateDBQuery(col=col, query=updateQuery, object_id=object_id)
            startPowerStatus = PowerOnStatus(Time=tempEndTime, data=data)
            Doc().DB_Write(data=startPowerStatus, col=col)

            return startPowerStatus

    elif data["PowerOn_Status"] == "False":

        tempEndTime = currentTime
        RunningOpenData = Doc().ReadDBQuery(col=col, query={"Status": "Down", "Cycle": "Open"})
        downOpenData = Doc().ReadDBQuery(col=col, query={"Status": "Running", "Cycle": "Open"})

        if downOpenData is None and RunningOpenData is None:
            stopPowerStatus = PowerOffStatus(tempEndTime, data)
            Doc().DB_Write(col=col, data=stopPowerStatus)

            return stopPowerStatus

        elif downOpenData:
            tempStartTime = downOpenData['StartTime']
            object_id = downOpenData['_id']
            tempDuration = tempEndTime - tempStartTime
            duration_temp_str = str(tempDuration)

            updateQuery = {"$set": {"StopTime": tempEndTime,
                                    "Duration": duration_temp_str,
                                    "Cycle": "Closed"}}
            Doc().UpdateDBQuery(col=col, query=updateQuery, object_id=object_id)
            stopPowerStatus = PowerOffStatus(tempEndTime, data)
            Doc().DB_Write(data=stopPowerStatus, col=col)

            return stopPowerStatus


def DurationCalculatorFormatted(durationStr):
    timeData = (durationStr.replace(":", ","))
    split_list = timeData.split(",")
    Hour = split_list[0]
    minutes = split_list[1]
    seconds = split_list[2]
    finalResult = "{0}h {1}m {2}s".format(Hour, minutes, seconds)
    return finalResult


def Duration_Calculator(durationStr):
    timeData = (durationStr.replace(":", ","))
    split_list = timeData.split(",")
    Hour = float(split_list[0])
    minutes = float(split_list[1])
    seconds = float(split_list[2])

    dur = (Hour * 60 + minutes + seconds / 60)
    duration = round(dur, 3)
    return duration


def Duration_Converter(seconds):

    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    return "%d:%02d:%02d" % (hour, minutes, seconds)


def productionCount_DBUpdater(category, date, qualityCode, qualityId):
    col = "Quality"
    query = {"date": date, "category": category}
    updateStatus = Doc().Increment_Value(col=col, incrementField="productioncount", query=query)

    if updateStatus is None:
        data = {
            "date": date,
            "productioncount": 1,
            "qualitycode": qualityCode,
            "qualityid": qualityId,
            "qualitydescription": category,
            "category": category
        }
        Doc().DB_Write(data=data, col=col)
