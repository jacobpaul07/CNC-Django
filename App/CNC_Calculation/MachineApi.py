import json
import bson

from datetime import datetime
from MongoDB_Main import Document as Doc
from App.globalsettings import GlobalFormats
from App.GeneralUtils.index import historyUpdateExcel
from App.GenericKafkaConsumer.GenericReplicationPublisher import publish_to_replication_server


class MachineApi:

    @staticmethod
    def get_down_time_reason(machine_id):

        col = 'DownTimeCode'
        query = {'machineID': machine_id}
        result = Doc().Read_Multiple_Document(col=col, query=query)
        return result

    @staticmethod
    def get_down_time_category(machine_id: str, col):

        group = {"$group": {"_id": {"id": "$Category", "category": "$Category"}}}
        match = {'$match': {'machineID': machine_id}}
        aggregation = [match, group]
        category = Doc().ReadDownCodeList(col=col, contents=aggregation)
        return category

    @staticmethod
    def get_quality_code(machine_id: str):

        col = 'QualityCode'
        query = {'machineID': machine_id}
        result = Doc().Read_Multiple_Document(col=col, query=query)
        return result

    @staticmethod
    def get_down_time_data(machine_id: str, date_time):
        col = 'Availability'
        from_date = datetime(date_time.year, date_time.month, date_time.day, 0, 0, 0, 000000)
        to_date = datetime(date_time.year, date_time.month, date_time.day, 23, 59, 59, 000000)
        criteria = {"machineID": machine_id, "Status": "Down", "Cycle": "Closed"}
        query = {"$and": [{"StartTime": {"$gte": from_date, "$lte": to_date}}, criteria]}
        result = Doc().Read_Multiple_Document(col=col, query=query)
        return result

    @staticmethod
    def post_down_time_data(request_data):
        col = "Availability"
        for obj in request_data:
            object_id = obj["id"]
            reference_id = obj["ReferenceID"]
            machine_id = obj["machineID"]
            machine_id = machine_id.replace("_", "-")

            replacement_data = {
                "DownTimeCode": obj["downid"],
                "Description": obj["reason"],
                "Category": obj["category"]
            }
            data = {"$set": replacement_data}
            query = {"$and": [{"_id": bson.ObjectId(object_id)}, {"machineID": machine_id}]}
            Doc().UpdateManyQueryBased(col=col, query=query, data=data)

            # Update on Replica Data Initiated
            query_cloud = {"$and": [{"_id": reference_id}, {"machineID": machine_id}]}
            publish_to_replication_server(collection_name=col, entry_mode="U", loaded_data=data,
                                          device_id=machine_id,
                                          query=query_cloud, return_response=False)

    @staticmethod
    def get_quality_category(machine_id):
        col = 'QualityCode'
        match = {'$match': {'machineID': machine_id}}
        group = {"$group": {"_id": {"id": "$Category", "category": "$Category"}}}
        aggregation = [match, group]
        category = Doc().ReadDownCodeList(col=col, contents=aggregation)
        return category

    @staticmethod
    def get_quality_data(date_time, machine_id):
        col = 'Quality'
        from_time = datetime.strftime(date_time, "%Y-%m-%d")
        query = {"$and": [{"date": str(from_time)}, {"machineID": machine_id}]}
        result = Doc().Read_Multiple_Document(col=col, query=query)
        return result

    @staticmethod
    def post_quality_data(request_data):
        col = 'Quality'
        for requestObj in request_data:
            object_id = requestObj["id"]
            machine_id = requestObj["machineID"]
            machine_id = machine_id.replace("_", "-")

            reference_id = requestObj["ReferenceID"]
            updated_data = {
                "date": requestObj["date"],
                "productioncount": int(requestObj["productioncount"]),
                "qualitycode": requestObj["qualitycode"],
                "qualityid": requestObj["qualityid"],
                "qualitydescription": requestObj["qualitydescription"],
                "category": requestObj["category"],
                "machineID": machine_id,
            }

            if len(str(requestObj["id"])) == 24:
                query = {"$and": [{"_id": bson.ObjectId(object_id)}, {"machineID": machine_id}]}
                data = {"$set": updated_data}
                Doc().UpdateManyQueryBased(col=col, query=query, data=data)

                # Update on Replica Data Initiated
                query_cloud = {"$and": [{"_id": reference_id}, {"machineID": machine_id}]}
                publish_to_replication_server(collection_name=col, entry_mode="U", loaded_data=data,
                                              device_id=machine_id,
                                              query=query_cloud, return_response=False)
            else:
                Doc().DB_Write(col=col, data=updated_data)
                # Insert Replica Data Initiated
                publish_to_replication_server(collection_name=col, entry_mode="C", loaded_data=updated_data,
                                              device_id=machine_id, query={}, return_response=False)

        # database Insert function
        return True

    @staticmethod
    def get_production_data(machine_id):
        col = 'ProductionPlan'
        # query = {"Category": "SHIFT"}
        query = {"machineID": machine_id}
        production_objects = Doc().Read_Multiple_Document(col=col, query=query)
        return production_objects

    @staticmethod
    def post_production_data(request_data: list):
        col = "ProductionPlan"
        # data = request.body.decode("UTF-8")
        # requestData = json.loads(data)
        production_list = []
        for obj in request_data:
            machine_id = obj["machineID"]
            machine_id = machine_id.replace("_", "-")

            object_id = obj["id"]
            reference_id = obj["ReferenceID"]
            shift_start_time = datetime.strptime(obj["starttime"], GlobalFormats.oee_mongo_db_date_time_format())
            shift_end_time = datetime.strptime(obj["endtime"], GlobalFormats.oee_mongo_db_date_time_format())
            replacement_data = {
                "SNo": obj["sno"],
                "Name": obj["shiftname"],
                "InSeconds": obj["inseconds"],
                "Category": obj["category"],
                "ShiftStartTime": datetime.strftime(shift_start_time, GlobalFormats.oee_excel_date_time_format()),
                "ShiftEndTime": datetime.strftime(shift_end_time, GlobalFormats.oee_excel_date_time_format()),
                "Mandatory": obj["mantatory"],
                "machineID": machine_id
            }
            production_list.append(replacement_data)
            query = {"$and": [{"_id": bson.ObjectId(object_id)}, {"machineID": machine_id}]}
            data = {"$set": replacement_data}
            Doc().UpdateManyQueryBased(col=col, query=query, data=data)

            # Update on Replica Data Initiated
            query_cloud = {"$and": [{"_id": reference_id}, {"machineID": machine_id}]}
            publish_to_replication_server(collection_name=col, entry_mode="U", loaded_data=data,
                                          device_id=machine_id,
                                          query=query_cloud, return_response=False)

        machine_id = request_data[0]["machineID"]
        with open("./App/JsonDataBase/ProductionPlan.json", "w+") as Files:
            json.dump(production_list, Files, indent=4)
            Files.close()

        # Production Plan History Database
        shift_start_time = request_data[0]["starttime"]
        current_time = datetime.strptime(shift_start_time, GlobalFormats.oee_mongo_db_date_time_format())
        historyUpdateExcel(loadedData=production_list, historyCollection="ProductionPlanHistory",
                           currentTime=current_time, machineID=machine_id)

    @staticmethod
    def get_total_production_count(date_time):
        col = 'Availability'
        from_date = datetime(date_time.year, date_time.month, date_time.day, 0, 0, 0, 000000)
        to_date = datetime(date_time.year, date_time.month, date_time.day, 23, 59, 59, 000000)
        criteria = {"Status": "Down", "Cycle": "Closed"}
        query = {"$and": [{"StartTime": {"$gte": from_date, "$lte": to_date}}, criteria]}
        result = Doc().Read_Multiple_Document(col=col, query=query)
        return result

    @staticmethod
    def get_down_time_report(from_date, to_date, status, machine_id):
        col = 'Availability'
        from_date = datetime(from_date.year, from_date.month, from_date.day, 0, 0, 0, 000000)
        to_date = datetime(to_date.year, to_date.month, to_date.day, 23, 59, 59, 000000)
        criteria = {"Status": status, "Cycle": "Closed", "machineID": machine_id}
        query = {"$and": [{"StartTime": {"$gte": from_date, "$lte": to_date}}, criteria]}
        result = Doc().Read_Multiple_Document(col=col, query=query)
        return result

    @staticmethod
    def get_oee_report(from_date, to_date):
        col = "LogsRawBackUp"
        result = Doc().DateIntervals_Document(fromDate=from_date, toDate=to_date, col=col, filterField="currentTime")
        return result
    
    @staticmethod
    def get_production_history(from_date, to_date, machine_id):
        result = Doc().read_production_history_document(fromDate=from_date, toDate=to_date, machineID=machine_id)
        return result

    @staticmethod
    def get_production_report(from_date, to_date):
        col = "Logs"
        from_date = datetime(from_date.year, from_date.month, from_date.day, 0, 0, 0, 000000)
        to_date = datetime(to_date.year, to_date.month, to_date.day, 23, 59, 59, 000000)
        query = {"$and": [{"Timestamp": {"$gte": from_date, "$lte": to_date}}]}
        result = Doc().Read_Multiple_Document(col=col, query=query)

        return result
