import json
from datetime import datetime
import bson
from MongoDB_Main import Document as Doc


class MachineApi:

    @staticmethod
    def getDownTimeReason(MachineId):

        col = 'DownTimeCode'
        contents = [
            {'$project': {
                '_id': {'$toString': '$_id'},
                'Threshold': True,
                'Category': True,
                'color': True,
                'DownCode': True,
                'DownCodeReason': True
                # other desired fields
            }}
        ]

        category = Doc().ReadDownCodeList(col=col, contents=contents)
        return category

    @staticmethod
    def getDownTimeCategory(MachineId: str, col):

        contents = [{"$group": {"_id": {"id": "$Category", "category": "$Category"}}}]
        category = Doc().ReadDownCodeList(col=col, contents=contents)
        return category

    @staticmethod
    def getQualityCode(MachineId: str):

        col = 'QualityCode'
        category = Doc().DB_Read(col=col)
        print(category)
        return category

    @staticmethod
    def getDownTimeData(MachineID: str, dateTime):
        col = 'Availability'
        fromDate = datetime(dateTime.year, dateTime.month, dateTime.day, 0, 0, 0, 000000)
        toDate = datetime(dateTime.year, dateTime.month, dateTime.day, 23, 59, 59, 000000)

        criteria = {"Status": "Down", "Cycle": "Closed"}
        query = {"$and": [{"StartTime": {"$gte": fromDate, "$lte": toDate}}, criteria]}

        result = Doc().Read_Multiple_Document(col=col, query=query)
        return result

    @staticmethod
    def postDownTimeData(requestData):
        col = "Availability"
        # data = request.body.decode("UTF-8")
        # requestData = json.loads(data)
        for obj in requestData:
            replacementData = {
                "DownTimeCode": obj["downid"],
                "Description": obj["reason"],
                "Category": obj["category"]
            }
            query = {"_id": bson.ObjectId(obj["id"])}
            data = {"$set": replacementData}
            Doc().UpdateManyQueryBased(col=col, query=query, data=data)

    @staticmethod
    def getQualityCategory():
        col = 'QualityCode'
        contents = [{"$group": {"_id": {"id": "$Category", "category": "$Category"}}}]
        category = Doc().ReadDownCodeList(col=col, contents=contents)
        return category

    @staticmethod
    def getQualityData(dateTime):
        col = 'Quality'
        fromTime = datetime.strftime(dateTime, "%Y-%m-%d")
        query = {"date": str(fromTime)}
        result = Doc().Read_Multiple_Document(col=col, query=query)
        return result

    @staticmethod
    def postQualityData(requestData):
        col = 'Quality'
        for requestObj in requestData:
            updatedData = {
                "date": requestObj["date"],
                "productioncount": int(requestObj["productioncount"]),
                "qualitycode": requestObj["qualitycode"],
                "qualityid": requestObj["qualityid"],
                "qualitydescription": requestObj["qualitydescription"],
                "category": requestObj["category"]
            }

            if len(str(requestObj["id"])) == 24:
                query = {"_id": bson.ObjectId(requestObj["id"])}
                data = {"$set": updatedData}
                Doc().UpdateManyQueryBased(col=col, query=query, data=data)
            else:
                Doc().DB_Write(col=col, data=updatedData)

        # database Insert function
        return True

    @staticmethod
    def getProductionData():
        col = 'ProductionPlan'
        # query = {"Category": "SHIFT"}
        query = {}
        productionObjects = Doc().Read_Multiple_Document(col=col, query=query)
        return productionObjects

    @staticmethod
    def postProductionData(requestData: list):
        col = "ProductionPlan"
        # data = request.body.decode("UTF-8")
        # requestData = json.loads(data)
        productionList = []
        for obj in requestData:
            replacementData = {
                "SNo": obj["sno"],
                "Name": obj["shiftname"],
                "InSeconds": obj["inseconds"],
                "Category": obj["category"],
                "ShiftStartTime": obj["starttime"],
                "ShiftEndTime": obj["endtime"],
                "Mandatory": obj["mantatory"]
            }
            productionList.append(replacementData)
            query = {"_id": bson.ObjectId(obj["id"])}
            data = {"$set": replacementData}
            Doc().UpdateManyQueryBased(col=col, query=query, data=data)
        with open("./App/JsonDataBase/ProductionPlan.json", "w+") as Files:
            json.dump(productionList, Files, indent=4)
            Files.close()

    @staticmethod
    def getTotalProductionCount(dateTime):
        col = 'Availability'
        fromDate = datetime(dateTime.year, dateTime.month, dateTime.day, 0, 0, 0, 000000)
        toDate = datetime(dateTime.year, dateTime.month, dateTime.day, 23, 59, 59, 000000)
        criteria = {"Status": "Down", "Cycle": "Closed"}
        query = {"$and": [{"StartTime": {"$gte": fromDate, "$lte": toDate}}, criteria]}
        result = Doc().Read_Multiple_Document(col=col, query=query)
        return result

    @staticmethod
    def getDownTimeReport(fromdate, todate, status):
        col = 'Availability'
        fromDate = datetime(fromdate.year, fromdate.month, fromdate.day, 0, 0, 0, 000000)
        toDate = datetime(todate.year, todate.month, todate.day, 23, 59, 59, 000000)
        criteria = {"Status": status, "Cycle": "Closed"}
        query = {"$and": [{"StartTime": {"$gte": fromDate, "$lte": toDate}}, criteria]}
        result = Doc().Read_Multiple_Document(col=col, query=query)
        return result

    @staticmethod
    def getOeeReport(fromdate):
        col = "LogsRawBackUp"
        result = Doc().DateIntervals_Document(Timestamp=fromdate, col=col, filterField="currentTime")
        return result

    @staticmethod
    def getProductionReport(fromdate, todate):
        col = "Logs"
        fromDate = datetime(fromdate.year, fromdate.month, fromdate.day, 0, 0, 0, 000000)
        toDate = datetime(todate.year, todate.month, todate.day, 23, 59, 59, 000000)
        query = {"$and": [{"Timestamp": {"$gte": fromDate, "$lte": toDate}}]}
        result = Doc().Read_Multiple_Document(col=col, query=query)

        return result
