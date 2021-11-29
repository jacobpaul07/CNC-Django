import pymongo
from bson import SON

from App.Json_Class.index import read_setting
from config.databaseconfig import Databaseconfig
import config.databaseconfig as dbc
from datetime import datetime, timedelta
import App.globalsettings as appSetting


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

    def DB_Write_Many(self, data, col):
        parameter = data
        collection = self.db[col]
        collection.insert_many(parameter)

    def DB_Collection_Drop(self, col):
        collection = self.db[col]
        collection.drop()

    def DB_Read(self, col):
        collection = self.db[col]
        v = collection.find()
        list = []
        for i in v:
            value = i
            list.append(value)
        print(list)
        return list

    def ReadDownCodeList(self, col, contents):
        collection = self.db[col]
        documents = collection.aggregate(contents)
        docsList = [docs for docs in documents]
        return docsList

    def Read_Document(self, col):
        collection = self.db[col]
        documents = collection.find({"_id": 0})
        docsList = [docs for docs in documents]
        return docsList

    def Criteria_Document(self, col, from_date, to_date, topic):
        collection = self.db[col]
        criteria = {"$and": [{"dateTime": {"$gte": from_date, "$lte": to_date}}, {"topic": topic}]}
        objectsFound = collection.find(criteria, {"_id": 0})
        series = []
        for docs in objectsFound:
            series.append(docs)
        return series

    def SpecificDate_Document(self, Timestamp: str, filterField: str, col):
        collection = self.db[col]
        dateTime = datetime.strptime(Timestamp, appSetting.OEE_MongoDBDateTimeFormat)
        fromDate = datetime(dateTime.year, dateTime.month, dateTime.day, dateTime.hour, dateTime.minute, 0, 000000)
        toDate = datetime(dateTime.year, dateTime.month, dateTime.day, dateTime.hour, dateTime.minute, 0,
                          000000) + timedelta(minutes=10)
        criteria = {"$and": [{filterField: {"$gte": fromDate, "$lte": toDate}}]}
        objectsFound = list(collection.find(criteria, {"_id": 0}).sort(filterField, pymongo.ASCENDING))
        series = []
        print(len(objectsFound))
        if len(objectsFound) > 0:
            series.append(objectsFound[0])
        return series

    def getDowntimeDocumentForSpecificDate(self, RecycledHour, specificDate: datetime):
        collection = self.db["Availability"]
        currentHour = specificDate.hour
        if currentHour <= RecycledHour:
            fromDate = datetime(specificDate.year, specificDate.month, specificDate.day,
                                RecycledHour, 0, 0, 000000) + timedelta(days=-1)
            toDate = datetime(specificDate.year, specificDate.month, specificDate.day,
                              RecycledHour, 0, 0, 000000)

        else:
            fromDate = datetime(specificDate.year, specificDate.month, specificDate.day,
                                RecycledHour, 0, 0, 000000)
            toDate = datetime(specificDate.year, specificDate.month, specificDate.day,
                              RecycledHour, 0, 0, 000000) + timedelta(days=1)

        criteria = {"$and": [{"StartTime": {"$gte": fromDate, "$lte": toDate}}, {"Status": "Down"}]}
        objectsFound = collection.find(criteria, {"_id": 0})
        series = []
        for docs in objectsFound:
            series.append(docs)
        return series

    def getDowntimeDocument(self, RecycledHour):
        collection = self.db["Availability"]
        currentHour = datetime.now().hour
        if currentHour <= RecycledHour:
            fromDate = datetime(datetime.today().year, datetime.today().month, datetime.today().day,
                                RecycledHour, 0, 0, 000000) + timedelta(days=-1)
            toDate = datetime(datetime.today().year, datetime.today().month, datetime.today().day,
                              RecycledHour, 0, 0, 000000)

        else:
            fromDate = datetime(datetime.today().year, datetime.today().month, datetime.today().day,
                                RecycledHour, 0, 0, 000000)
            toDate = datetime(datetime.today().year, datetime.today().month, datetime.today().day,
                              RecycledHour, 0, 0, 000000) + timedelta(days=1)

        print(fromDate, toDate)
        criteria = {"$and": [{"StartTime": {"$gte": fromDate, "$lte": toDate}}, {"Status": "Down"}]}
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

    def Increment_Value(self, col, incrementField, query):
        collection = self.db[col]
        # myquery = {'MID': MID}
        data = {'$inc': {incrementField: 1}}
        updatedDocument = collection.find_one_and_update(query, data)
        # updatedCount = x.matched_count
        print("documents updated in MongoDB.")
        return updatedDocument

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

    def UpdateManyQueryBased(self, col, query, data):
        collection = self.db[col]
        collection.update_many(query, data)

    def Read_Multiple_Document(self, col, query):
        collection = self.db[col]
        objectsFound = collection.find(query)
        docsList = [docs for docs in objectsFound]
        return docsList

    def Read_Quality_Document(self, fromDate, toDate):
        col = "Quality"
        collection = self.db[col]
        fromDateStr = str(fromDate.date())
        toDateStr = str(toDate.date())
        query = {"$and": [{"date": {"$gte": fromDateStr, "$lte": toDateStr}}]}
        objectsFound = collection.find(query)
        docsList = [docs for docs in objectsFound]
        return docsList

    def DateIntervals_Document(self, fromDate, toDate, filterField: str, col):
        collection = self.db[col]
        startDate = datetime(fromDate.year, fromDate.month, fromDate.day, 0, 0, 0, 000000)
        endDate = datetime(toDate.year, toDate.month, toDate.day, 23, 59, 59, 000000)

        AggregateQuery = [
            {
                '$match': {
                    'currentTime': {
                        '$gte': startDate,
                        '$lte': endDate
                    }
                }
            }, {
                '$group': {
                    '_id': {
                        '$dateFromParts': {
                            'year': {
                                '$year': '$currentTime'
                            },
                            'month': {
                                '$month': '$currentTime'
                            },
                            'day': {
                                '$dayOfMonth': '$currentTime'
                            }
                        }
                    },
                    'data': {
                        '$last': '$$ROOT'
                    }
                }
            }
        ]
        stage_1 = {"$match": {"currentTime": {"$gte": startDate, "$lte": endDate}}}

        # stage_2 = {"$sort": {"currentTime": -1}}
        # stage_2 = {'$sort': {'currentTime': 1}}
        stage_3 = {"$group": {
            "_id": {
                "$dateFromParts": {
                    "year": {"$year": "$currentTime"},
                    "month": {"$month": "$currentTime"},
                    "day": {"$dayOfMonth": "$currentTime"},
                },
            },
            "data": {
                "$last": "$$ROOT"
            }
        }}
        Aggregation = [stage_1, stage_3]
        cursor = collection.aggregate(AggregateQuery)
        # objectsFound = collection.find_one(criteria, {"_id": 0})
        series = []
        for obj in cursor:
            series.append(obj)
        return series
