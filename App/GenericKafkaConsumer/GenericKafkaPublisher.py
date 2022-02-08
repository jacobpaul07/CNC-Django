import os
import sys

from confluent_kafka import Producer


def kafka_generic_publisher(kafka_server: str, kafka_topic: str, message):
    try:
        config = {'bootstrap.servers': kafka_server}
        # Create Producer instance
        producer = Producer(config)

        # Optional per-message delivery callback (triggered by poll() or flush())
        # when a message has been successfully delivered or permanently failed delivery (after retries).

        def delivery_callback(err, msg):
            if err:
                print('ERROR: Message failed delivery: {}'.format(err))

        # Produce data by selecting random values from these lists.
        producer.produce(topic=kafka_topic, value=message, callback=delivery_callback)
        print("Kafka Produced --> 'GENERIC'")
        # Block until the messages are sent.
        producer.poll(10000)
        producer.flush()

    except Exception as ex:
        print("Kafka Producer Error: ", ex)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
