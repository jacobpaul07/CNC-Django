import datetime
import json
import threading
import time
from kafka import KafkaConsumer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from App.Json_Class.index import read_setting
from MongoDB_Main import Document as Doc

thread_Lock = threading.Lock()


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

            sentLiveData(loadValue)
            DbLogs(loadValue)
            # Doc().DB_Write(data=loadValue, col="Logs")

            print("Kafka Consumed Successfully")

    except Exception as ex:
        print("Error Occurred", ex)


def DbLogs(loadValue):

    thread = threading.Thread(
        target=DbLogsThread,
        args=[loadValue]
    )
    thread.start()


def DbLogsThread(loadValue):
    thread_Lock.acquire()
    timeStamp = datetime.datetime.now()
    loadValue["Timestamp"] = timeStamp
    col = "Logs"
    thread = threading.Thread(
        target=Doc().DB_Write,
        args=(loadValue, col)
    )
    thread.start()
    time.sleep(60)
    thread_Lock.release()
