import json
from rest_framework.views import APIView
from django.http import HttpResponse, HttpResponseBadRequest
from App.Json_Class import index as config, Edge
import App.globalsettings as appsetting
from App.OPCUA.OPCUA import Opc_UA


class ReadDeviceSettings(APIView):

    def get(self, request):
        jsonData: Edge = config.read_setting()
        jsonResponse = json.dumps(jsonData.to_dict(), indent=4)

        return HttpResponse(jsonResponse, "application/json")


class StartOpcService(APIView):

    def post(self, request):
        appsetting.startOPCUAService = True
        Opc_UA()
        return HttpResponse('success', "application/json")


class StopOpcService(APIView):

    def post(self, request):
        appsetting.startOPCUAService = False
        Opc_UA()
        return HttpResponse('success', "application/json")


# class StartRtuService(APIView):
#
#     def post(self, request):
#         appsetting.startRtuService = True
#         modbus_rtu()
#
#         return HttpResponse('success', "application/json")
#
#
# class StopRtuService(APIView):
#
#     def post(self, request):
#         appsetting.startRtuService = False
#         modbus_rtu()
#
#         return HttpResponse('success', "application/json")
#
#
# class StartPpmpService(APIView):
#
#     def post(self, request):
#         appsetting.startPpmpService = True
#         start_ppmp_post()
#
#         return HttpResponse('success', "application/json")
#
#
# class StopPpmpService(APIView):
#     def post(self, request):
#         appsetting.startPpmpService = False
#         start_ppmp_post()
#
#         return HttpResponse('success', "application/json")
#
#
#
# class ConfigGatewayProperties(APIView):
#
#     def post(self, request):
#         data = request.body.decode("UTF-8")
#         requestData = json.loads(data)
#         jsonData: Edge = config.read_setting()
#         edgeDeviceProperties = jsonData.edgedevice.properties.to_dict()
#         for key in requestData:
#             value = requestData[key]
#             for objectKey in edgeDeviceProperties:
#                 # for device_key in properties:
#                 if objectKey == key:
#                     edgeDeviceProperties[key] = value
#
#         jsonData.edgedevice.properties = EdgeDeviceProperties.from_dict(edgeDeviceProperties)
#         updated_json_data = jsonData.to_dict()
#         print(updated_json_data)
#         config.write_setting(updated_json_data)
#
#         return HttpResponse('success', "application/json")
#
#
# class ConfigDataCenterProperties(APIView):
#
#     def post(self, request):
#         data = request.body.decode("utf-8")
#         requestData = json.loads(data)
#         payLoadData = requestData["data"]
#         deviceType: str = requestData["deviceType"]
#         print("DeviceType:", deviceType)
#         if deviceType == "COM1" or deviceType == "COM2":
#             ConfigComProperties().updateComPortProperties(requestData=payLoadData, portName=deviceType)
#         if deviceType == "TCP":
#             ConfigTcpProperties().updateTcpPortProperties(requestData=payLoadData)
#
#         return HttpResponse("Success", "application/json")
#
#
# class ConfigDataCenterDeviceProperties(APIView):
#
#     def post(self, request):
#         data = request.body.decode("utf-8")
#         requestData = json.loads(data)
#         payLoadData = requestData["data"]
#         deviceType: str = requestData["deviceType"]
#         deviceName: str = requestData["deviceName"]
#         print("DeviceType:", deviceType)
#         if deviceType == "COM1" or deviceType == "COM2":
#             response = ConfigComDevicesProperties().updateComDeviceProperties(payLoadData, deviceType, deviceName)
#             if response == 'success':
#                 return HttpResponse(response, "application/json")
#             else:
#                 return HttpResponseBadRequest(response)
#
#         if deviceType == "TCP":
#             response = ConfigTCPDevicesProperties().updateTCPDeviceProperties(payLoadData, deviceName)
#             if response == 'success':
#                 return HttpResponse(response, "application/json")
#             else:
#                 return HttpResponseBadRequest(response)
#
#
# class ConfigDataCenterDeviceIOTags(APIView):
#
#     def post(self, request):
#         data = request.body.decode("utf-8")
#         requestData = json.loads(data)
#         payLoadData = requestData["data"]
#         deviceType: str = requestData["deviceType"]
#         deviceName: str = requestData["deviceName"]
#         print("DeviceType:", deviceType)
#         if deviceType.startswith("COM") and len(deviceType) == 4:
#             response = ConfigDevicesIOTags().updateComIoTags(payLoadData, deviceType, deviceName)
#             if response == 'success':
#                 return HttpResponse(response, "application/json")
#             else:
#                 return HttpResponseBadRequest(response)
#
#         if deviceType == "TCP":
#             response = ConfigDevicesIOTags().updateTcpIoTags(payLoadData, deviceName)
#             if response == 'success':
#                 return HttpResponse(response, "application/json")
#             else:
#                 return HttpResponseBadRequest(response)
#
#
# class ConfigPpmpStations(APIView):
#
#     def post(self, request):
#         data = request.body.decode("utf-8")
#         requestData = json.loads(data)
#         payLoadData = requestData["data"]
#         deviceType: str = requestData["deviceType"]
#         print("DeviceType:", deviceType)
#         if deviceType == "PPMP":
#             response = ConfigPpmpStation().updateStations(payLoadData)
#             if response == 'success':
#                 return HttpResponse(response, "application/json")
#             else:
#                 return HttpResponseBadRequest(response)
#
class startWebSocket(APIView):

    def post(self, request):
        appsetting.runWebSocket = True
        # thread = threading.Thread(
        #     target=sendDataToWebSocket,
        #     args=())

        # Starting the Thread
        # thread.start()
        return HttpResponse('success', "application/json")


class stopWebSocket(APIView):

    def post(self, request):
        appsetting.runWebSocket = False

        return HttpResponse('success', "application/json")

#
# def sendDataToWebSocket():
#     while appsetting.runWebSocket:
#         text_data = str(datetime.datetime.now())
#
#         channel_layer = get_channel_layer()
#         async_to_sync(channel_layer.group_send)("notificationGroup", {
#             "type": "chat_message",
#             "message": text_data
#         })
#         time.sleep(10)
#
#
# class ConfigDataServiceProperties(APIView):
#
#     def post(self, request):
#         data = request.body.decode("utf-8")
#         requestData = json.loads(data)
#         payLoadData = requestData["data"]
#         deviceType: str = requestData["deviceType"]
#         print("DeviceType:", deviceType)
#         if deviceType == "PPMP":
#             response = ConfigPpmpProperties().updatePpmpProperties(requestData=payLoadData)
#         else:
#             response = "No PPMP"
#         #     ConfigTcpProperties().updateTcpPortProperties(requestData=payLoadData)
#
#         if response == 'success':
#             return HttpResponse(response, "application/json")
#         else:
#             return HttpResponseBadRequest(response)
