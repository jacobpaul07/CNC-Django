import json
from rest_framework.views import APIView
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse


class postlogindata(APIView):
    @staticmethod
    def post(request):
        defaultData = {
            "access_token": "MTQ0NjJkZmQ5OTM2NDE1ZTZjNGZmZjI3",
            "token_type": "bearer",
            "expires_in": 3600,
            "refresh_token": "IwOGYzYTlmM2YxOTQ5MGE3YmNmMDFkNTVk",
        }
        jsonResponse = json.dumps(defaultData, indent=4)
        return HttpResponse(jsonResponse, "application/json")


class getdashboarddata(APIView):
    @staticmethod
    def get(request):
        f = open('./Webapp/JsonWeb/webDashBoard.json', "r")
        data = json.loads(f.read())
        jsonResponse = json.dumps(data, indent=4)
        return HttpResponse(jsonResponse, "application/json")


class getdevicesList(APIView):
    @staticmethod
    def get(request):
        f = open('./Webapp/JsonWeb/devicelist.json', "r")
        data = json.loads(f.read())
        jsonResponse = json.dumps(data, indent=4)
        return HttpResponse(jsonResponse, "application/json")
