import datetime
import json
import os
import sys
import threading
from App.globalsettings import GlobalFormats
from confluent_kafka import Consumer, KafkaError
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from App.GeneralUtils.index import write_web_dashboard
from App.Json_Class.index import read_setting
from App.KafkaConsumer.LogsCreator import DbLogsCreatorThread
from Webapp.webDeviceStatusMonitor import read_device_status, write_device_status


def sent_live_data(data):
    try:
        web_streamed_data = json.dumps(data, indent=4, default=str)
        channel_layer = get_channel_layer()

        device_id = data["machineID"]
        formatted_device_id = device_id.replace("-", "_")
        async_to_sync(channel_layer.group_send)(formatted_device_id, {
            "type": "chat_message",
            "message": web_streamed_data
        })
    except Exception as ex:
        print("kafkaConsumerWeb -> sentLiveData Error:", ex)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, file_name, exc_tb.tb_lineno)


def sent_live_dashboard_data(dashboard_data):
    try:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)("webdashboard", {
            "type": "chat_message",
            "message": dashboard_data
        })
    except Exception as ex:
        print("kafkaConsumerWeb -> sent_live_dashboard_data Error:", ex)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, file_name, exc_tb.tb_lineno)


def update_device_status_list(data):
    try:
        current_time_str = str(datetime.datetime.now())
        device_id = data["machineID"]
        web_device_status_list = read_device_status()
        machine_status_data = web_device_status_list

        if len(machine_status_data) == 0:
            new_obj = {
                "deviceID": device_id,
                "lastUpdateTime": current_time_str,
                "runningStatus": "True"
            }
            machine_status_data.append(new_obj)
            print(machine_status_data)

        else:
            machine_list = list(filter(lambda x: (x["deviceID"] == device_id), machine_status_data))
            if len(machine_list) == 0:
                new_obj = {
                    "deviceID": device_id,
                    "lastUpdateTime": current_time_str,
                    "runningStatus": "True"
                }
                machine_status_data.append(new_obj)
            else:
                for index, machines in enumerate(machine_status_data):
                    if machine_status_data[index]["deviceID"] == device_id:
                        machine_status_data[index]["runningStatus"] = "True"
                        machine_status_data[index]["lastUpdateTime"] = current_time_str

        web_device_status_list = machine_status_data
        write_device_status(json_content=web_device_status_list)

    except Exception as ex:
        print("generate Dashboard Summary Error:", ex)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        f_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, f_name, exc_tb.tb_lineno)


def UpdateDeviceList(data):
    try:
        device_name = data["machineID"]
        device_id = data["machineID"].replace("-", "_")
        web_device_list_path = "./Webapp/JsonWeb/devicelist.json"
        with open(web_device_list_path, "r") as f:
            web_device_list = json.loads(f.read())

        if len(web_device_list) == 0:
            new_obj = {
                "deviceID": device_id,
                "deviceName": device_name,
            }
            web_device_list.append(new_obj)

        else:
            machine_list = list(filter(lambda x: (x["deviceID"] == device_id), web_device_list))
            if len(machine_list) == 0:
                new_obj = {
                    "deviceID": device_id,
                    "deviceName": device_name,
                }
                web_device_list.append(new_obj)

        with open(web_device_list_path, "w+") as webDeviceFile:
            json.dump(web_device_list, webDeviceFile, indent=4)
            webDeviceFile.close()
    except Exception as ex:
        print("Update Device List Error:", ex)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        f_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, f_name, exc_tb.tb_lineno)


def generateDashboardSummary(data):
    try:
        UpdateDeviceList(data)
        update_device_status_list(data)

        # power_on_status = data["powerOnStatus"]
        machine_status = data["machineStatus"]
        color = machine_status["color"]
        description = machine_status["name"]
        status_type = machine_status["statusType"]

        device_name = data["machineID"]
        device_id = data["machineID"].replace("-", "_")
        oee = data["oee"]
        web_dash_board_path = "./Webapp/JsonWeb/webDashBoard.json"
        with open(web_dash_board_path, "r") as f:
            web_dashboard_data = json.loads(f.read())

        # print(webDashboardData)
        machine_data = web_dashboard_data["machineData"]
        running_status = "Machine ON" if status_type == "running" else "Planned Stop" if status_type == "planned" else "UnPlanned Stop"

        if len(machine_data) == 0:
            GlobalFormats.new_device_added = True
            new_obj = {
                "machineID": device_id,
                "machineName": device_name,
                "status": running_status,
                "description": description,
                "color": color,
                "location": "Floor 2",
                "availability": oee["availability"],
                "performance": oee["performance"],
                "quality": oee["quality"],
                "oee": oee["oee"],
                "statusType": status_type
            }
            machine_data.append(new_obj)
            print(machine_data)

        else:
            machine_list = list(filter(lambda x: (x["machineID"] == device_id), machine_data))
            if len(machine_list) == 0:
                new_obj = {
                    "machineID": device_id,
                    "machineName": device_name,
                    "status": running_status,
                    "description": description,
                    "color": color,
                    "location": "Floor 2",
                    "availability": oee["availability"],
                    "performance": oee["performance"],
                    "quality": oee["quality"],
                    "oee": oee["oee"],
                    "statusType": status_type
                }
                machine_data.append(new_obj)
            else:
                for index, machines in enumerate(machine_data):
                    if machine_data[index]["machineID"] == device_id:
                        machine_data[index]["status"] = running_status
                        machine_data[index]["description"] = description
                        machine_data[index]["machineName"] = device_name
                        machine_data[index]["color"] = color
                        machine_data[index]["location"] = "Floor 2"
                        machine_data[index]["availability"] = oee["availability"]
                        machine_data[index]["performance"] = oee["performance"]
                        machine_data[index]["quality"] = oee["quality"]
                        machine_data[index]["oee"] = oee["oee"]
                        machine_data[index]["statusType"] = status_type

        web_dashboard_data["machineData"] = machine_data
        write_web_dashboard(web_dashboard_data)

        web_data_json_str = json.dumps(web_dashboard_data, indent=4)
        sent_live_dashboard_data(web_data_json_str)

    except Exception as ex:
        print("generate Dashboard Summary Error:", ex)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        f_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, f_name, exc_tb.tb_lineno)


def KafkaConsumerDefinitionWeb():
    data = read_setting()
    kafka_setting = data.edgedevice.Service.Kafka
    topic_name: str = kafka_setting.topicName
    cloud_servers: str = kafka_setting.cloudServers

    kafka_consumer_config = {
        "bootstrap.servers": cloud_servers,
        "group.id": "python_example_group_1",
        'enable.auto.commit': False,
        'session.timeout.ms': 6000,
        "auto.offset.reset": "latest",
        "allow.auto.create.topics": True,
        "api.version.request": False
        # 'default.topic.config': {'auto.offset.reset': 'latest'}
    }

    # Create Consumer instance
    consumer = Consumer(kafka_consumer_config)
    consumer.subscribe([topic_name])

    try:
        while True:
            msg = consumer.poll(0.1)
            if msg is None:
                continue
            elif not msg.error():
                received_value = msg.value().decode('utf-8')
                load_value = json.loads(received_value)
                DbLogsCreatorThread(loadValue=load_value)
                consumer.commit()

                print("kafka 'WEB' --> Consumed ")
                generateDashboardSummary(load_value)
                sent_live_data(load_value)

            elif msg.error().code() == KafkaError._PARTITION_EOF:
                print('End of partition reached {0}/{1}'
                      .format(msg.topic(), msg.partition()))
            else:
                print('Error occured: {0}'.format(msg.error().str()))

    except Exception as ex:
        print("Kafka Local Error:", ex)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        f_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, f_name, exc_tb.tb_lineno)

        consumer.close()
        thread = threading.Thread(
            target=KafkaConsumerDefinitionWeb,
            args=()
        )
        # Starting the Thread
        thread.start()
