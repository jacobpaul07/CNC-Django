import json
from rest_framework.views import APIView
from django.http import HttpResponse, HttpResponseBadRequest
from App.Json_Class import index as config, Edge
import App.globalsettings as appSetting
from App.Json_Class.EdgeDeviceProperties_dto import EdgeDeviceProperties
from App.OPCUA.JsonClass import LiveData
from App.OPCUA.KafkaConsumer import KafkaConsumerDefinition, LiveDataThread
from App.OPCUA.OPCUA import Opc_UA
from Webapp.configHelper import ConfigOPCUAParameters, ConfigDataServiceProperties as PropertyConfig, \
    UpdateOPCUAParameters
import threading
from MongoDB_Main import Document as Doc
from App.OPCUA import index as reader


class getdowntimecategory(APIView):
    @staticmethod
    def get(request):
        category = [
            {"id": "1", "category": "plannedDowntime"},
            {"id": "2", "category": "UnplannedDowntime"}
        ]
        jsonResponse = json.dumps(category, indent=4)
        return HttpResponse(jsonResponse, "application/json")


class getdowntimedata(APIView):
    @staticmethod
    def get(request):
        downtimedata = [
            {
                "id": "1",
                "date": "2021-12-01",
                "from": "09:30 AM",
                "to": "10:30 AM",
                "duration": "01:00 hr",
                "downid": "01",
                "reason": "test",
                "category": ""
            },
            {
                "id": "2",
                "date": "2021-12-01",
                "from": "11:30 AM",
                "to": "12:30 AM",
                "duration": "01:00 hr",
                "downid": "01",
                "reason": "test",
                "category": ""
            }
        ]
        jsonResponse = json.dumps(downtimedata, indent=4)

        return HttpResponse(jsonResponse, "application/json")


class postdowntimedata(APIView):
    @staticmethod
    def post(request):

        data = request.body.decode("UTF-8")
        requestData = json.loads(data)

        # database Insert function

        return HttpResponse('success', "application/json")



class getqualitycategory(APIView):
    @staticmethod
    def get(request):
        category = [
            {"id": "1", "category": "good"},
            {"id": "2", "category": "bad"}
        ]
        jsonResponse = json.dumps(category, indent=4)

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
        jsonResponse = json.dumps(qualitydata, indent=4)

        return HttpResponse(jsonResponse, "application/json")


class postqualitydata(APIView):
    @staticmethod
    def post(request):
        data = request.body.decode("UTF-8")
        requestData = json.loads(data)

        # database Insert function
        return HttpResponse('success', "application/json")


class getproductiondata(APIView):
    @staticmethod
    def get(request):
        productiondata = [
            {
                "id": "1",
                "shiftname": "Shift001",
                "inseconds": "28800",
                "category": "Shift",
                "starttime": "06:00 AM 20-10-21",
                "endtime": "02:00 PM 20-10-21",
                "mantatory": "yes",
            },
            {
                "id": "2",
                "shiftname": "Shift002",
                "inseconds": "28800",
                "category": "Shift",
                "starttime": "04:00 AM 20-10-21",
                "endtime": "08:00 PM 20-10-21",
                "mantatory": "no",
            }
        ]
        jsonResponse = json.dumps(productiondata, indent=4)

        return HttpResponse(jsonResponse, "application/json")


class postproductiondata(APIView):
    @staticmethod
    def post(request):
        data = request.body.decode("UTF-8")
        requestData = json.loads(data)

        # database Insert function
        return HttpResponse("jsonResponse", "application/json")
