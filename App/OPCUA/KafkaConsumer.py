import json
import os
import sys
import threading
import requests
# from argparse import ArgumentParser, FileType
import time

from confluent_kafka import Consumer, OFFSET_BEGINNING, KafkaError
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from App.Json_Class.index import read_setting
from App.OPCUA.OPCUA_Reader import publishToKafka
from App.OPCUA.index import readCalculation_file
import aiohttp
import asyncio

thread_Lock = threading.Lock()


def sentLiveData(data):
    text_data = json.dumps(data, indent=4)
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)("notifications", {
        "type": "chat_message",
        "message": text_data
    })


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
        "auto.offset.reset": "latest"
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
                sentLiveData(loadValue)
                consumer.commit()

            elif msg.error().code() == KafkaError._PARTITION_EOF:
                print('End of partition reached {0}/{1}'
                      .format(msg.topic(), msg.partition()))
            else:
                print('Error occured: {0}'.format(msg.error().str()))

    except KeyboardInterrupt and Exception as ex:
        consumer.close()
        print("Kafka Local Error:", ex)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fName = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fName, exc_tb.tb_lineno)
        thread = threading.Thread(
            target=KafkaConsumerDefinition,
            args=()
        )
        # Starting the Thread
        thread.start()

#
# def KafkaWebApiConsumerDefinition():
#     data = read_setting()
#     kafkaSetting = data.edgedevice.Service.Kafka
#     readCalculationDataJson = readCalculation_file()
#     deviceId = readCalculationDataJson["MachineId"]
#     topicName = 'request_' + deviceId
#     bootstrapServers: str = kafkaSetting.cloudServers
#
#     kafkaConsumerConfig = {
#         "bootstrap.servers": bootstrapServers,
#         "group.id": "python_example_group_2",
#         'enable.auto.commit': False,
#         'session.timeout.ms': 6000,
#         "auto.offset.reset": "latest",
#         "allow.auto.create.topics": True
#     }
#
#     # Create Consumer instance
#     apiConsumer = Consumer(kafkaConsumerConfig)
#     apiConsumer.subscribe([topicName])
#
#     try:
#         while True:
#             msg = apiConsumer.poll(0.1)
#             if msg is None:
#                 continue
#             elif not msg.error():
#                 receivedValue = msg.value().decode('utf-8')
#                 print("kafka 'Api Web' --> Consumed")
#                 loadValue = json.loads(receivedValue)
#                 apiConsumer.commit()
#                 # callApiAndResponseToWeb(loadValue)
#
#             elif msg.error().code() == KafkaError._PARTITION_EOF:
#                 print('End of partition reached {0}/{1}'
#                       .format(msg.topic(), msg.partition()))
#             else:
#                 print('Error occured: {0}'.format(msg.error().str()))
#
#     except KeyboardInterrupt and Exception as ex:
#         apiConsumer.close()
#         print("Kafka api Web Consumer Error:", ex)
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         fName = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#         print(exc_type, fName, exc_tb.tb_lineno)
#         thread = threading.Thread(
#             target=KafkaWebApiConsumerDefinition,
#             args=()
#         )
#
#         # Starting the Thread
#         thread.start()


# def callApiAndResponseToWeb(data):
#     try:
#         method = data["method"]
#         url = 'http://localhost:8008' + data["url"]
#
#         if method == "GET":
#             params = data["params"]
#             response = requests.get(url=url, params=params)
#             result = response.json()
#         else:
#             body = data["body"]
#             response = requests.post(url=url, data=body)
#             result = response.json()
#         jsonObject = read_setting()
#         kafkaJson = jsonObject.edgedevice.Service.Kafka
#         cloudServers: str = kafkaJson.cloudServers
#         topicName = 'response_' + data['deviceID']
#         data["result"] = result
#         kafkaMessage = json.dumps(data)
#         publishToKafka(kafkaServer=cloudServers, kafkaTopic=topicName, message=kafkaMessage)
#         print('web api response kafka publish')
#
#     except KeyboardInterrupt and Exception as ex:
#         print("Kafka api Web Consumer Error:", ex)
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         fName = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#         print(exc_type, fName, exc_tb.tb_lineno)