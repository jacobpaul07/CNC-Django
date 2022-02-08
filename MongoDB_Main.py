import pymongo
import config.databaseconfig as dbc
import App.globalsettings as appSetting

from datetime import datetime, timedelta
from App.Json_Class.index import read_setting
from config.databaseconfig import Databaseconfig
from App.GenericKafkaConsumer.GenericReplicationPublisher import publish_to_replication_server


class Document:

    def __init__(self):
        # Read the config file objects
        data = read_setting()
        data_base: str = data.edgedevice.Service.MongoDB.DataBase
        connection = Databaseconfig()
        connection.connect()
        self.db = dbc.client[data_base]

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
        obj_list = []
        for i in v:
            value = i
            obj_list.append(value)
        return obj_list

    def ReadDownCodeList(self, col, contents):
        collection = self.db[col]
        documents = collection.aggregate(contents)
        docs_list = [docs for docs in documents]
        return docs_list

    def Read_Document(self, col):
        collection = self.db[col]
        documents = collection.find()
        docs_list = [docs for docs in documents]
        return docs_list

    def Criteria_Document(self, col, from_date, to_date, topic):
        collection = self.db[col]
        criteria = {"$and": [{"dateTime": {"$gte": from_date, "$lte": to_date}}, {"topic": topic}]}
        objects_found = collection.find(criteria, {"_id": 0})
        series = []
        for docs in objects_found:
            series.append(docs)
        return series

    # ''' MachineID not implemented here '''
    def SpecificDate_Document(self, Timestamp: str, filterField: str, col, machineID):
        collection = self.db[col]
        date_time = datetime.strptime(Timestamp, appSetting.OEE_MongoDBDateTimeFormat)
        from_date = datetime(date_time.year, date_time.month, date_time.day, date_time.hour, date_time.minute, 0, 000000)
        to_date = datetime(date_time.year, date_time.month, date_time.day, date_time.hour, date_time.minute, 0,
                           000000) + timedelta(minutes=10)
        criteria = {"$and": [{filterField: {"$gte": from_date, "$lte": to_date}}, {"machineID": machineID}]}
        objects_found = list(collection.find(criteria, {"_id": 0}).sort(filterField, pymongo.ASCENDING))
        series = []
        if len(objects_found) > 0:
            series.append(objects_found[0])
        return series

    def getDowntimeDocumentForSpecificDate(self, RecycledHour, specificDate: datetime, machineID):
        collection = self.db["Availability"]
        current_hour = specificDate.hour
        if current_hour <= RecycledHour:
            from_date = datetime(specificDate.year, specificDate.month, specificDate.day,
                                 RecycledHour, 0, 0, 000000) + timedelta(days=-1)
            to_date = datetime(specificDate.year, specificDate.month, specificDate.day,
                               current_hour, 0, 0, 000000)

        else:
            from_date = datetime(specificDate.year, specificDate.month, specificDate.day,
                                 RecycledHour, 0, 0, 000000)
            to_date = datetime(specificDate.year, specificDate.month, specificDate.day,
                               current_hour, 0, 0, 000000)

        criteria = {
            "$and": [{"StartTime": {"$gte": from_date, "$lte": to_date}}, {"Status": "Down"}, {"machineID": machineID}]}
        objects_found = collection.find(criteria, {"_id": 0})
        series = []
        for docs in objects_found:
            series.append(docs)
        return series

    def getDowntimeDocument(self, RecycledHour):
        collection = self.db["Availability"]
        current_hour = datetime.now().hour
        if current_hour <= RecycledHour:
            from_date = datetime(datetime.today().year, datetime.today().month, datetime.today().day,
                                 RecycledHour, 0, 0, 000000) + timedelta(days=-1)
            to_date = datetime(datetime.today().year, datetime.today().month, datetime.today().day,
                               RecycledHour, 0, 0, 000000)

        else:
            from_date = datetime(datetime.today().year, datetime.today().month, datetime.today().day,
                                 RecycledHour, 0, 0, 000000)
            to_date = datetime(datetime.today().year, datetime.today().month, datetime.today().day,
                               RecycledHour, 0, 0, 000000) + timedelta(days=1)

        criteria = {"$and": [{"StartTime": {"$gte": from_date, "$lte": to_date}}, {"Status": "Down"}]}
        objects_found = collection.find(criteria, {"_id": 0})
        series = []
        for docs in objects_found:
            series.append(docs)
        return series

    def Write_Document(self, col, myquery, data):
        collection = self.db[col]
        # myquery = {'DeviceID': DeviceID}
        x = collection.replace_one(myquery, data)
        updated_count = x.matched_count
        print("documents updated in MongoDB.")
        # print(updatedCount, "documents updated.")
        return updated_count

    def Increment_Value(self, col, incrementField, query):
        collection = self.db[col]
        # myquery = {'MID': MID}
        data = {'$inc': {incrementField: 1}}
        updated_document = collection.find_one_and_update(query, data)
        # updatedCount = x.matched_count
        print("documents updated in MongoDB.")
        return updated_document

    def LastUpdatedDocument(self, col):
        collection = self.db[col]
        objects_found = collection.find().sort([('timestamp', -1)]).limit(1)
        x = []
        for docs in objects_found:
            x.append(docs)
        return x

    def ReadDBQuery(self, col, query):
        collection = self.db[col]
        objects_found = collection.find_one(query)
        return objects_found

    def UpdateDBQuery(self, col, query, updateData):
        collection = self.db[col]
        objects_found = collection.find_one_and_update(query, updateData)
        return objects_found

    def update_query_local_and_cloud(self, col, query, update_data, machine_id, query_cloud):
        collection = self.db[col]
        objects_found = collection.find_one_and_update(query, update_data)
        publish_to_replication_server(collection_name=col, entry_mode="U", loaded_data=update_data,
                                      device_id=machine_id,
                                      query=query_cloud, return_response=False)
        return objects_found

    def UpdateQueryBased(self, col, query, data):
        collection = self.db[col]
        x = collection.find_one_and_update(query, data)
        return x

    def UpdateManyQueryBased(self, col, query, data):
        collection = self.db[col]
        collection.update_many(query, data)

    def Read_Multiple_Document(self, col, query):
        collection = self.db[col]
        objects_found = collection.find(query)
        docs_list = [docs for docs in objects_found]
        return docs_list

    def Read_Quality_Document(self, fromDate, toDate, machineID):
        col = "Quality"
        collection = self.db[col]
        from_date_str = str(fromDate.date())
        to_date_str = str(toDate.date())
        query = {"$and": [{"date": {"$gte": from_date_str, "$lte": to_date_str}}, {"machineID": machineID}]}
        objects_found = collection.find(query)
        docs_list = [docs for docs in objects_found]
        return docs_list

    def Read_Productivity_Document(self, startDateTime, EndDateTime, machineID):
        col = "Productivity"
        collection = self.db[col]
        start_date = datetime(startDateTime.year, startDateTime.month, startDateTime.day, 0, 0, 0, 000000)
        end_date = datetime(EndDateTime.year, EndDateTime.month, EndDateTime.day, 23, 59, 59, 000000) + timedelta(days=1)
        query = {"$and": [{"timeStamp": {"$gte": start_date, "$lte": end_date}}, {"machineID": machineID}]}
        objects_found = collection.find(query)
        docs_list = [docs for docs in objects_found]
        return docs_list

    def Read_Availability_Document(self, fromDate, toDate, machineID):
        col = "Availability"
        collection = self.db[col]
        start_date = datetime(fromDate.year, fromDate.month, fromDate.day, 0, 0, 0, 000000)
        end_date = datetime(toDate.year, toDate.month, toDate.day, 23, 59, 59, 000000)
        query = {"$and": [{"StartTime": {"$gte": start_date},
                           "StopTime": {"$lte": end_date},
                           "Cycle": "Closed", "machineID": machineID}]}
        objects_found = collection.find(query)
        docs_list = [docs for docs in objects_found]
        return docs_list

    # def Read_Produciton_History_Document(self, fromDate, toDate, machineID):
    #     col = "ProductionPlanHistory"
    #     collection = self.db[col]
    #
    #     startDate = datetime(fromDate.year, fromDate.month, fromDate.day, 0, 0, 0, 000000)
    #     endDate = datetime(toDate.year, toDate.month, toDate.day, 23, 59, 59, 000000)
    #     query = {"$and": [{"timeStamp": {"$gte": startDate}},
    #                       {"timeStamp": {"$lte": endDate}},
    #                       {"machineID": machineID}]}
    #     objectsFound = collection.find(query)
    #     docsList = [docs for docs in objectsFound]
    #     return docsList

    def Read_DbLogs(self, fromDate, toDate, machineID):
        col = "Logs"
        collection = self.db[col]
        # query = {"$and": [{"Timestamp": {"$gte": start_date}}, {"Timestamp": {"$lte": end_date}},
        #                   {"machineID": machineID}]}

        aggregate = [
            {
                '$match': {
                    '$and': [
                        {
                            'machineID': machineID
                        }, {
                            'Timestamp': {
                                '$gte': fromDate,
                                '$lte': toDate
                            }
                        }
                    ]
                }
            }, {
                '$group': {
                    '_id': {
                        'date': {
                            '$dateFromParts': {
                                'year': {
                                    '$year': '$Timestamp'
                                },
                                'month': {
                                    '$month': '$Timestamp'
                                },
                                'day': {
                                    '$dayOfMonth': '$Timestamp'
                                }
                            }
                        },
                        'hour': {
                            '$hour': '$Timestamp'
                        }
                    },
                    'doc': {
                        '$last': '$$ROOT'
                    }
                }
            }, {
                '$sort': {
                    '_id': 1
                }
            }, {
                '$replaceRoot': {
                    'newRoot': {
                        '$mergeObjects': [
                            {
                                'datewithhour': '$_id'
                            }, '$doc'
                        ]
                    }
                }
            }
        ]

        objects_found = collection.aggregate(aggregate)
        docs_list = [docs for docs in objects_found]
        return docs_list

    def DateIntervals_Document(self, fromDate, toDate, filterField: str, col):
        collection = self.db[col]
        start_date = datetime(fromDate.year, fromDate.month, fromDate.day, 0, 0, 0, 000000)
        end_date = datetime(toDate.year, toDate.month, toDate.day, 23, 59, 59, 000000)
        stage_1 = {"$match": {filterField: {"$gte": start_date, "$lte": end_date}}}
        stage_2 = {'$sort': {'_id': 1}}
        stage_3 = {"$group": {
            "_id": {
                "$dateFromParts": {
                    "year": {"$year": "$" + filterField},
                    "month": {"$month": "$" + filterField},
                    "day": {"$dayOfMonth": "$" + filterField},
                },
            },
            "data": {
                "$last": "$$ROOT"
            }
        }}
        stage_4 = {'$sort': {'_id': 1}}

        aggregation = [stage_1, stage_2, stage_3, stage_4]
        cursor = collection.aggregate(aggregation)
        series = []
        for obj in cursor:
            series.append(obj)
        return series

    def HourIntervals_Document(self, fromDate, toDate, col):
        collection = self.db[col]
        start_date = datetime(fromDate.year, fromDate.month, fromDate.day, 0, 0, 0, 000000)
        end_date = datetime(toDate.year, toDate.month, toDate.day, 23, 59, 59, 000000)
        stage_1 = {"$match": {"currentTime": {"$gte": start_date, "$lte": end_date}}}
        stage_2 = {"$group": {
            "_id": {
                "year": {"$year": "$currentTime"},
                "month": {"$month": "$currentTime"},
                "day": {"$dayOfMonth": "$currentTime"},
                "hour": {"$hour": "$currentTime"},
            },
            "data": {
                "$last": "$$ROOT"
            }
        }
        }
        stage_3 = {'$sort': {'_id': 1}}

        Aggregation = [stage_1, stage_3, stage_2, stage_3]
        cursor = collection.aggregate(Aggregation)
        series = []
        for obj in cursor:
            series.append(obj)
        return series

    def historyUpdateExcelDocuments(self, date, historyCollection, updatedDocument, machineID):
        collection = self.db[historyCollection]
        start_date = datetime(date.year, date.month, date.day, 0, 0, 0, 000000)
        end_date = datetime(date.year, date.month, date.day, 23, 59, 59, 000000)
        query = {"$and": [{"timeStamp": {"$gte": start_date, "$lte": end_date}}, {"machineID": machineID}]}
        collection.delete_many(query)
        # replica delete many procedure call
        publish_to_replication_server(collection_name=historyCollection, entry_mode="DM", loaded_data={},
                                      device_id=machineID, query=query, return_response=False)

        for write_obj in updatedDocument:
            self.DB_Write(data=write_obj, col=historyCollection)
            # replica create document
            publish_to_replication_server(collection_name=historyCollection, entry_mode="C", loaded_data=write_obj,
                                          device_id=machineID, query={}, return_response=False)

    def Read_Availability_Document_History(self, fromDate, toDate, machineID):
        col = "Availability"
        collection = self.db[col]
        query = {"$and": [{"StartTime": {"$gte": fromDate.replace(tzinfo=None)}},
                          {"StopTime": {"$lte": toDate.replace(tzinfo=None)}},
                          {"machineID": machineID}
                          ]}
        objects_found = collection.find(query)
        docs_list = [docs for docs in objects_found]
        return docs_list

    def read_production_history_document(self, fromDate, toDate, machineID):
        col = "ProductionPlanHistory"
        collection = self.db[col]
        start_date = datetime(fromDate.year, fromDate.month, fromDate.day, 0, 0, 0, 000000)
        end_date = datetime(toDate.year, toDate.month, toDate.day, 23, 59, 59, 000000)
        query = {"$and": [{"timeStamp": {"$gte": start_date}},
                          {"timeStamp": {"$lte": end_date}}, {"machineID": machineID}]}
        objects_found = collection.find(query)
        docs_list = [docs for docs in objects_found]
        return docs_list
