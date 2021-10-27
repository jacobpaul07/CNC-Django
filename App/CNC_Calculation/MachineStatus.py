import json

from App.OPCUA.ResultFormatter import MachineStatus, Duration_Calculator, Duration_Converter
import datetime


def GenericProperty(readDB, otherDB, currentTime, path, otherPath):

    # if readDB is None:
    #     insertData = MachineStatus(currentTime)
    #     Doc().DB_Write(col=col, data=insertData)
    #     return 0
    #
    # else:
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
    # updateData = {"$set": {"TotalDuration": totalDuration,
    #                        "Timestamp": currentTime}}

    # returnValue = Doc().UpdateQueryBased(col=col, query=query, data=updateData)

    # Doc().UpdateQueryBased(col="Down",
    #                        query=query,
    #                        data={"$set": {"Timestamp": currentTime}})
    return 0


def machineStatus(returnData, Running_Json, Down_Json):

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
