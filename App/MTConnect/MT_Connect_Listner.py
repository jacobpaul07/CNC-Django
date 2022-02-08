import os
import sys
import requests
import datetime
import threading

from lxml import objectify
from App.Json_Class.OPCUAProperties import OPCProperties
from App.OPCUA.OPCUA_Reader import format_data_and_send_to_kafka
from App.Json_Class.MTConnectParameters import MtConnectParameters


def read_mtconnect(properties: OPCProperties, parameters: MtConnectParameters, threadsCount, callback):
    current_time: datetime = datetime.datetime.now()
    print("TimeStamp", current_time)
    success = True
    datas_list: list = []
    if properties.Enable == "true" or properties.Enable == "True":
        url: str = properties.url

        try:
            request_data = get_data(url)
            request_data = request_data.decode('utf-8')

            # file_path = './App/SampleXML.xml'
            # with open(file_path) as f:
            #     request_data = f.read()
            #     f.close()

            mt_data = on_receive(data=request_data, parameters=parameters)

            # if success display registers
            # write last sequence number in json or database

            format_data_and_send_to_kafka(datas_list=mt_data, currentTime=current_time)

        except Exception as exception:
            success = False
            print("MTconnect Reader - Device is not Connected Error:", exception)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            f_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, f_name, exc_tb.tb_lineno)

        thread = threading.Thread(
            target=callback,
            args=(properties, parameters, threadsCount, datas_list, success)
        )
        thread.start()
    return datas_list


def get_data(url):
    r = requests.get(url, stream=False)
    return_data = r.content
    return return_data


def get_result(streams, parentpath, resultMode, attribName):
    try:
        main_object = streams
        paths = parentpath.split('->')
        for current_parent in paths:
            tmp_result = ""
            if ":" in current_parent:
                current_parent_tmp = current_parent.split(':')[0]
                filters = current_parent.split(':')[1]
                attribute_field = filters.split("=")[0]
                attribute_value = filters.split("=")[1]
                if main_object is not None:
                    for c_obj in main_object.getchildren():
                        c_tag_name = c_obj.tag.split('}')[1]
                        if current_parent_tmp == c_tag_name:
                            attr_val = c_obj.attrib[attribute_field]
                            if attr_val == attribute_value:
                                main_object = c_obj
                                tmp_result = "ok"
                                break

                if tmp_result == "":
                    return ""

            else:
                if hasattr(main_object, current_parent):
                    main_object = main_object[current_parent]
                else:
                    return ""

        if resultMode == "obj":
            return main_object

        elif resultMode == "text":
            text_result = main_object.text
            return text_result

        else:
            attr_result = main_object.attrib[attribName]
            return attr_result

    except Exception as exception:
        print("MT_Connect_Listener -> get_result Error:", exception)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        f_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, f_name, exc_tb.tb_lineno)


def mtconnect_status_formatter(required_xml_obj):
    device_name = list(filter(lambda x: (x["paramName"] == "Device Name"), required_xml_obj))[0]["result"]
    run_status = list(filter(lambda x: (x["paramName"] == "Run Status"), required_xml_obj))[0]["result"]
    active_alarm = list(filter(lambda x: (x["paramName"] == "Active Alarms"), required_xml_obj))[0]["result"]
    controller_mode = list(filter(lambda x: (x["paramName"] == "CONTROLLER MODE"), required_xml_obj))[0]["result"]
    haas = list(filter(lambda x: (x["paramName"] == "HAAS"), required_xml_obj))[0]["result"]
    downtime_reason_code = list(filter(lambda x: (x["paramName"] == "Downtime reason code"), required_xml_obj))[0][
        "result"]
    len_of_active_alarms = 0 if haas == "" else len(haas.getchildren())

    MACHINE_NAME = device_name
    STANDBY = True if run_status == "STOPPED" and active_alarm == "NO ACTIVE ALARMS" else False
    PRODUCTIVE = True if run_status == "ACTIVE" and active_alarm == "NO ACTIVE ALARMS" and controller_mode == "AUTOMATIC" else False
    SCHEDULED_DOWN = True if run_status == "STOPPED" and len_of_active_alarms > 0 else False
    UNSCHEDULED_DOWN = True if STANDBY is True and PRODUCTIVE is False else False
    MACHINE_STATUS_UP = True if active_alarm == "NO ACTIVE ALARMS" else False
    MACHINE_STATUS_DOWN = True if len_of_active_alarms > 0 else False
    DOWNTIME_REASON_CODE = downtime_reason_code

    DOWNTIME_REASON_CODE = "100" if STANDBY is True else DOWNTIME_REASON_CODE
    MACHINE_STATUS_UP = False if STANDBY is True else MACHINE_STATUS_UP

    obj = [
        {"name": "MACHINE_NAME", "refName": "MachineID", "value": MACHINE_NAME},
        {"name": "STANDBY", "refName": "", "value": STANDBY},
        {"name": "PRODUCTIVE", "refName": "", "value": PRODUCTIVE},
        {"name": "SCHEDULED_DOWN", "refName": "", "value": SCHEDULED_DOWN},
        {"name": "UNSCHEDULED_DOWN", "refName": "", "value": UNSCHEDULED_DOWN},
        {"name": "MACHINE_STATUS_UP", "refName": "PowerOnStatus", "value": MACHINE_STATUS_UP},
        {"name": "MACHINE_STATUS_DOWN", "refName": "DownTimeStatus", "value": MACHINE_STATUS_DOWN},
        {"name": "DOWNTIME_REASON_CODE", "refName": "DownTimeReasonCode", "value": DOWNTIME_REASON_CODE},
    ]

    return obj


def on_receive(data, parameters: MtConnectParameters):
    try:
        if data.startswith("--"):
            data = ""

        if data.startswith("Content"):
            data = ""

        if data.strip().endswith('</MTConnectStreams>'):
            xml = data
            xml = xml.encode('utf-8')
            root = objectify.fromstring(xml)
            streams = root.Streams
            result_object = []
            for param in parameters.MeasurementTag:
                param_name = param.param_name
                parent_path = param.parent_path
                return_value_mode = param.return_value_mode
                attribute_name = param.attribute_name
                result = get_result(streams=streams, parentpath=parent_path,
                                    resultMode=return_value_mode, attribName=attribute_name)
                temp_result = {"paramName": param_name, "result": result}
                result_object.append(temp_result)

            formatted_data = mtconnect_status_formatter(
                required_xml_obj=result_object)
            print(formatted_data)

            default_data = [{"DisplayName": "CycleStart", "value": "True"},
                            {"DisplayName": "DownTimeReasonCode", "value": "212"},
                            {"DisplayName": "DownTimeStatus", "value": "True"},
                            {"DisplayName": "EmergencyStop", "value": "True"},
                            {"DisplayName": "IdealCycleTime", "value": "60"},
                            {"DisplayName": "JobID", "value": "JID-01"},
                            {"DisplayName": "MachineID", "value": "MID01"},
                            {"DisplayName": "OperatorID", "value": "OID-02"},
                            {"DisplayName": "PowerOnStatus", "value": "True"},
                            {"DisplayName": "ProductionStart", "value": "True"},
                            {"DisplayName": "QualityCode", "value": "1"},
                            {"DisplayName": "ShiftID", "value": "SID-01"}]

            for data in formatted_data:
                ref_name = data["refName"]
                value = data["value"]

                if ref_name != "":
                    list(filter(lambda x: (x["DisplayName"] == ref_name), default_data))[0]["value"] = value

            return default_data

    except Exception as exception:
        print("MTconnect Reader - Device is not Connected Error:", exception)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        f_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, f_name, exc_tb.tb_lineno)
