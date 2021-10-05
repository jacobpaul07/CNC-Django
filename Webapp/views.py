import json
from rest_framework.views import APIView
from django.http import HttpResponse, HttpResponseBadRequest
from App.Json_Class import index as config, Edge
import App.globalsettings as appSetting
from App.Json_Class.EdgeDeviceProperties_dto import EdgeDeviceProperties
from App.OPCUA.OPCUA import Opc_UA
from Webapp.configHelper import ConfigOPCUAParameters, ConfigDataServiceProperties as PropertyConfig


class ReadDeviceSettings(APIView):
    @staticmethod
    def get(request):
        jsonData: Edge = config.read_setting()
        jsonResponse = json.dumps(jsonData.to_dict(), indent=4)

        return HttpResponse(jsonResponse, "application/json")


class StartOpcService(APIView):
    @staticmethod
    def post(request):
        appSetting.startOPCUAService = True
        Opc_UA()
        return HttpResponse('success', "application/json")


class StopOpcService(APIView):
    @staticmethod
    def post(request):
        appSetting.startOPCUAService = False
        Opc_UA()
        return HttpResponse('success', "application/json")


class ConfigGatewayProperties(APIView):
    @staticmethod
    def post(request):
        data = request.body.decode("UTF-8")
        requestData = json.loads(data)
        jsonData: Edge = config.read_setting()
        edgeDeviceProperties = jsonData.edgedevice.properties.to_dict()
        for key in requestData:
            value = requestData[key]
            for objectKey in edgeDeviceProperties:
                # for device_key in properties:
                if objectKey == key:
                    edgeDeviceProperties[key] = value

        jsonData.edgedevice.properties = EdgeDeviceProperties.from_dict(edgeDeviceProperties)
        updated_json_data = jsonData.to_dict()
        print(updated_json_data)
        config.write_setting(updated_json_data)

        return HttpResponse('success', "application/json")


class StartWebSocket(APIView):
    @staticmethod
    def post(request):
        appSetting.runWebSocket = True
        return HttpResponse('success', "application/json")


class StopWebSocket(APIView):
    @staticmethod
    def post(request):
        appSetting.runWebSocket = False

        return HttpResponse('success', "application/json")


class ConfigDataServiceProperties(APIView):
    @staticmethod
    def post(request):
        data = request.body.decode("utf-8")
        requestData = json.loads(data)
        payLoadData = requestData["data"]
        deviceType: str = requestData["Type"]
        print("DeviceType:", deviceType)
        if deviceType == "OPCUAProperties" or deviceType == "MQTTProperties" or deviceType == "MongoDB" or \
                deviceType == "Redis":
            response = PropertyConfig().updateProperties(requestData=payLoadData, deviceType=deviceType)

        elif deviceType == "OPCUAParameterMeasurementTags":
            response = ConfigOPCUAParameters().updateMeasurementTag(requestData=payLoadData["MeasurementTag"])

        elif deviceType == "Redis":
            response = None

        else:
            response = "No Protocol"
        #     ConfigTcpProperties().updateTcpPortProperties(requestData=payLoadData)

        if response == 'success':
            return HttpResponse(response, "application/json")
        else:
            return HttpResponseBadRequest(response)
