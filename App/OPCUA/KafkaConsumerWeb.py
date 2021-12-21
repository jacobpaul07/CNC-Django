import json
import os
import sys
import threading
# from argparse import ArgumentParser, FileType
from confluent_kafka import Consumer, OFFSET_BEGINNING, KafkaError
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from App.Json_Class.index import read_setting


def sentLiveData(data):
    webStreamedData = json.dumps(data, indent=4)
    channel_layer = get_channel_layer()

    deviceID = data["machineID"]
    async_to_sync(channel_layer.group_send)(deviceID, {
        "type": "chat_message",
        "message": webStreamedData
    })


def sentLiveDashboardData(DashboardData):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)("webdashboard", {
        "type": "chat_message",
        "message": DashboardData
    })


def UpdateDeviceList(data):
    try:
        deviceID = data["machineID"]
        webDeviceListPath = "./Webapp/JsonWeb/devicelist.json"
        with open(webDeviceListPath, "r") as f:
            webDeviceList = json.loads(f.read())

        if len(webDeviceList) == 0:
            newObj = {
                "deviceID": deviceID,
                "deviceName": deviceID,
            }
            webDeviceList.append(newObj)

        else:
            machineList = list(filter(lambda x: (x["deviceID"] == deviceID), webDeviceList))
            if len(machineList) == 0:
                newObj = {
                    "deviceID": deviceID,
                    "deviceName": deviceID,
                }
                webDeviceList.append(newObj)

        with open(webDeviceListPath, "w+") as webDeviceFile:
            json.dump(webDeviceList, webDeviceFile, indent=4)
            webDeviceFile.close()
    except Exception as ex:
        print("Update Device List Error:", ex)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fName = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fName, exc_tb.tb_lineno)


def generateDashboardSummary(data):
    try:
        # Updating "deviceList.json" File
        UpdateDeviceList(data)

        deviceID = data["machineID"]
        oee = data["oee"]
        webDashBoardPath = "./Webapp/JsonWeb/webDashBoard.json"
        with open(webDashBoardPath, "r") as f:
            webDashboardData = json.loads(f.read())

        machineData = webDashboardData["machineData"]
        if len(machineData) == 0:
            newObj = {
                "machineID": deviceID,
                "machineName": deviceID,
                "status": "Running",
                "location": "Floor 2",
                "availability": oee["availability"],
                "performance": oee["performance"],
                "quality": oee["quality"],
                "oee": oee["oee"]
            }
            machineData.append(newObj)

        else:
            machineList = list(filter(lambda x: (x["machineID"] == deviceID), machineData))
            if len(machineList) == 0:
                newObj = {
                    "machineID": deviceID,
                    "machineName": deviceID,
                    "status": "Running",
                    "location": "Floor 2",
                    "availability": oee["availability"],
                    "performance": oee["performance"],
                    "quality": oee["quality"],
                    "oee": oee["oee"]
                }
                machineData.append(newObj)
            else:
                for index, machines in enumerate(machineData):
                    if machineData[index]["machineID"] == deviceID:
                        machineData[index]["status"] = "Running"
                        machineData[index]["machineName"]: deviceID
                        machineData[index]["status"] = "Running"
                        machineData[index]["location"] = "Floor 2"
                        machineData[index]["availability"] = oee["availability"]
                        machineData[index]["performance"] = oee["performance"]
                        machineData[index]["quality"] = oee["quality"]
                        machineData[index]["oee"] = oee["oee"]

            webDashboardData["machineData"] = machineData

            with open(webDashBoardPath, "w+") as webDashFile:
                json.dump(webDashboardData, webDashFile, indent=4)
                webDashFile.close()

            webDataJsonStr = json.dumps(webDashboardData, indent=4)
            sentLiveDashboardData(webDataJsonStr)
    except Exception as ex:
        print("generate Dashboard Summary Error:", ex)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fName = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fName, exc_tb.tb_lineno)


def KafkaConsumerDefinitionWeb():
    data = read_setting()
    kafkaSetting = data.edgedevice.Service.Kafka
    topicName: str = kafkaSetting.topicName
    cloudServers: str = kafkaSetting.cloudServers

    kafkaConsumerConfig = {
        "bootstrap.servers": cloudServers,
        "group.id": "python_example_group_1",
        'enable.auto.commit': False,
        'session.timeout.ms': 6000,
        "auto.offset.reset": "latest"
        # 'default.topic.config': {'auto.offset.reset': 'latest'}
    }

    # Create Consumer instance
    consumer = Consumer(kafkaConsumerConfig)
    consumer.subscribe([topicName])

    try:
        while True:
            msg = consumer.poll(0.1)
            if msg is None:
                continue
            elif not msg.error():
                receivedValue = msg.value().decode('utf-8')
                print("kafka 'WEB' --> Consumed ")
                loadValue = json.loads(receivedValue)
                generateDashboardSummary(loadValue)
                sentLiveData(loadValue)
                consumer.commit()

            elif msg.error().code() == KafkaError._PARTITION_EOF:
                print('End of partition reached {0}/{1}'
                      .format(msg.topic(), msg.partition()))
            else:
                print('Error occured: {0}'.format(msg.error().str()))

    except Exception as ex:
        print("Kafka Local Error:", ex)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fName = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fName, exc_tb.tb_lineno)

        consumer.close()
        thread = threading.Thread(
            target=KafkaConsumerDefinitionWeb,
            args=()
        )
        # Starting the Thread
        thread.start()

