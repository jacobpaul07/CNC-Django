import datetime
import json
from rest_framework.views import APIView
from django.http import HttpResponse, HttpResponseBadRequest

from App.CNC_Calculation.MachineStatus import StartTimer, downTimeParticularTimeDataUpdater
from App.CNC_Calculation.ReadFromExcel import OnMyWatch
from App.Json_Class import index as config, Edge
import App.globalsettings as appSetting
from App.Json_Class.EdgeDeviceProperties_dto import EdgeDeviceProperties
from App.OPCUA.JsonClass import LiveData
from App.OPCUA.KafkaConsumer import KafkaConsumerDefinition
from App.OPCUA.OPCUA import Opc_UA
from App.OPCUA.Output import StandardOutput
from Webapp.configHelper import ConfigOPCUAParameters, ConfigDataServiceProperties as PropertyConfig, \
    UpdateOPCUAParameters
import threading
from MongoDB_Main import Document as Doc
from App.OPCUA import index as reader


def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()


class ReadDeviceSettings(APIView):
    @staticmethod
    def get(request):
        jsonData: Edge = config.read_setting()
        jsonResponse = json.dumps(jsonData.to_dict(), indent=4)

        return HttpResponse(jsonResponse, "application/json")


class GetOeeData(APIView):
    @staticmethod
    def get(request):
        mode = request.GET.get("mode")
        if mode == "live":
            jsonData: LiveData = reader.read_setting()
            jsonResponse = json.dumps(jsonData.to_dict(), indent=4)
            return HttpResponse(jsonResponse, "application/json")
        elif mode == "specificdate":
            date = request.GET.get("date")
            print(date)
            # jsonResponse = Doc().SpecificDate_Document(Timestamp=date, filterField="Timestamp", col="Logs")
            rawDbLog = Doc().SpecificDate_Document(Timestamp=date, filterField="currentTime", col="LogsRawBackUp")
            print(rawDbLog)
            specificDate = datetime.datetime.strptime(date, appSetting.OEE_MongoDBDateTimeFormat)
            Output = []
            if rawDbLog:
                raw = rawDbLog[0]
                raw["Calculation_Data"] = downTimeParticularTimeDataUpdater(reasonCodeList=raw["reasonCodeList"],
                                                                            calculationData=raw["Calculation_Data"],
                                                                            specificDate=specificDate)

                Output = StandardOutput(result=raw["result"],
                                        OeeArgs=raw["OeeArgs"],
                                        Calculation_Data=raw["Calculation_Data"],
                                        ProductionPlan_Data=raw["ProductionPlan_Data"],
                                        OutputArgs=raw["OutputArgs"],
                                        DisplayArgs=raw["DisplayArgs"],
                                        currentTime=raw["currentTime"],
                                        availabilityJson=raw["availabilityJson"],
                                        reasonCodeList=raw["reasonCodeList"],
                                        productionFile=raw["productionFile"],
                                        qualityCategories=raw["qualityCategories"],
                                        defaultQualityCategories=raw["defaultQualityCategories"],
                                        )

            returndata = json.dumps(Output)
            return HttpResponse(returndata, "application/json")



class StartOpcService(APIView):
    @staticmethod
    def post(request):
        appSetting.startOPCUAService = True
        StartTimer()
        Opc_UA()
        # watch = OnMyWatch("D:/CNC-OEE/CNC-Django/App/Excel")
        # watch = OnMyWatch("/cnc/App/Excel/")
        # watch = OnMyWatch()
        # watch.run()
        thread = threading.Thread(target=KafkaConsumerDefinition, args=())
        thread.start()
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
        mode = requestData["mode"]
        deviceType: str = requestData["Type"]
        print("DeviceType:", deviceType)
        if deviceType == "OPCUAProperties" or deviceType == "MQTTProperties" or deviceType == "MongoDB" or \
                deviceType == "Redis":
            response = PropertyConfig().updateProperties(requestData=payLoadData, deviceType=deviceType)

        elif mode == "update" and deviceType == "OPCUAParameterMeasurementTags":
            response = ConfigOPCUAParameters().updateMeasurementTag(requestData=payLoadData["MeasurementTag"])

        elif (mode == "create" or mode == "delete") and (deviceType == "OPCUAParameterMeasurementTags"):
            response = UpdateOPCUAParameters().appendMeasurementTag(payLoadData["MeasurementTag"], mode)

        else:
            response = "No Protocol"
        #     ConfigTcpProperties().updateTcpPortProperties(requestData=payLoadData)

        if response == 'success':
            return HttpResponse(response, "application/json")
        else:
            return HttpResponseBadRequest(response)


class ReadSeriesData(APIView):
    @staticmethod
    def post(request):
        try:
            reqdata = request.body.decode("utf-8")
            requestData = json.loads(reqdata)
            col = "KafkaConsumer"
            from_date = requestData["from_date"]
            to_date = requestData["to_date"]
            topic = "test"
            data = Doc().Criteria_Document(col, from_date, to_date, topic)
            jsonResponse = data
            if data:
                return HttpResponse(jsonResponse, "application/json")
            else:
                response = {"No Data Found"}
                return HttpResponseBadRequest(response)

        except Exception as Ex:
            response = {"Error": "Please Enter the Date and time range Correctly",
                        "Exception": str(Ex)}
            jsonResponse = json.dumps(response, indent=4)
            return HttpResponseBadRequest(jsonResponse)
