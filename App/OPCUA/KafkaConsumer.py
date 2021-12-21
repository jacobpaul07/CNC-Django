import json
import os
import sys
import threading
# from argparse import ArgumentParser, FileType
from confluent_kafka import Consumer, OFFSET_BEGINNING, KafkaError
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from App.Json_Class.index import read_setting

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
    #
    #
    # # Create Consumer instance
    # consumer = Consumer(kafkaConsumerConfig)
    #
    # # Set up a callback to handle the '--reset' flag.
    # def reset_offset(consumer, partitions):
    #     # if args.reset:
    #     for p in partitions:
    #         p.offset = OFFSET_BEGINNING
    #     consumer.assign(partitions)
    #
    # # Subscribe to topic
    # consumer.subscribe([topicName], on_assign=reset_offset)
    #
    # # Poll for new messages from Kafka and print them.
    # try:
    #     while True:
    #         msg = consumer.poll(1.0)
    #         if msg is None:
    #             print("Waiting...")
    #         elif msg.error():
    #             print("ERROR: %s".format(msg.error()))
    #         else:
    #             # Extract the (optional) key and value, and print.
    #             receivedValue = msg.value().decode('utf-8')
    #             print("kafka Web Consumed")
    #             loadValue = json.loads(receivedValue)
    #             sentLiveData(loadValue)
    #
    # except KeyboardInterrupt and Exception as ex:
    #     consumer.close()
    #     print("Kafka Local Error:", ex)
    #     exc_type, exc_obj, exc_tb = sys.exc_info()
    #     fName = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    #     print(exc_type, fName, exc_tb.tb_lineno)
    #
    #     thread = threading.Thread(
    #         target=KafkaConsumerDefinition,
    #         args=()
    #     )
    #     # Starting the Thread
    #     thread.start()

    # data = read_setting()
    # kafkaSetting = data.edgedevice.Service.Kafka
    # topicName: str = kafkaSetting.topicName
    # bootstrap_servers: str = kafkaSetting.bootstrap_servers
    # kafkaConsumerConfig = {
    #     "bootstrap.servers": bootstrap_servers,
    #     "group.id": "python_example_group_1",
    #     "auto.offset.reset": "smallest",
    #     "enable.auto.commit": "false",
    # }
    # consumer = Consumer(kafkaConsumerConfig)
    #
    # try:
    #     while True:
    #         consumer.subscribe([topicName], on_assign=reset_offset)
    #         msg = consumer.poll(0)
    #         if msg is None:
    #             pass
    #             # Initial message consumption may take up to
    #             # `session.timeout.ms` for the consumer group to
    #             # rebalance and start consuming
    #
    #         elif msg.error():
    #             print("ERROR: %s".format(msg.error()))
    #         else:
    #             # Extract the (optional) key and value, and print.
    #             receivedValue = msg.value().decode('utf-8')
    #             print(receivedValue)
    #             print("Kafka Local Consumed")
    #             loadValue = json.loads(receivedValue)
    #             sentLiveData(loadValue)
    #
    # except KeyboardInterrupt and Exception as ex:
    #     consumer.close()
    #     print("Kafka Local Error:", ex)
    #     exc_type, exc_obj, exc_tb = sys.exc_info()
    #     fName = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    #     print(exc_type, fName, exc_tb.tb_lineno)
    #
    #     thread = threading.Thread(
    #         target=KafkaConsumerDefinition,
    #         args=()
    #     )
    #     # Starting the Thread
    #     thread.start()
