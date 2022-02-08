import json
import datetime
import os
import sys

from App.GenericKafkaConsumer.GenericKafkaConsume import publish_to_replication_server
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
    startPowerStatus = {"machineID": data["MachineID"], "SID": data["ShiftID"], "OID": data["OperatorID"],
                        "JID": data["JobID"], "PowerOnStatus": "ON", "StartTime": Time,
                        "StopTime": "", "Duration": "", "Status": "Running", "Cycle": "Open",
                        "DownTimeCode": "", "Description": "", "Category": "", "ReferenceID": ""}
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

        stopPowerStatus = {"machineID": data["MachineID"], "SID": data["ShiftID"], "OID": data["OperatorID"],
                           "JID": data["JobID"], "PowerOnStatus": "OFF", "StartTime": Time,
                           "StopTime": "", "Duration": "", "Status": "Down", "Cycle": "Open",
                           "DownTimeCode": reasonCode, "Description": reasonDescription, "Category": "",
                           "ReferenceID": ""}

        return stopPowerStatus

    except Exception as ex:
        print('Error in ResultFormatter', ex)


def dataValidation(data: dict, currentTime):
    col = "Availability"
    machineID = data["MachineID"]
    if data["PowerOn_Status"] == "True":
        downOpenData = Doc().ReadDBQuery(col=col, query={"Status": "Down", "Cycle": "Open", "machineID": machineID})
        RunningOpenData = Doc().ReadDBQuery(col=col,
                                            query={"Status": "Running", "Cycle": "Open", "machineID": machineID})

        # If PreviousPowerDown is not there and PreviousPowerON is not there then do an INSERT
        if downOpenData is None and RunningOpenData is None:
            startTime = currentTime
            startPowerStatus = PowerOnStatus(Time=startTime, data=data)
            Doc().DB_Write(col=col, data=startPowerStatus)
            publish_to_replication_server(collection_name=col, entry_mode="C", loaded_data=startPowerStatus,
                                          device_id=machineID, query={}, return_response=False)
            return startPowerStatus

        elif downOpenData:
            tempEndTime = currentTime
            tempStartTime = downOpenData['StartTime']
            object_id = downOpenData['_id']
            reference_id = downOpenData['ReferenceID']
            tempDuration = str(tempEndTime - tempStartTime)
            updateData = ({"$set": {"StopTime": tempEndTime,
                                    "Duration": tempDuration,
                                    "Cycle": "Closed"}})
            query = {"$and": [{"_id": object_id}, {"machineID": machineID}]}
            queryCloud = {"$and": [{"_id": reference_id}, {"machineID": machineID}]}
            Doc().UpdateDBQuery(col=col, query=query, updateData=updateData)
            publish_to_replication_server(collection_name=col, entry_mode="U", loaded_data=updateData,
                                          device_id=machineID,
                                          query=queryCloud, return_response=False)
            startPowerStatus = PowerOnStatus(Time=tempEndTime, data=data)
            Doc().DB_Write(data=startPowerStatus, col=col)
            publish_to_replication_server(collection_name=col, entry_mode="C", loaded_data=startPowerStatus,
                                          device_id=machineID, query={}, return_response=False)

            return startPowerStatus

    elif data["PowerOn_Status"] == "False":

        tempEndTime = currentTime
        RunningOpenData = Doc().ReadDBQuery(col=col, query={"Status": "Down", "Cycle": "Open", "machineID": machineID})
        downOpenData = Doc().ReadDBQuery(col=col, query={"Status": "Running", "Cycle": "Open", "machineID": machineID})

        if downOpenData is None and RunningOpenData is None:
            stopPowerStatus = PowerOffStatus(tempEndTime, data)
            Doc().DB_Write(col=col, data=stopPowerStatus)
            publish_to_replication_server(collection_name=col, entry_mode="C", loaded_data=stopPowerStatus,
                                          device_id=machineID, query={}, return_response=False)
            return stopPowerStatus

        elif data["DownTime_ReasonCode"] != RunningOpenData['DownTimeCode']:
            temp_start_time = RunningOpenData['StartTime']
            reference_id = RunningOpenData['ReferenceID']
            object_id = RunningOpenData['_id']
            temp_duration = str(currentTime - temp_start_time)
            update_data = ({"$set": {"StopTime": currentTime,
                                     "Duration": temp_duration,
                                     "Cycle": "Closed"}})
            query = {"$and": [{"_id": object_id}, {"machineID": machineID}]}
            query_cloud = {"$and": [{"_id": reference_id}, {"machineID": machineID}]}
            Doc().update_query_local_and_cloud(col=col, query=query, update_data=update_data,
                                               query_cloud=query_cloud, machine_id=machineID)
            return None

        elif downOpenData:
            tempStartTime = downOpenData['StartTime']
            object_id = downOpenData['_id']
            reference_id = downOpenData['ReferenceID']
            tempDuration = tempEndTime - tempStartTime
            duration_temp_str = str(tempDuration)

            updateData = {"$set": {"StopTime": tempEndTime,
                                   "Duration": duration_temp_str,
                                   "Cycle": "Closed"}}
            query = {"$and": [{"_id": object_id}, {"machineID": machineID}]}
            queryCloud = {"$and": [{"_id": reference_id}, {"machineID": machineID}]}

            Doc().UpdateDBQuery(col=col, query=query, updateData=updateData)
            publish_to_replication_server(collection_name=col, entry_mode="U", loaded_data=updateData,
                                          device_id=machineID,
                                          query=queryCloud, return_response=False)
            stopPowerStatus = PowerOffStatus(tempEndTime, data)
            Doc().DB_Write(data=stopPowerStatus, col=col)
            publish_to_replication_server(collection_name=col, entry_mode="C", loaded_data=stopPowerStatus,
                                          device_id=machineID, query={}, return_response=False)

            return stopPowerStatus


def DurationCalculatorFormatted(durationStr):
    timeData = (durationStr.replace(":", ","))
    split_list = timeData.split(",")
    Hour = split_list[0]
    minutes = split_list[1]
    seconds = split_list[2]
    finalResult = "{0}h {1}m {2}s".format(Hour, minutes, seconds)
    return finalResult


def DurationCalculatorFormatted1(durationStr):
    timeData = (durationStr.replace(":", ","))
    split_list = timeData.split(",")
    Hour = split_list[0]
    minutes = split_list[1]
    seconds = split_list[2]
    finalResult = "{0}h {1}m".format(Hour, minutes)
    return finalResult


def get_duration(duration, formats, separator):
    hours = int(duration / 3600)
    minutes = int(duration % 3600 / 60)
    seconds = int((duration % 3600) % 60)
    if formats == "hm":
        raw = '{:02d}:{:02d}'.format(hours, minutes)
        formatted = '{:02d}h'.format(int(hours)) + separator + '{:02d}m'.format(int(minutes))
    else:
        raw = '{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds)
        formatted = '{:02d}h'.format(int(hours)) + separator + '{:02d}m'.format(
            int(minutes)) + separator + '{:02d}s'.format(int(seconds))

    output = {"raw": raw, "formatted": formatted}

    return output


def Duration_Calculator(durationStr):
    timeData = (durationStr.replace(":", ","))
    split_list = timeData.split(",")
    Hour = float(split_list[0])
    minutes = float(split_list[1])
    seconds = float(split_list[2])

    dur = (Hour * 60 + minutes + seconds / 60)
    duration = round(dur, 3)
    return duration


def Duration_Converter_Formatted(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    raw = "%d:%02d:%02d" % (hour, minutes, seconds)
    formatted = "{}h {}m {}s".format(int(hour), int(minutes), int(seconds))

    return raw, formatted


def productionCount_DBUpdater(category, date, qualityCode, qualityId, MachineID):
    col = "Quality"
    query = {"date": date, "category": category, "machineID": MachineID}
    increment_fields = "productioncount"
    update_status = Doc().Increment_Value(col=col, incrementField=increment_fields, query=query)
    publish_to_replication_server(collection_name=col, entry_mode="INC", loaded_data=increment_fields,
                                  device_id=MachineID, query=query, return_response=False)

    if update_status is None:
        data = {
            "machineID": MachineID,
            "date": date,
            "productioncount": 1,
            "qualitycode": qualityCode,
            "qualityid": qualityId,
            "qualitydescription": category,
            "category": category,
            "ReferenceID": ""
        }
        Doc().DB_Write(data=data, col=col)
        publish_to_replication_server(collection_name=col, entry_mode="C", loaded_data=data,
                                      device_id=MachineID, query={}, return_response=False)


def productionCount_Log(MID, SID, JID, OID, Category, TimeStamp, QualityCode):
    col = "Productivity"
    count = 1
    data = {
        "machineID": MID,
        "shiftID": SID,
        "jobID": JID,
        "operatorID": OID,
        "timeStamp": TimeStamp,
        "productionCount": count,
        "qualityCode": QualityCode,
        "qualityDescription": Category,
        "category": Category,
        "ReferenceID": ""
    }
    Doc().DB_Write(data=data, col=col)
    print("productionCountLog Published")
    publish_to_replication_server(collection_name=col, entry_mode="C", loaded_data=data,
                                  device_id=MID, query={}, return_response=False)
