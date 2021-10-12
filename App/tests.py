import time

from kafka import KafkaProducer

from kq import Queue


def add(a, b):
    return a + b


# Set up a Kafka producer.
producer = KafkaProducer(bootstrap_servers="127.0.0.1:9092")

# Set up a queue.
queue = Queue(topic="test", producer=producer)

# Enqueue a function call.
while True:
    job = queue.enqueue(add, 1, 2)
    time.sleep(5)
    print("done")

