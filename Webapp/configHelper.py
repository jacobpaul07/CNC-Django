from App.Json_Class import index as config, Edge
from typing import List
from App.Json_Class.MQTTProperties_dto import MqttProperties
from App.Json_Class.MQTT_dto import mqtts
from App.Json_Class.MongoDB_dto import mongodb
from App.Json_Class.OPCMeasurementTags_dto import MeasurementTags
from App.Json_Class.OPCUAProperties import OPCProperties
from App.Json_Class.OPCUA_dto import opcua
from App.Json_Class.Redis_dto import redis
from App.Json_Class.Services_dto import Services
import json


def updateGenericDeviceObject(requestData, jsonProperties):
    for key in requestData:
        value = requestData[key]
        for objectKey in jsonProperties:
            # for device_key in properties:
            if objectKey == key:
                jsonProperties[key] = value
    return jsonProperties


def updateConfig(jsonData):
    updated_json_data = jsonData.to_dict()
    config.write_setting(updated_json_data)


class ConfigDataServiceProperties:
    @staticmethod
    def updateProperties(requestData, deviceType):
        jsonData: Edge = config.read_setting()

        if deviceType == "OPCUAProperties":
            OPCUA: opcua = jsonData.edgedevice.DataService.OPCUA
            jsonProperties = OPCUA.Properties.to_dict()
            updateGenericDeviceObject(requestData, jsonProperties)
            jsonData.edgedevice.DataService.OPCUA.Properties = OPCProperties.from_dict(jsonProperties)

        elif deviceType == "MQTTProperties":
            MQTT: mqtts = jsonData.edgedevice.DataService.MQTT
            jsonProperties = MQTT.Properties.to_dict()
            updateGenericDeviceObject(requestData, jsonProperties)
            jsonData.edgedevice.DataService.MQTT.Properties = MqttProperties.from_dict(jsonProperties)

        elif deviceType == "MongoDB":
            Properties: mongodb = jsonData.edgedevice.Service.MongoDB
            jsonProperties = Properties.to_dict()
            updateGenericDeviceObject(requestData, jsonProperties)
            jsonData.edgedevice.Service.MongoDB = mongodb.from_dict(jsonProperties)

        elif deviceType == "Redis":
            Properties: redis = jsonData.edgedevice.Service.Redis
            jsonProperties = Properties.to_dict()
            updateGenericDeviceObject(requestData, jsonProperties)
            jsonData.edgedevice.Service.Redis = redis.from_dict(jsonProperties)
        updateConfig(jsonData)
        return "success"


class ConfigOPCUAParameters:
    @staticmethod
    def updateMeasurementTag(requestData):
        jsonData: Edge = config.read_setting()
        parameters: List[MeasurementTags] = jsonData.edgedevice.DataService.OPCUA.Parameters.MeasurementTag
        for value in requestData:
            for i in range(len(parameters)):
                if parameters[i].DisplayName == value["DisplayName"]:
                    updateTag = parameters[i].to_dict()
                    result = updateGenericDeviceObject(value, updateTag)
                    parameters[i] = MeasurementTags.from_dict(result)
        jsonData.edgedevice.DataService.OPCUA.Parameters.MeasurementTag = parameters
        updateConfig(jsonData)
        return "success"


class UpdateOPCUAParameters:
    @staticmethod
    def appendMeasurementTag(requestData, mode):
        jsonData: Edge = config.read_setting()
        parameters: List[MeasurementTags] = jsonData.edgedevice.DataService.OPCUA.Parameters.MeasurementTag

        duplicateCount: int = 0
        noDataCount: bool = False

        for value in requestData:
            filtered = len(list(filter(lambda x: x.DisplayName == value["DisplayName"], parameters)))
            if mode == "create":
                duplicateCount = duplicateCount + filtered
                if filtered == 0:
                    newRecord: MeasurementTags = MeasurementTags.from_dict(
                        {
                            "NameSpace": value["NameSpace"],
                            "Identifier": value["Identifier"],
                            "DisplayName": value["DisplayName"],
                            "InitialValue": value["InitialValue"],
                        }
                    )
                    parameters.append(newRecord)

            elif mode == "delete":
                if filtered > 0:
                    deleteRecord: MeasurementTags = MeasurementTags.from_dict(
                        {
                            "NameSpace": value["NameSpace"],
                            "Identifier": value["Identifier"],
                            "DisplayName": value["DisplayName"],
                            "InitialValue": value["InitialValue"],
                        }
                    )
                    parameters.remove(deleteRecord)
                else:
                    noDataCount = True

        if duplicateCount > 0:
            return "Success But Some Duplicate Data was found --> Name should be Unique"
        elif noDataCount is True:
            return "Nodata Found"
        else:
            jsonData.edgedevice.DataService.OPCUA.Parameters.MeasurementTag = parameters
            updateConfig(jsonData)
            return "success"
