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
                'Color': True,
                'DownCode': True,
                'DownCodeReason': True
                # other desired fields
            }}
        ]

        category = Doc().ReadDownCodeList(col=col, contents=contents)
        return category

    @staticmethod
    def getDownTimeCategory(MachineId: str):

        col = 'DownTimeCode'
        contents = [{"$group": {"_id": {"id": "$Category", "category": "$Category"}}}]
        category = Doc().ReadDownCodeList(col=col, contents=contents)
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
        print(fromTime)
        query = {"date": str(fromTime)}
        result = Doc().Read_Multiple_Document(col=col, query=query)
        return result
    #
    # @staticmethod
    # def postQualityData():
    #     col ='Running'
    #     data = request.body.decode("UTF-8")
    #     requestData = json.loads(data)
    #     # object_id = requestData[_id]
    #     # updatequery = {"$set": {requestData}}
    #
    #     for listdata in requestData:
    #         id = listdata[_id]
    #         query = {_id: id}
    #         updatequery = {"$set": {listdata}}
    #         if Doc().findWithQuery(col, query).limit(1).count() > 0:
    #             Doc.UpdateDBQuery(col=col, query=updatequery, object_id=id)
    #         else:
    #             Doc().DB_Write(listdata)
    #
    #     # database Insert function
    #     return True

    @staticmethod
    def getProductionData():
        col = 'ProductionPlan'
        query = {"Category": "SHIFT"}
        productionObjects = Doc().Read_Multiple_Document(col=col, query=query)
        return productionObjects

    @staticmethod
    def postProductionData(requestData: list):
        col = "ProductionPlan"
        # data = request.body.decode("UTF-8")
        # requestData = json.loads(data)
        for obj in requestData:
            replacementData = {
                "Name": obj["shiftname"],
                "InSeconds": obj["inseconds"],
                "Category": obj["category"],
                "ShiftStartTime": obj["starttime"],
                "ShiftEndTime": obj["endtime"],
                "Mandatory": obj["mantatory"]
            }
            query = {"_id": bson.ObjectId(obj["id"])}
            data = {"$set": replacementData}
            Doc().UpdateManyQueryBased(col=col, query=query, data=data)