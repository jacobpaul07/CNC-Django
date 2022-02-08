import json
from rest_framework.views import APIView
from django.http import HttpResponse, HttpResponseBadRequest

from App.GeneralUtils.index import readWebDashBoard, readDeviceList


class GetDashboardData(APIView):
    @staticmethod
    def get(request):
        try:
            data = readWebDashBoard()
            json_response = json.dumps(data, indent=4)
            return HttpResponse(json_response, "application/json")
        except Exception as ex:
            print("Error -> GetDashboardData ", ex)
            json_response = {"Response": "No Data Available !!"}
            return HttpResponseBadRequest(json_response)


class GetDevicesList(APIView):
    @staticmethod
    def get(request):
        try:
            data = readDeviceList()
            json_response = json.dumps(data, indent=4)
            return HttpResponse(json_response, "application/json")
        except Exception as ex:
            print("Error -> GetDevicesList ", ex)
            json_response = {"Response": "No Data Available !!"}
            return HttpResponseBadRequest(json_response)
