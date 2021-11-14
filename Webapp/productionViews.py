import datetime
import json
import threading

from rest_framework import status

import App.globalsettings as gs
from rest_framework.views import APIView
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from App.CNC_Calculation.MachineApi import MachineApi
from App.CNC_Calculation.MachineStatus import downTimeReasonUpdater
from App.OPCUA.ResultFormatter import DurationCalculatorFormatted


class getdowntimereason(APIView):
    @staticmethod
    def get(request):
        # reasons = [
        #     {"id": "1001", "name": "tea break"},
        #     {"id": "1002", "name": "launch"},
        #     {"id": "1003", "name": "Mechanical breakdown"}

        MachineId = "MID-01"
        reasons = MachineApi.getDownTimeReason(MachineId)
        if not reasons:
            jsonResponse = []
        else:
            jsonList = []
            for reason in reasons:
                data = {
                    "id": reason["DownCode"],
                    "name": reason["DownCodeReason"]
                }
                jsonList.append(data)
            jsonResponse = json.dumps(jsonList, indent=4)
        return HttpResponse(jsonResponse, "application/json")


class getdowntimecategory(APIView):
    @staticmethod
    def get(request):
        # category = [
        #     {"id": "1", "category": "plannedDowntime"},
        #     {"id": "2", "category": "UnplannedDowntime"}
        # ]
        MachineId = "MID-01"
        col = 'DownTimeCode'
        reasons = MachineApi.getDownTimeCategory(MachineId,col)

        jsonList = []
        for reason in reasons:
            data = {
                "id": reason["_id"]["id"],
                "category": reason["_id"]["category"]
            }
            jsonList.append(data)
        jsonResponse = json.dumps(jsonList, indent=4)
        return HttpResponse(jsonResponse, "application/json")


class getdowntimedata(APIView):
    @staticmethod
    def get(request):
        fromDate = request.GET.get("date")
        dateTime = datetime.datetime.strptime(fromDate, gs.OEE_MongoDBDateTimeFormat)
        downTimeData = MachineApi.getDownTimeData(MachineID="MID-01", dateTime=dateTime)

        downDataList = []
        for index, downObj in enumerate(downTimeData):
            data = {
                "sno": str(index + 1),
                "id": str(downObj["_id"]),
                "date": datetime.datetime.strftime(downObj["StartTime"], gs.OEE_JsonDateFormat),
                "from": datetime.datetime.strftime(downObj["StartTime"], gs.OEE_OutputTimeFormat),
                "to": datetime.datetime.strftime(downObj["StopTime"], gs.OEE_OutputTimeFormat),
                "duration": DurationCalculatorFormatted(downObj["Duration"]),
                "downid": downObj["DownTimeCode"],
                "reason": downObj["Description"],
                "category": downObj["Category"]
            }
            downDataList.append(data)

        # downtimedata = [
        #     {
        #         "id": "1",
        #         "date": "2021-12-01",
        #         "from": "09:30 AM",
        #         "to": "10:30 AM",
        #         "duration": "01:00 hr",
        #         "downid": "01",
        #         "reason": "test",
        #         "category": ""
        #     },
        #     {
        #         "id": "2",
        #         "date": "2021-12-01",
        #         "from": "11:30 AM",
        #         "to": "12:30 AM",
        #         "duration": "01:00 hr",
        #         "downid": "01",
        #         "reason": "test",
        #         "category": ""
        #     }
        # ]

        jsonResponse = json.dumps(downDataList, indent=4)
        return HttpResponse(jsonResponse, "application/json")


class postdowntimedata(APIView):
    @staticmethod
    def post(request):
        # database Insert function
        data = request.body.decode("UTF-8")
        requestData = json.loads(data)
        MachineApi.postDownTimeData(requestData)

        ''' After Save function is completed This function is called for UI reflection. '''
        thread = threading.Thread(target=downTimeReasonUpdater, args=())
        thread.start()

        return HttpResponse('success', "application/json")


class getqualitycategory(APIView):
    @staticmethod
    def get(request):
        category = [
            {"id": "1", "category": "good"},
            {"id": "2", "category": "bad"}
        ]

        MachineId = "MID-01"
        col = 'QualityCode'
        reasons = MachineApi.getQualityCode(MachineId)
        jsonList = []
        for reason in reasons:
            data = {
                "id": reason["category"],
                "category": reason["category"]
            }
            jsonList.append(data)
        jsonResponse = json.dumps(jsonList, indent=4)
        print(jsonResponse)
        return HttpResponse(jsonResponse, "application/json")


class getqualitycode(APIView):
    @staticmethod
    def get(request):
        category = [
            {"code": "1", "id": "good piece", "description": "good"},
            {"code": "2", "id": "bad piece", "description": "bad"}
        ]
        MachineId = "MID-01"
        reasons = MachineApi.getQualityCode(MachineId)
        jsonList = []
        for reason in reasons:
            data = {
                "code": reason["qualityCode"],
                "id": reason["category"],
                "description": reason["QualityDescription"]
            }
            jsonList.append(data)
        jsonResponse = json.dumps(jsonList, indent=4)
        return HttpResponse(jsonResponse, "application/json")


class getqualitydata(APIView):
    @staticmethod
    def get(request):
        qualitydata = [
            {
                "id": "1",
                "date": "2021-12-01",
                "productioncount": "10",
                "qualitycode": "10001",
                "qualityid": "ID001",
                "qualitydescription": "A high stantared",
                "category": "good",
            }
        ]

        fromDate = request.GET.get("date")
        dateTime = datetime.datetime.strptime(fromDate, gs.OEE_MongoDBDateTimeFormat)
        qualityData = MachineApi.getQualityData(dateTime=dateTime)

        qualityDataList = []
        for index, qualityObj in enumerate(qualityData):
            data = {
                "sno": str(index + 1),
                "id": str(qualityObj["_id"]),
                "date": qualityObj["date"],
                "productioncount": qualityObj["productioncount"],
                "qualitycode": qualityObj["qualitycode"],
                "qualityid": qualityObj["qualityid"],
                "qualitydescription": qualityObj["qualitydescription"],
                "category": qualityObj["category"]
            }
            qualityDataList.append(data)

        jsonResponse = json.dumps(qualityDataList, indent=4)

        return HttpResponse(jsonResponse, "application/json")


class postqualitydata(APIView):
    @staticmethod
    def post(request):
        data = request.body.decode("UTF-8")
        requestData = json.loads(data)
        MachineApi.postQualityData(requestData)

        # database Insert function
        return HttpResponse('success', "application/json")


class getproductiondata(APIView):
    @staticmethod
    def get(request):
        # productiondata = [
        #     {
        #         "id": "1",
        #         "shiftname": "Shift001",
        #         "inseconds": "28800",
        #         "category": "Shift",
        #         "starttime": "06:00 AM 20-10-21",
        #         "endtime": "02:00 PM 20-10-21",
        #         "mantatory": "yes",
        #     },
        #     {
        #         "id": "2",
        #         "shiftname": "Shift002",
        #         "inseconds": "28800",
        #         "category": "Shift",
        #         "starttime": "04:00 AM 20-10-21",
        #         "endtime": "08:00 PM 20-10-21",
        #         "mantatory": "no",
        #     }
        # ]

        productionData = MachineApi.getProductionData()
        if not productionData:
            jsonResponse = []
        else:
            productionDataList = []
            for index, obj in enumerate(productionData):
                data = {
                    "sno": str(index + 1),
                    "id": str(obj["_id"]),
                    "shiftname": obj["Name"],
                    "inseconds": obj["InSeconds"],
                    "category": obj["Category"],
                    "starttime": obj["ShiftStartTime"],
                    "endtime": obj["ShiftEndTime"],
                    "mantatory": obj["Mandatory"],
                }
                productionDataList.append(data)
            jsonResponse = json.dumps(productionDataList, indent=4)

        return HttpResponse(jsonResponse, "application/json")


class postproductiondata(APIView):
    @staticmethod
    def post(request):
        data = request.body.decode("UTF-8")
        requestData = json.loads(data)

        # database Insert function
        MachineApi.postProductionData(requestData=requestData)
        return HttpResponse("Successful", "application/json")


class getTotalProductionCount(APIView):
    @staticmethod
    def get(request):
        fromDate = request.GET.get("date")
        dateTime = datetime.datetime.strptime(fromDate, gs.OEE_MongoDBDateTimeFormat)
        qualityData = MachineApi.getQualityData(dateTime=dateTime)
        totalCount = 0
        for objects in qualityData:
            totalCount += int(float(objects["productioncount"]))
        response = {"totalQuantity": str(totalCount)}
        return JsonResponse(response, status=status.HTTP_200_OK, safe=False)
