import datetime
import json
import threading
from rest_framework import status

from App.globalsettings import GlobalFormats
from rest_framework.views import APIView
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from App.CNC_Calculation.MachineApi import MachineApi
from App.CNC_Calculation.MachineStatus import down_time_reason_updater
from App.GeneralUtils.ResultFormatter import DurationCalculatorFormatted
from App.GeneralUtils.index import get_device_id


class GetDownTimeReason(APIView):
    @staticmethod
    def get(request):
        params = get_args_from_params(request)
        device_id = params["deviceID"]

        # calculationDataJson = readCalculation_file()
        # MachineId = calculationDataJson["MachineId"]
        reasons = MachineApi.get_down_time_reason(device_id)
        if not reasons:
            json_response = {"response": "No data available"}
            return HttpResponseBadRequest(json_response)
        else:
            json_list = []
            for reason in reasons:
                data = {
                    "id": reason["DownCode"],
                    "name": reason["DownCodeReason"]
                }
                json_list.append(data)
            json_response = json.dumps(json_list, indent=4)
        return HttpResponse(json_response, "application/json")


class GetDownTimeCategory(APIView):
    @staticmethod
    def get(request):
        params = get_args_from_params(request)
        device_id = params["deviceID"]

        col = 'DownTimeCode'
        reasons = MachineApi.get_down_time_category(device_id, col)

        json_list = []
        for reason in reasons:
            data = {
                "id": reason["_id"]["id"],
                "category": reason["_id"]["category"]
            }
            json_list.append(data)
        json_response = json.dumps(json_list, indent=4)
        return HttpResponse(json_response, "application/json")


class GetDownTimeData(APIView):
    @staticmethod
    def get(request):

        params = get_args_from_params(request)
        mode = params["mode"]
        device_id = params["deviceID"]
        from_date = params["from_date"]

        date_time = datetime.datetime.strptime(from_date, GlobalFormats.oee_mongo_db_date_time_format())
        down_time_data = MachineApi.get_down_time_data(machine_id=device_id, date_time=date_time)
        down_data_list = []
        for index, downObj in enumerate(down_time_data):
            data = {
                "sno": str(index + 1),
                "id": str(downObj["_id"]),
                "date": datetime.datetime.strftime(downObj["StartTime"], GlobalFormats.oee_json_date_format()),
                "from": datetime.datetime.strftime(downObj["StartTime"], GlobalFormats.oee_output_time_format()),
                "to": datetime.datetime.strftime(downObj["StopTime"], GlobalFormats.oee_output_time_format()),
                "duration": DurationCalculatorFormatted(downObj["Duration"]),
                "downid": downObj["DownTimeCode"],
                "reason": downObj["Description"],
                "category": downObj["Category"],
                "machineID": device_id,
                "mode": mode,
                "ReferenceID": downObj["ReferenceID"]
            }
            down_data_list.append(data)

        json_response = json.dumps(down_data_list, indent=4)
        return HttpResponse(json_response, "application/json")


class PostDownTimeData(APIView):
    @staticmethod
    def post(request):
        # database Insert function
        data = request.body.decode("UTF-8")
        request_data = json.loads(data)
        MachineApi.post_down_time_data(request_data)

        ''' After Save function is completed This function is called for UI reflection. '''
        thread = threading.Thread(target=down_time_reason_updater, args=())
        thread.start()

        return HttpResponse('success', "application/json")


class GetQualityCategory(APIView):
    @staticmethod
    def get(request):
        params = get_args_from_params(request)
        mode = params["mode"]
        device_id = params["deviceID"]

        if mode != "web":
            reasons = MachineApi.get_quality_code(device_id)
            json_list = []
            for reason in reasons:
                data = {
                    "id": reason["category"],
                    "category": reason["category"]
                }
                json_list.append(data)
            json_response = json.dumps(json_list, indent=4)
            return HttpResponse(json_response, "application/json")

        else:
            return HttpResponse("web", "application/json")


class GetQualityCode(APIView):
    @staticmethod
    def get(request):
        params = get_args_from_params(request)
        device_id = params["deviceID"]
        reasons = MachineApi.get_quality_code(device_id)
        json_list = []
        for reason in reasons:
            data = {
                "code": reason["qualityCode"],
                "id": reason["category"],
                "description": reason["QualityDescription"]
            }
            json_list.append(data)
        json_response = json.dumps(json_list, indent=4)
        return HttpResponse(json_response, "application/json")


class GetQualityData(APIView):
    @staticmethod
    def get(request):
        params = get_args_from_params(request)
        mode = params["mode"]
        device_id = params["deviceID"]
        from_date = params["from_date"]

        date_time = datetime.datetime.strptime(from_date, GlobalFormats.oee_mongo_db_date_time_format())
        quality_data = MachineApi.get_quality_data(date_time=date_time, machine_id=device_id)

        quality_data_list = []
        for index, qualityObj in enumerate(quality_data):
            data = {
                "sno": str(index + 1),
                "id": str(qualityObj["_id"]),
                "date": qualityObj["date"],
                "productioncount": qualityObj["productioncount"],
                "qualitycode": qualityObj["qualitycode"],
                "qualityid": qualityObj["qualityid"],
                "qualitydescription": qualityObj["qualitydescription"],
                "category": qualityObj["category"],
                "machineID": device_id,
                "mode": mode,
                "ReferenceID": qualityObj["ReferenceID"]
            }
            quality_data_list.append(data)

        json_response = json.dumps(quality_data_list, indent=4)

        return HttpResponse(json_response, "application/json")


class PostQualityData(APIView):
    @staticmethod
    def post(request):
        data = request.body.decode("UTF-8")
        request_data = json.loads(data)
        MachineApi.post_quality_data(request_data)

        # database Insert function
        return HttpResponse('success', "application/json")


class GetProductionData(APIView):
    @staticmethod
    def get(request):

        params = get_args_from_params(request)
        mode = params["mode"]
        device_id = params["deviceID"]

        production_data = MachineApi.get_production_data(machine_id=device_id)
        if not production_data:
            json_response = []
        else:
            production_data_list = []
            for index, obj in enumerate(production_data):
                data = {
                    "sno": str(index + 1),
                    "id": str(obj["_id"]),
                    "shiftname": obj["Name"],
                    "inseconds": obj["InSeconds"],
                    "category": obj["Category"],
                    "starttime": obj["ShiftStartTime"],
                    "endtime": obj["ShiftEndTime"],
                    "mantatory": obj["Mandatory"],
                    "machineID": device_id,
                    "mode": mode,
                    "ReferenceID": obj["ReferenceID"]
                }
                production_data_list.append(data)
            json_response = json.dumps(production_data_list, indent=4)

        return HttpResponse(json_response, "application/json")


class PostProductionData(APIView):
    @staticmethod
    def post(request):
        data = request.body.decode("UTF-8")
        request_data = json.loads(data)

        # database Insert function
        MachineApi.post_production_data(request_data=request_data)
        return HttpResponse("Successful", "application/json")


class GetTotalProductionCount(APIView):
    @staticmethod
    def get(request):

        params = {k: v[0] for k, v in dict(request.GET).items()}
        from_date = params["date"]
        mode = params["mode"]
        params_device_id = params["deviceID"]
        device_id = params_device_id if mode == "web" else get_device_id()
        device_id = device_id.replace("_", "-")

        date_time = datetime.datetime.strptime(from_date, GlobalFormats.oee_mongo_db_date_time_format())
        quality_data = MachineApi.get_quality_data(date_time=date_time, machine_id=device_id)
        total_count = 0
        for objects in quality_data:
            total_count += int(float(objects["productioncount"]))
        response = {"totalQuantity": str(total_count)}
        return JsonResponse(response, status=status.HTTP_200_OK, safe=False)


def get_args_from_params(request):
    params = {k: v[0] for k, v in dict(request.GET).items()}
    from_date = params["date"] if "date" in params else None
    mode = params["mode"]
    params_device_id = params["deviceID"]
    device_id = params_device_id if mode == "web" else get_device_id()
    device_id = device_id.replace("_", "-")

    params = {
        "from_date": from_date,
        "mode": mode,
        "deviceID": device_id
    }
    return params
