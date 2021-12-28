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
        # print("GenerateDashboard:",data)
        # Updating "deviceList.json" File
        UpdateDeviceList(data)
        powerOnStatus = data["powerOnStatus"]
        Machine_Status = data["machineStatus"]
        color = Machine_Status["color"]
        Description = Machine_Status["name"]
        statusType = Machine_Status["statusType"]

        deviceID = data["machineID"]
        oee = data["oee"]
        webDashBoardPath = "./Webapp/JsonWeb/webDashBoard.json"
        with open(webDashBoardPath, "r") as f:
            webDashboardData = json.loads(f.read())

        # print(webDashboardData)
        machineData = webDashboardData["machineData"]
        runningStatus = "Machine ON" if statusType == "running" else "Planned Stop" if statusType == "planned" else "UnPlanned Stop"

        if len(machineData) == 0:
            newObj = {
                "machineID": deviceID,
                "machineName": deviceID,
                "status": runningStatus,
                "description": Description,
                "color": color,
                "location": "Floor 2",
                "availability": oee["availability"],
                "performance": oee["performance"],
                "quality": oee["quality"],
                "oee": oee["oee"],
                "statusType": statusType
            }
            machineData.append(newObj)
            print(machineData)

        else:
            machineList = list(filter(lambda x: (x["machineID"] == deviceID), machineData))
            if len(machineList) == 0:
                newObj = {
                    "machineID": deviceID,
                    "machineName": deviceID,
                    "status": runningStatus,
                    "description": Description,
                    "color": color,
                    "location": "Floor 2",
                    "availability": oee["availability"],
                    "performance": oee["performance"],
                    "quality": oee["quality"],
                    "oee": oee["oee"],
                    "statusType": statusType
                }
                machineData.append(newObj)
            else:
                for index, machines in enumerate(machineData):
                    if machineData[index]["machineID"] == deviceID:
                        machineData[index]["status"] = runningStatus
                        machineData[index]["description"] = Description
                        machineData[index]["machineName"] = deviceID
                        machineData[index]["color"] = color
                        machineData[index]["location"] = "Floor 2"
                        machineData[index]["availability"] = oee["availability"]
                        machineData[index]["performance"] = oee["performance"]
                        machineData[index]["quality"] = oee["quality"]
                        machineData[index]["oee"] = oee["oee"]
                        machineData[index]["statusType"] = statusType

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
        "auto.offset.reset": "latest",
        "allow.auto.create.topics": True
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
                consumer.commit()
                print("kafka 'WEB' --> Consumed ")
                loadValue = json.loads(receivedValue)
                generateDashboardSummary(loadValue)
                sentLiveData(loadValue)

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
