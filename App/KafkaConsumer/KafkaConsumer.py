import asyncio
import json
import os
import sys
import threading

from confluent_kafka import Consumer, KafkaError
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from App.Json_Class.index import read_setting
from App.KafkaConsumer.LogsCreator import DbLogsCreatorThread

thread_Lock = threading.Lock()


async def sentLiveData(data):
    try:
        text_data = json.dumps(data, indent=4)
        channel_layer = get_channel_layer()
        await channel_layer.group_send("notifications", {
            "type": "chat_message",
            "message": text_data
        })
    except Exception as ex:
        print("Kafka Local Error:", ex)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, file_name, exc_tb.tb_lineno)


def KafkaConsumerDefinition():
    data = read_setting()
    kafkaSetting = data.edgedevice.Service.Kafka
    topicName: str = kafkaSetting.topicName
    bootstrapServers: str = kafkaSetting.bootstrap_servers

    kafkaConsumerConfig = {
        "bootstrap.servers": bootstrapServers,
        "group.id": "python_example_group_1",
        'enable.auto.commit': False,
        'session.timeout.ms': 6000,
        "auto.offset.reset": "latest",
        "api.version.request": False
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
                print("kafka 'Local' --> Consumed")
                loadValue = json.loads(receivedValue)
                consumer.commit()

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(sentLiveData(loadValue))
                loop.close()

                # sentLiveData(loadValue)
                DbLogsCreatorThread(loadValue=loadValue)

            elif msg.error().code() == KafkaError._PARTITION_EOF:
                print('End of partition reached {0}/{1}'
                      .format(msg.topic(), msg.partition()))
            else:
                print('Error occured: {0}'.format(msg.error().str()))

    except KeyboardInterrupt and Exception as ex:
        consumer.close()
        print("Kafka Local Error:", ex)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, file_name, exc_tb.tb_lineno)
        thread = threading.Thread(
            target=KafkaConsumerDefinition,
            args=()
        )
        # Starting the Thread
        thread.start()

