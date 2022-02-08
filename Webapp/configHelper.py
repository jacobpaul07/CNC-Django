from App.Json_Class import index as config, Edge
from typing import List
from App.Json_Class.MQTTProperties_dto import MqttProperties
from App.Json_Class.MQTT_dto import mqtts
from App.Json_Class.MongoDB_dto import mongodb
from App.Json_Class.OPCMeasurementTags_dto import MeasurementTags
from App.Json_Class.OPCUAProperties import OPCProperties
from App.Json_Class.OPCUA_dto import opcua
from App.Json_Class.Redis_dto import redis


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
        json_data: Edge = config.read_setting()

        if deviceType == "OPCUAProperties":
            opcua_properties: opcua = json_data.edgedevice.DataService.OPCUA
            json_properties = opcua_properties.Properties.to_dict()
            updateGenericDeviceObject(requestData, json_properties)
            json_data.edgedevice.DataService.OPCUA.Properties = OPCProperties.from_dict(json_properties)

        elif deviceType == "MQTTProperties":
            mqtt: mqtts = json_data.edgedevice.DataService.MQTT
            json_properties = mqtt.Properties.to_dict()
            updateGenericDeviceObject(requestData, json_properties)
            json_data.edgedevice.DataService.MQTT.Properties = MqttProperties.from_dict(json_properties)

        elif deviceType == "MongoDB":
            properties: mongodb = json_data.edgedevice.Service.MongoDB
            json_properties = properties.to_dict()
            updateGenericDeviceObject(requestData, json_properties)
            json_data.edgedevice.Service.MongoDB = mongodb.from_dict(json_properties)

        elif deviceType == "Redis":
            properties: redis = json_data.edgedevice.Service.Redis
            json_properties = properties.to_dict()
            updateGenericDeviceObject(requestData, json_properties)
            json_data.edgedevice.Service.Redis = redis.from_dict(json_properties)
        updateConfig(json_data)
        return "success"


class ConfigOPCUAParameters:
    @staticmethod
    def updateMeasurementTag(requestData):
        json_data: Edge = config.read_setting()
        parameters: List[MeasurementTags] = json_data.edgedevice.DataService.OPCUA.Parameters.MeasurementTag
        for value in requestData:
            for i in range(len(parameters)):
                if parameters[i].DisplayName == value["DisplayName"]:
                    update_tag = parameters[i].to_dict()
                    result = updateGenericDeviceObject(value, update_tag)
                    parameters[i] = MeasurementTags.from_dict(result)
        json_data.edgedevice.DataService.OPCUA.Parameters.MeasurementTag = parameters
        updateConfig(json_data)
        return "success"


class UpdateOPCUAParameters:
    @staticmethod
    def appendMeasurementTag(requestData, mode):
        json_data: Edge = config.read_setting()
        parameters: List[MeasurementTags] = json_data.edgedevice.DataService.OPCUA.Parameters.MeasurementTag

        duplicate_count: int = 0
        no_data_count: bool = False

        for value in requestData:
            filtered = len(list(filter(lambda x: x.DisplayName == value["DisplayName"], parameters)))
            if mode == "create":
                duplicate_count = duplicate_count + filtered
                if filtered == 0:
                    new_record: MeasurementTags = MeasurementTags.from_dict(
                        {
                            "NameSpace": value["NameSpace"],
                            "Identifier": value["Identifier"],
                            "DisplayName": value["DisplayName"],
                            "InitialValue": value["InitialValue"],
                        }
                    )
                    parameters.append(new_record)

            elif mode == "delete":
                if filtered > 0:
                    delete_record: MeasurementTags = MeasurementTags.from_dict(
                        {
                            "NameSpace": value["NameSpace"],
                            "Identifier": value["Identifier"],
                            "DisplayName": value["DisplayName"],
                            "InitialValue": value["InitialValue"],
                        }
                    )
                    parameters.remove(delete_record)
                else:
                    no_data_count = True

        if duplicate_count > 0:
            return "Success But Some Duplicate Data was found --> Name should be Unique"
        elif no_data_count is True:
            return "Nodata Found"
        else:
            json_data.edgedevice.DataService.OPCUA.Parameters.MeasurementTag = parameters
            updateConfig(json_data)
            return "success"
