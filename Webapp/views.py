import os
import json
import sys
import threading
import datetime
import dateutil.parser
import App.globalsettings as app_setting

from App.MTConnect.MT_Connect import initialize_mtconnect
from App.OPCUA.OPCUA import initialize_opcua
from App.GeneralUtils.JsonClass import LiveData
from rest_framework.views import APIView
from MongoDB_Main import Document as Doc
from App.OPCUA.Output import StandardOutput
from App.globalsettings import GlobalFormats
from App.GeneralUtils.GeneralUtilities import float_parser
from App.GeneralUtils import index as reader
from App.Json_Class import index as config, Edge
from App.KafkaConsumer.KafkaConsumer import KafkaConsumerDefinition
from App.OPCUA.OPCUA_Reader import closeAvailabilityDocument
from django.http import HttpResponse, HttpResponseBadRequest
from App.KafkaConsumer.KafkaConsumerWeb import KafkaConsumerDefinitionWeb
from App.Json_Class.EdgeDeviceProperties_dto import EdgeDeviceProperties
from App.CNC_Calculation.SpecificDateDowntimeCalc import GetUpdatedLiveData
from App.GenericKafkaConsumer.GenericKafkaConsume import kafka_generic_consumer
from Webapp.configHelper import ConfigOPCUAParameters, ConfigDataServiceProperties as PropertyConfig, \
    UpdateOPCUAParameters
from App.CNC_Calculation.MachineStatus import start_timer, down_time_particular_time_data_updater, \
    get_seconds_from_time_difference


def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()


class ReadDeviceSettings(APIView):
    @staticmethod
    def get(request):
        json_data: Edge = config.read_setting()
        json_response = json.dumps(json_data.to_dict(), indent=4)

        return HttpResponse(json_response, "application/json")


class GetOeeData(APIView):
    @staticmethod
    def get(request):

        try:
            datamode = request.GET.get("datamode")
            mode = request.GET.get("mode")
            if datamode == "live":
                json_data: LiveData = reader.read_setting()
                json_response = json.dumps(json_data.to_dict(), indent=4)
                return HttpResponse(json_response, "application/json")
            elif datamode == "specificdate":

                date = request.GET.get("date")
                specific_date = datetime.datetime.strptime(date, GlobalFormats.oee_mongo_db_date_time_format())
                from_date = specific_date
                to_date = specific_date
                calculation_data = reader.readDefaultCalculationJsonFile()
                if mode == "web":
                    machine_id = request.GET.get("deviceID").replace("_", "-")
                else:
                    machine_id = reader.readCalculation_file()["MachineId"]

                db_log = Doc().SpecificDate_Document(Timestamp=date, filterField="Timestamp", col="Logs", machineID=machine_id)
                reason_code_list = Doc().Read_Document(col="DownTimeCode")
                production_plan_history = Doc().read_production_history_document(from_date, to_date, machine_id)
                production_shifts = list(filter(lambda x: (x["Category"] == "SHIFT"), production_plan_history))

                if len(production_shifts) > 0:
                    production_first_shift = production_shifts[0]
                    production_from_date_time = dateutil.parser.parse(production_first_shift["ShiftStartTime"])
                else:
                    production_from_date_time = from_date

                if db_log:
                    raw = db_log[0]
                    # return HttpResponse(json.dumps(raw, default=str), "application/json")
                    recycle_time = raw["RecycleHour"]
                    doc_time = raw["Timestamp"]

                    # convert raw to livedata
                    raw_json = json.loads(json.dumps(raw, default=str), object_hook=float_parser)
                    original_live_data = LiveData.from_dict(raw_json)

                    # fresh calculation data we should fill needed data
                    calculation_data["RecycleTime"] = recycle_time
                    calculation_data["MachineId"] = machine_id

                    read_availability_doc = Doc().Read_Availability_Document_History(production_from_date_time, to_date, machine_id)
                    read_availability_doc = closeAvailabilityDocument(read_availability_doc, specific_date)
                    reason_code_list = json.loads(json.dumps(reason_code_list, default=str))
                    read_availability_doc = json.loads(json.dumps(read_availability_doc, default=str))
                    result = down_time_particular_time_data_updater(reason_code_list=reason_code_list,
                                                                    calculation_data=calculation_data,
                                                                    availability_json=read_availability_doc,
                                                                    specific_date=specific_date)
                    calculate_result = result["result"]
                    read_calculation_data_json_new = result["calculationData"]
                    availability_json_new = result["availabilityJson"]

                    down_duration = get_seconds_from_time_difference(calculate_result["TotalDownTime"])
                    down_time_duration_formatted = calculate_result["TotalDownTImeFormatted"]

                    read_calculation_data_json_new["Down"]["ActiveHours"] = calculate_result["TotalDownTime"]
                    output_args = {
                        "DownDuration": down_duration,
                        "DownTimeDurationFormatted": down_time_duration_formatted,
                    }

                    output = GetUpdatedLiveData(orginalData=original_live_data,
                                                Calculation_Data=read_calculation_data_json_new,
                                                currentTime=doc_time,
                                                availabilityJson=availability_json_new,
                                                reasonCodeList=reason_code_list,
                                                OutputArgs=output_args,
                                                recycleHour=recycle_time
                                                )
                    return_data = json.dumps(output)
                    return HttpResponse(return_data, "application/json")

                else:
                    bad_response = "No Data Available at " + date
                    print(bad_response)
                    return HttpResponseBadRequest(bad_response)

        except Exception as ex:
            print("Error in WebApp/Views.py -> GetOeeData", ex)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, file_name, exc_tb.tb_lineno)


class GetOeeDataOld(APIView):
    @staticmethod
    def get(request):
        params = {k: v[0] for k, v in dict(request.GET).items()}
        mode = params["mode"]
        device_id = params["deviceID"]
        if mode == "live":
            json_data: LiveData = reader.read_setting()
            json_response = json.dumps(json_data.to_dict(), indent=4)
            return HttpResponse(json_response, "application/json")
        elif mode == "specificdate":
            date = params["date"]
            # jsonResponse = Doc().SpecificDate_Document(Timestamp=date, filterField="Timestamp", col="Logs")
            raw_db_log = Doc().SpecificDate_Document(Timestamp=date, filterField="currentTime", col="LogsRawBackUp",
                                                     machineID=device_id)
            specific_date = datetime.datetime.strptime(date, app_setting.OEE_MongoDBDateTimeFormat)
            output = []
            if raw_db_log:
                raw = raw_db_log[0]
                result = down_time_particular_time_data_updater(reason_code_list=raw["reasonCodeList"],
                                                                calculation_data=raw["Calculation_Data"],
                                                                availability_json=raw["availabilityJson"],
                                                                specific_date=specific_date)

                raw["Calculation_Data"] = result["calculationData"]
                raw["availabilityJson"] = result["availabilityJson"]
                recycle_hour = 6
                output = StandardOutput(result=raw["result"],
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
                                        recycleHour=recycle_hour
                                        )

            return_data = json.dumps(output)
            return HttpResponse(return_data, "application/json")


class StartOpcService(APIView):
    @staticmethod
    def post(request):
        if os.environ['ApplicationMode'] != "web":
            StartOpcService.startOPC()
        else:
            StartOpcService.startKafkaWeb()

        return HttpResponse('success', "application/json")

    @staticmethod
    def startOPC():
        app_setting.startOPCUAService = True
        GlobalFormats.startOPCUAService = True
        start_timer()
        initialize_opcua()
        initialize_mtconnect()
        # KafkaConsumerDefinition()
        thread = threading.Thread(target=KafkaConsumerDefinition, args=())
        thread.start()

    @staticmethod
    def startConsumeWebApiRequest():
        # KafkaConsumerDefinition()
        mode = "mobile"
        thread = threading.Thread(target=kafka_generic_consumer, args=[mode])
        thread.start()

    @staticmethod
    def startConsumeDeviceApiRequest():
        # KafkaConsumerDefinition()
        mode = "web"
        thread = threading.Thread(target=kafka_generic_consumer, args=[mode])
        thread.start()

    @staticmethod
    def startKafkaWeb():
        thread = threading.Thread(target=KafkaConsumerDefinitionWeb, args=())
        thread.start()


class StopOpcService(APIView):
    @staticmethod
    def post(request):
        app_setting.startOPCUAService = False
        initialize_opcua()
        return HttpResponse('success', "application/json")


class ConfigGatewayProperties(APIView):
    @staticmethod
    def post(request):
        data = request.body.decode("UTF-8")
        request_data = json.loads(data)
        json_data: Edge = config.read_setting()
        edge_device_properties = json_data.edgedevice.properties.to_dict()
        for key in request_data:
            value = request_data[key]
            for objectKey in edge_device_properties:
                # for device_key in properties:
                if objectKey == key:
                    edge_device_properties[key] = value

        json_data.edgedevice.properties = EdgeDeviceProperties.from_dict(edge_device_properties)
        updated_json_data = json_data.to_dict()
        config.write_setting(updated_json_data)

        return HttpResponse('success', "application/json")


class StartWebSocket(APIView):
    @staticmethod
    def post(request):
        app_setting.runWebSocket = True
        return HttpResponse('success', "application/json")


class StopWebSocket(APIView):
    @staticmethod
    def post(request):
        app_setting.runWebSocket = False

        return HttpResponse('success', "application/json")


class ConfigDataServiceProperties(APIView):
    @staticmethod
    def post(request):
        data = request.body.decode("utf-8")
        requestData = json.loads(data)
        payLoadData = requestData["data"]
        mode = requestData["mode"]
        device_type: str = requestData["Type"]
        print("DeviceType:", device_type)
        if device_type == "OPCUAProperties" or device_type == "MQTTProperties" or device_type == "MongoDB" or \
                device_type == "Redis":
            response = PropertyConfig().updateProperties(requestData=payLoadData, deviceType=device_type)

        elif mode == "update" and device_type == "OPCUAParameterMeasurementTags":
            response = ConfigOPCUAParameters().updateMeasurementTag(requestData=payLoadData["MeasurementTag"])

        elif (mode == "create" or mode == "delete") and (device_type == "OPCUAParameterMeasurementTags"):
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
            request_body = request.body.decode("utf-8")
            request_data = json.loads(request_body)
            col = "KafkaConsumer"
            from_date = request_data["from_date"]
            to_date = request_data["to_date"]
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
