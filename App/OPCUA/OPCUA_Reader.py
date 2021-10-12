import json
import threading
from datetime import datetime
from App.Json_Class.index import read_setting
from kafka import KafkaProducer
from opcua import Client
from App.Json_Class.OPCUAParameters import OPCParameters
from App.Json_Class.OPCUAProperties import OPCProperties


def ReadOPCUA(Properties: OPCProperties, OPCTags: OPCParameters, threadsCount, callback):

    success = True
    datasList = []
    # producer = KafkaProducer(bootstrap_servers="localhost:9092")
    jsonObject = read_setting()
    kafkaJson = jsonObject.edgedevice.Service.Kafka
    bootstrap_servers: str = kafkaJson.bootstrap_servers
    producer = KafkaProducer(bootstrap_servers=[bootstrap_servers],
                             value_serializer=lambda x:
                             json.dumps(x).encode('utf-8'))

    if Properties.Enable == "true" or Properties.Enable == "True":
        url: str = Properties.url
        client = Client(url)
        try:
            client.connect()
            # read 8 registers at address 0, store result in regs list
            for tags in OPCTags.MeasurementTag:
                nameSpace = tags.NameSpace
                identifier = tags.Identifier
                DisplayName = tags.DisplayName
                register = client.get_node("ns={0};i={1}".format(nameSpace, identifier))
                registerValue = register.get_value()
                timeStamp = datetime.now().strftime("%Y-%m-%dT%I:%M:%S_%p")

                data = {
                    "DisplayName": DisplayName,
                    "value": registerValue,
                    "timestamp": timeStamp
                }
                datasList.append(data)

            # if success display registers
            if datasList:
                # producer = KafkaProducer(bootstrap_servers='localhost:9092')
                topicName: str = kafkaJson.topicName
                producer.send(topicName, value=datasList)
                # print("Kafka Producer Status", val)
                #print(str(datasList))

        except Exception as exception:
            success = False
            print("Device is not Connected Error:", exception)
        # Encoding as byte Data for KAFKA
        encoded_data = json.dumps(datasList).encode('utf-8')
        # queue = Queue(topic="test", producer=producer)
        # queue.enqueue(func=callback,
        #               args=(Properties, OPCTags, threadsCount, datasList, success))

        # producer.send('test', value=datasList)
        # print(encoded_data)
        thread = threading.Thread(
            target=callback,
            args=(Properties, OPCTags, threadsCount, datasList, success)
        )
        thread.start()

    return datasList
