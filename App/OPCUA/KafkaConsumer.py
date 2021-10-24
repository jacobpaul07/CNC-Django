import json
from kafka import KafkaConsumer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from App.Json_Class.index import read_setting


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
            loadValue: list = json.loads(receivedValue)
            sentLiveData(loadValue)

            print("Kafka Consumed Successfully")

    except Exception as ex:
        print("Error Occurred", ex)
