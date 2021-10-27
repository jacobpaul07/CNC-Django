import datetime
import json
import threading
import time

from kafka import KafkaConsumer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from App.Json_Class.index import read_setting
from App.OPCUA.LiveJsonReadWrite import read_setting as reader
from App.OPCUA.ResultFormatter import DurationCalculatorFormatted
from App.OPCUA.index import read_temp_file
from MongoDB_Main import Document as Doc


def sentLiveData(data):
    text_data = json.dumps(data, indent=4)

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)("notificationGroup", {
        "type": "chat_message",
        "message": text_data
    })


def KafkaConsumerDefinition():
    data = read_setting()
    kafkaSetting = data.edgedevice.Service.Kafka
    topicName: str = kafkaSetting.topicName
    bootstrap_servers: str = kafkaSetting.bootstrap_servers
    group_id: str = kafkaSetting.group_id

    try:
        consumer = KafkaConsumer(topicName, group_id=group_id, bootstrap_servers=[bootstrap_servers],
                                 api_version=(0, 10, 1))
        for msg in consumer:
            receivedValue = msg.value.decode('utf8')
            loadValue = json.loads(receivedValue)
            dumpedValue = json.dumps(loadValue, indent=4)

            # filePath = './App/OPCUA/readWrite.json'
            # with open(filePath, "w") as f:
            #     f.write(dumpedValue)

            sentLiveData(loadValue)
            Doc().DB_Write(data=loadValue, col="Logs")

            print("Kafka Consumed Successfully")

    except Exception as ex:
        print("Error Occurred", ex)


# def LiveDataThread():
#
#     thread = threading.Thread(
#         target=sentLiveDataStreamer,
#         args=()
#     )
#     thread.start()
#
#
# def sentLiveDataStreamer():
#     readJson = reader()
#     tmpObj = read_temp_file()
#
#     machineStatus = tmpObj["machineStatus"]
#     timestamp = tmpObj["LastUpdateTime"]
#     ActiveHours = tmpObj["ActiveHours"]
#
#     currentTimeStamp = datetime.datetime.now()
#     LastUpdateTime = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
#     timeDifference = currentTimeStamp - LastUpdateTime
#     differ = datetime.datetime.strptime(ActiveHours, "%H:%M:%S")
#     activeHoursTmp = differ+timeDifference
#     activeHours = activeHoursTmp.strftime("%H:%M:%S")
#     activeHours_str = DurationCalculatorFormatted(activeHours)
#     if machineStatus == "True":
#         readJson["running"]["activeHours"] = activeHours_str
#     else:
#         readJson["downtime"]["activeHours"] = activeHours_str
#
#     text_data = json.dumps(readJson, indent=4)
#
#     channel_layer = get_channel_layer()
#     async_to_sync(channel_layer.group_send)("notificationGroup", {
#         "type": "chat_message",
#         "message": text_data
#     })
#     time.sleep(1)
#
#     thread = threading.Thread(
#         target=LiveDataThread,
#         args=()
#     )
#     thread.start()
