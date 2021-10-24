from App.OPCUA.ResultFormatter import MachineStatus, Duration_Calculator, Duration_Converter
from MongoDB_Main import Document as Doc
import datetime


def machineStatus(returnData):
    currentTime = datetime.datetime.now()
    query = {"MachineId": "MID-01"}

    if returnData["PowerOn_Status"] == "True":
        col = "Running"
        readDB = Doc().ReadDBQuery(col=col, query=query)
        if readDB is None:
            insertData = MachineStatus(currentTime)
            Doc().DB_Write(col=col, data=insertData)
            return 0

        else:
            durationOld = Duration_Calculator(readDB["TotalDuration"])
            oldTimestamp = readDB["Timestamp"]
            durationNew_Str = str(currentTime - oldTimestamp)
            print(durationNew_Str)
            durationNew = Duration_Calculator(durationNew_Str)
            totalDur = durationOld + durationNew
            totalDuration = Duration_Converter(totalDur*60)
            print(totalDuration)
            updateData = {"$set": {"TotalDuration": totalDuration,
                                   "Timestamp": currentTime}}
            returnValue = Doc().UpdateQueryBased(col=col, query=query, data=updateData)
            Doc().UpdateQueryBased(col="Down",
                                   query=query,
                                   data={"$set": {"Timestamp": currentTime}},
                                   )

            return returnValue

    elif returnData["PowerOn_Status"] == "False":
        col = "Down"
        readDB = Doc().ReadDBQuery(col=col, query=query)

        if readDB is None:
            insertData = MachineStatus(currentTime)
            Doc().DB_Write(col=col, data=insertData)
            return 0

        else:
            durationOld = Duration_Calculator(readDB["TotalDuration"])
            oldTimestamp = readDB["Timestamp"]
            durationNew_Str = str(currentTime - oldTimestamp)
            durationNew = Duration_Calculator(durationNew_Str)
            totalDur = durationOld + durationNew
            totalDuration = Duration_Converter(totalDur * 60)
            print(totalDuration)
            updateData = {"$set": {"TotalDuration": totalDuration,
                                   "Timestamp": currentTime}}
            returnValue = Doc().UpdateQueryBased(col=col, query=query, data=updateData)

            Doc().UpdateQueryBased(col="Down",
                                   query=query,
                                   data={"$set": {"Timestamp": currentTime}},
                                   )
            if returnValue is None:
                insertData = MachineStatus(currentTime)
                Doc().DB_Write(col=col, data=insertData)

            return returnValue

