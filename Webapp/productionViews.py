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
from App.OPCUA.index import readCalculation_file


class getdowntimereason(APIView):
    @staticmethod
    def get(request):

        calculationDataJson = readCalculation_file()
        MachineId = calculationDataJson["MachineId"]
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
        params = {k: v[0] for k, v in dict(request.GET).items()}
        mode = params["mode"]
        deviceID = params["deviceID"]

        col = 'DownTimeCode'
        reasons = MachineApi.getDownTimeCategory(deviceID, col)

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

        params = {k: v[0] for k, v in dict(request.GET).items()}
        fromDate = params["date"]
        mode = params["mode"]
        deviceID = params["deviceID"]

        dateTime = datetime.datetime.strptime(fromDate, gs.OEE_MongoDBDateTimeFormat)
        downTimeData = MachineApi.getDownTimeData(MachineID=deviceID, dateTime=dateTime)
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
                "category": downObj["Category"],
                "machineID": deviceID
            }
            downDataList.append(data)

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
    async def get(request):
        params = {k: v[0] for k, v in dict(request.GET).items()}
        mode = params["mode"] if "mode" in params else ""
        deviceID = params["deviceID"] if "deviceID" in params else ""
        if mode != "web":
            reasons = MachineApi.getQualityCode(deviceID)
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

        else:
            return HttpResponse("web", "application/json")


class getqualitycode(APIView):
    @staticmethod
    def get(request):

        params = {k: v[0] for k, v in dict(request.GET).items()}
        mode = params["mode"]
        deviceID = params["deviceID"]

        reasons = MachineApi.getQualityCode(deviceID)
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

        params = {k: v[0] for k, v in dict(request.GET).items()}
        fromDate = params["date"]
        mode = params["mode"]
        deviceID = params["deviceID"]

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
                "category": qualityObj["category"],
                "machineID": deviceID
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

        params = {k: v[0] for k, v in dict(request.GET).items()}
        mode = params["mode"]
        deviceID = params["deviceID"]
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
                    "machineID": deviceID
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

        params = {k: v[0] for k, v in dict(request.GET).items()}
        fromDate = params["date"]
        mode = params["mode"]
        deviceID = params["deviceID"]

        dateTime = datetime.datetime.strptime(fromDate, gs.OEE_MongoDBDateTimeFormat)
        qualityData = MachineApi.getQualityData(dateTime=dateTime)
        totalCount = 0
        for objects in qualityData:
            totalCount += int(float(objects["productioncount"]))
        response = {"totalQuantity": str(totalCount)}
        return JsonResponse(response, status=status.HTTP_200_OK, safe=False)


# import datetime
# import json
# import threading
#
# from rest_framework import status
# import App.globalsettings as gs
# from rest_framework.views import APIView
# from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
# from App.CNC_Calculation.MachineApi import MachineApi
# from App.CNC_Calculation.MachineStatus import downTimeReasonUpdater
# from App.OPCUA.ResultFormatter import DurationCalculatorFormatted
# from Webapp.TestAsyncApi import TestClass
#
#
# class getdowntimereason():
#     @staticmethod
#     async def get(request):
#         params = {k: v[0] for k, v in dict(request.GET).items()}
#         mode = params["mode"] if "mode" in params else ""
#         deviceID = params["deviceID"] if "deviceID" in params else ""
#
#         if mode != "web":
#             reasons = MachineApi.getDownTimeReason(deviceID)
#             if not reasons:
#                 jsonResponse = []
#             else:
#                 jsonList = []
#                 for reason in reasons:
#                     data = {
#                         "id": reason["DownCode"],
#                         "name": reason["DownCodeReason"]
#                     }
#                     jsonList.append(data)
#                 jsonResponse = json.dumps(jsonList, indent=4)
#             return HttpResponse(jsonResponse, "application/json")
#
#         else:
#             response = await TestClass.getData(request)
#             jsonResponse = json.dumps(response, indent=4)
#             return HttpResponse(jsonResponse, "application/json")
#
#
# class getdowntimecategory():
#     @staticmethod
#     async def get(request):
#         params = {k: v[0] for k, v in dict(request.GET).items()}
#         mode = params["mode"]
#         deviceID = params["deviceID"]
#         if mode != "web":
#             col = 'DownTimeCode'
#             reasons = MachineApi.getDownTimeCategory(deviceID, col)
#
#             jsonList = []
#             for reason in reasons:
#                 data = {
#                     "id": reason["_id"]["id"],
#                     "category": reason["_id"]["category"]
#                 }
#                 jsonList.append(data)
#             jsonResponse = json.dumps(jsonList, indent=4)
#             return HttpResponse(jsonResponse, "application/json")
#
#         else:
#             response = await TestClass.getData(request)
#             jsonResponse = json.dumps(response, indent=4)
#             return HttpResponse(jsonResponse, "application/json")
#
#
# class getdowntimedata():
#     @staticmethod
#     async def get(request):
#         params = {k: v[0] for k, v in dict(request.GET).items()}
#         fromDate = params["date"]
#         mode = params["mode"] if "mode" in params else ""
#         deviceID = params["deviceID"] if "deviceID" in params else ""
#
#         if mode != "web":
#             dateTime = datetime.datetime.strptime(fromDate, gs.OEE_MongoDBDateTimeFormat)
#             downTimeData = MachineApi.getDownTimeData(MachineID="MID-01", dateTime=dateTime)
#
#             downDataList = []
#             for index, downObj in enumerate(downTimeData):
#                 data = {
#                     "sno": str(index + 1),
#                     "id": str(downObj["_id"]),
#                     "date": datetime.datetime.strftime(downObj["StartTime"], gs.OEE_JsonDateFormat),
#                     "from": datetime.datetime.strftime(downObj["StartTime"], gs.OEE_OutputTimeFormat),
#                     "to": datetime.datetime.strftime(downObj["StopTime"], gs.OEE_OutputTimeFormat),
#                     "duration": DurationCalculatorFormatted(downObj["Duration"]),
#                     "downid": downObj["DownTimeCode"],
#                     "reason": downObj["Description"],
#                     "category": downObj["Category"],
#                     "machineID": deviceID,
#                     "mode": mode
#                 }
#                 downDataList.append(data)
#
#             jsonResponse = json.dumps(downDataList, indent=4)
#             return HttpResponse(jsonResponse, "application/json")
#
#         else:
#             response = await TestClass.getData(request)
#             for obj in response:
#                 obj["mode"] = "web"
#             jsonResponse = json.dumps(response, indent=4)
#             return HttpResponse(jsonResponse, "application/json")
#
#
# class postdowntimedata():
#     @staticmethod
#     async def post(request):
#
#         # database Insert function
#         data = request.body.decode("UTF-8")
#         requestData = json.loads(data)
#
#         mode = requestData[0]["mode"]
#
#         if mode != "web":
#             MachineApi.postDownTimeData(requestData)
#
#             ''' After Save function is completed This function is called for UI reflection. '''
#             thread = threading.Thread(target=downTimeReasonUpdater, args=())
#             thread.start()
#             return HttpResponse('success', "application/json")
#
#         else:
#             response = await TestClass.getData(request)
#             jsonResponse = json.dumps(response, indent=4)
#             return HttpResponse(jsonResponse, "application/json")
#
#
# class getqualitycategory():
#     @staticmethod
#     async def get(request):
#         params = {k: v[0] for k, v in dict(request.GET).items()}
#         mode = params["mode"]
#         deviceID = params["deviceID"]
#         if mode != "web":
#             reasons = MachineApi.getQualityCode(deviceID)
#             jsonList = []
#             for reason in reasons:
#                 data = {
#                     "id": reason["category"],
#                     "category": reason["category"]
#                 }
#                 jsonList.append(data)
#             jsonResponse = json.dumps(jsonList, indent=4)
#             print(jsonResponse)
#             return HttpResponse(jsonResponse, "application/json")
#
#         else:
#             response = await TestClass.getData(request)
#             jsonResponse = json.dumps(response, indent=4)
#             return HttpResponse(jsonResponse, "application/json")
#
#
# class getqualitycode():
#     @staticmethod
#     async def get(request):
#
#         params = {k: v[0] for k, v in dict(request.GET).items()}
#         mode = params["mode"]
#         deviceID = params["deviceID"]
#
#         if mode != "web":
#
#             reasons = MachineApi.getQualityCode(deviceID)
#             jsonList = []
#             for reason in reasons:
#                 data = {
#                     "code": reason["qualityCode"],
#                     "id": reason["category"],
#                     "description": reason["QualityDescription"]
#                 }
#                 jsonList.append(data)
#             jsonResponse = json.dumps(jsonList, indent=4)
#             return HttpResponse(jsonResponse, "application/json")
#
#         else:
#             response = await TestClass.getData(request)
#             jsonResponse = json.dumps(response, indent=4)
#             return HttpResponse(jsonResponse, "application/json")
#
#
# class getqualitydata():
#     @staticmethod
#     async def get(request):
#         params = {k: v[0] for k, v in dict(request.GET).items()}
#         fromDate = params["date"]
#         mode = params["mode"]
#         deviceID = params["deviceID"]
#
#         if mode != "web":
#             dateTime = datetime.datetime.strptime(fromDate, gs.OEE_MongoDBDateTimeFormat)
#             qualityData = MachineApi.getQualityData(dateTime=dateTime)
#
#             qualityDataList = []
#             for index, qualityObj in enumerate(qualityData):
#                 data = {
#                     "sno": str(index + 1),
#                     "id": str(qualityObj["_id"]),
#                     "date": qualityObj["date"],
#                     "productioncount": qualityObj["productioncount"],
#                     "qualitycode": qualityObj["qualitycode"],
#                     "qualityid": qualityObj["qualityid"],
#                     "qualitydescription": qualityObj["qualitydescription"],
#                     "category": qualityObj["category"],
#                     "machineID": deviceID,
#                     "mode": mode
#                 }
#                 qualityDataList.append(data)
#
#             jsonResponse = json.dumps(qualityDataList, indent=4)
#
#             return HttpResponse(jsonResponse, "application/json")
#
#         else:
#             response = await TestClass.getData(request)
#             for obj in response:
#                 obj["mode"] = "web"
#             jsonResponse = json.dumps(response, indent=4)
#             return HttpResponse(jsonResponse, "application/json")
#
#
# class postqualitydata():
#     @staticmethod
#     async def post(request):
#         data = request.body.decode("UTF-8")
#         requestData = json.loads(data)
#         mode = requestData[0]["mode"]
#
#         if mode != "web":
#             data = request.body.decode("UTF-8")
#             requestData = json.loads(data)
#             MachineApi.postQualityData(requestData)
#
#             # database Insert function
#             return HttpResponse('success', "application/json")
#
#         else:
#             response = await TestClass.getData(request)
#             jsonResponse = json.dumps(response, indent=4)
#             return HttpResponse(jsonResponse, "application/json")
#
#
# class getproductiondata():
#     @staticmethod
#     async def get(request):
#
#         params = {k: v[0] for k, v in dict(request.GET).items()}
#         mode = params["mode"]
#         deviceID = params["deviceID"]
#
#         if mode != "web":
#             productionData = MachineApi.getProductionData()
#             if not productionData:
#                 jsonResponse = []
#             else:
#                 productionDataList = []
#                 for index, obj in enumerate(productionData):
#                     data = {
#                         "sno": str(index + 1),
#                         "id": str(obj["_id"]),
#                         "shiftname": obj["Name"],
#                         "inseconds": obj["InSeconds"],
#                         "category": obj["Category"],
#                         "starttime": obj["ShiftStartTime"],
#                         "endtime": obj["ShiftEndTime"],
#                         "mantatory": obj["Mandatory"],
#                         "machineID": deviceID,
#                         "mode": mode
#                     }
#                     productionDataList.append(data)
#                 jsonResponse = json.dumps(productionDataList, indent=4)
#
#             return HttpResponse(jsonResponse, "application/json")
#
#         else:
#             response = await TestClass.getData(request)
#             for obj in response:
#                 obj["mode"] = "web"
#             jsonResponse = json.dumps(response, indent=4)
#             return HttpResponse(jsonResponse, "application/json")
#
#
# class postproductiondata():
#     @staticmethod
#     async def post(request):
#         data = request.body.decode("UTF-8")
#         requestData = json.loads(data)
#         mode = requestData[0]["mode"]
#
#         if mode != "web":
#             data = request.body.decode("UTF-8")
#             requestData = json.loads(data)
#
#             # database Insert function
#             MachineApi.postProductionData(requestData=requestData)
#             return HttpResponse("Successful", "application/json")
#
#         else:
#             response = await TestClass.getData(request)
#             jsonResponse = json.dumps(response, indent=4)
#             return HttpResponse(jsonResponse, "application/json")
#
#
# class getTotalProductionCount():
#     @staticmethod
#     async def get(request):
#
#         params = {k: v[0] for k, v in dict(request.GET).items()}
#         fromDate = params["date"]
#         mode = params["mode"]
#         deviceID = params["deviceID"]
#
#         if mode != "web":
#             dateTime = datetime.datetime.strptime(fromDate, gs.OEE_MongoDBDateTimeFormat)
#             qualityData = MachineApi.getQualityData(dateTime=dateTime)
#             totalCount = 0
#             for objects in qualityData:
#                 totalCount += int(float(objects["productioncount"]))
#             response = {"totalQuantity": str(totalCount)}
#             return JsonResponse(response, status=status.HTTP_200_OK, safe=False)
#
#         else:
#             response = await TestClass.getData(request)
#             jsonResponse = json.dumps(response, indent=4)
#             return HttpResponse(jsonResponse, "application/json")
