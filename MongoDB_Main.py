import time

from App.Json_Class.index import read_setting
from config.databaseconfig import Databaseconfig
import config.databaseconfig as dbc
import json
from datetime import datetime, timedelta


class Document:

    def __init__(self):
        # Read the config file objects
        data = read_setting()
        DataBase: str = data.edgedevice.Service.MongoDB.DataBase
        connection = Databaseconfig()
        connection.connect()
        self.db = dbc.client[DataBase]

    def DB_Write(self, data, col):
        parameter = data
        collection = self.db[col]
        collection.insert_one(parameter)

    def DB_Read(self, col):
        collection = self.db[col]
        v = collection.find()
        list = []
        for i in v:
            value = i
            list.append(value)
        print(list)
        return list

    def Read_Document(self, col, DeviceID):
        collection = self.db[col]
        myquery = {'DeviceID': DeviceID}
        x = collection.find_one(myquery, {"_id": 0})
        return x

    def Criteria_Document(self, col, from_date, to_date, topic):
        collection = self.db[col]
        criteria = {"$and": [{"dateTime": {"$gte": from_date, "$lte": to_date}}, {"topic": topic}]}
        objectsFound = collection.find(criteria, {"_id": 0})
        series = []
        for docs in objectsFound:
            series.append(docs)
        return series

    def Write_Document(self, col, myquery, data):
        collection = self.db[col]
        # myquery = {'DeviceID': DeviceID}
        x = collection.replace_one(myquery, data)
        updatedCount = x.matched_count
        print("documents updated in MongoDB.")
        # print(updatedCount, "documents updated.")
        return updatedCount

    def Increment_Value(self, col, MID, value):
        collection = self.db[col]
        myquery = {'MachineId': MID}
        data = {'$inc': {value: 1}}
        x = collection.find_one_and_update(myquery, data)
        # updatedCount = x.matched_count
        print("documents updated in MongoDB.")

    def LastUpdatedDocument(self, col):
        collection = self.db[col]
        objectsFound = collection.find().sort([('timestamp', -1)]).limit(1)
        x = []
        for docs in objectsFound:
            x.append(docs)
        return x

    def ReadDBQuery(self, col, query):
        collection = self.db[col]
        objectsFound = collection.find_one(query)
        return objectsFound

    def UpdateDBQuery(self, col, query, object_id):
        collection = self.db[col]
        objectsFound = collection.find_one_and_update({"_id": object_id}, query)
        return objectsFound

    def UpdateQueryBased(self, col, query, data):
        collection = self.db[col]
        x = collection.find_one_and_update(query, data)
        return x


# collection.find({"Status": "Down", "Cycle": "Open"})
# Document().Increment_Value("LiveData", "MID-01", "badCount")

# timeStamp = datetime.now()
# col = "Running"
# doc = Document().ReadDBQuery(col=col, query={"MachineID": "MID-01"})
# duration = doc["TotalDuration"]
# oldTimestamp = doc["Timestamp"]
#
# totalDuration = timeStamp - oldTimestamp
# print(totalDuration)

# def datetime_to_timestamp(dt):
#     return time.mktime(dt.timetuple()) + dt.microsecond / 1e6

# currentTime = datetime.now()
# time.sleep(10)
# newtime = datetime.now()
# duration = str(newtime - currentTime)
#
# status = {
#         "MachineID": "MID-01",
#         "TotalDuration": duration,
#         "Timestamp": currentTime
#     }
#
# Document().DB_Write(col="Running", data=status)

