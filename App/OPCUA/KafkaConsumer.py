import json

from kafka import KafkaConsumer
from MongoDB_Main import Document as Doc
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import App.globalsettings as appsetting

bootstrap_servers = ['localhost:9092']
topicName = 'test'


def sentLiveData(data):
    text_data = json.dumps(data, indent=4)

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)("notificationGroup", {
        "type": "chat_message",
        "message": text_data
    })


def KafkaConsumerDefinition():
    try:
        consumer = KafkaConsumer(topicName, group_id='group1', bootstrap_servers=bootstrap_servers, api_version=(0, 10, 1))
        for msg in consumer:
            # print("Topic Name=%s,Message=%s" % (msg.topic, msg.value))
            # print('consumer data received')

            receivedValue = msg.value.decode('utf8')
            loadValue: list = json.loads(receivedValue)

            mongoData = {
                "topic": msg.topic,
                "partition": msg.partition,
                "offset": msg.offset,
                "timestamp": msg.timestamp,
                "timestamp_type": msg.timestamp_type,
                "key": msg.key,
                "value": loadValue,
                "headers": msg.headers,
                "checksum": msg.checksum,
                "serialized_key_size": msg.serialized_key_size,
                "serialized_value_size": msg.serialized_value_size,
                "serialized_header_size": msg.serialized_header_size
            }
            col = "KafkaConsumer"
            sentLiveData(mongoData)
            Doc().DB_Write(mongoData, col)
            print(mongoData)
            print("Kafka Consumed Successfully")
    except Exception as ex:
        print("Error Occurred", ex)



