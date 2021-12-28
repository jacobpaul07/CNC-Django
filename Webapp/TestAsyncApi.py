import asyncio
import copy
import json
import os
import sys


from django.http.response import HttpResponseNotAllowed
from django.http import JsonResponse
import uuid
from confluent_kafka import Consumer, KafkaError
from App.OPCUA.OPCUA_Reader import publishToKafka
from App.Json_Class.index import read_setting

listOfQueue = []
listOfQueueEvent = []


def getEventData(guid):
    data = list(filter(lambda x: (x['guid'] == guid), listOfQueue))
    event = list(filter(lambda x: (x['guid'] == guid), listOfQueueEvent))
    row = {
        'data': data[0],
        'event': event[0]
    }
    return row


async def kafkaPublisher(guid):
    print("kafka Web API Publisher Started")
    rowData = getEventData(guid)['data']
    kafkaMessage = json.dumps(rowData)

    jsonObject = read_setting()
    kafkaJson = jsonObject.edgedevice.Service.Kafka
    cloudServers: str = kafkaJson.cloudServers
    topicName = 'request_' + rowData['deviceID']
    print("Kafka Web Pub Topic", topicName)
    publishToKafka(kafkaServer=cloudServers, kafkaTopic=topicName, message=kafkaMessage)
    eventData = getEventData(guid)['event']
    await eventData['event'].wait()


async def kafkaConsumer(guid):
    rowData = getEventData(guid)['data']
    print("rowData", rowData)
    data = read_setting()
    kafkaSetting = data.edgedevice.Service.Kafka
    topicName = 'response_' + rowData['deviceID']
    cloudServers: str = kafkaSetting.cloudServers

    kafkaConsumerConfig = {
        "bootstrap.servers": cloudServers,
        "group.id": "python_example_group_3",
        'enable.auto.commit': False,
        'session.timeout.ms': 6000,
        "auto.offset.reset": "latest",
        "allow.auto.create.topics": True
    }

    # Create Consumer instance
    apiConsumer = Consumer(kafkaConsumerConfig)
    apiConsumer.subscribe([topicName])
    consumed = False

    try:
        while not consumed:
            msg = apiConsumer.poll(0.1)
            if msg is None:
                # print('no response from web api producer from iot')
                pass
            elif not msg.error():
                receivedValue = msg.value().decode('utf-8')
                print("kafka 'Api Web' --> Consumed")
                loadValue = json.loads(receivedValue)
                apiConsumer.commit()
                responseGuid = loadValue['guid']
                consumed = True

                if responseGuid == rowData['guid']:
                    rowData["result"] = loadValue["result"]

            elif msg.error().code() == KafkaError._PARTITION_EOF:
                print('End of partition reached {0}/{1}'
                      .format(msg.topic(), msg.partition()))
            else:
                print('Error occured: {0}'.format(msg.error().str()))

    except KeyboardInterrupt and Exception as ex:
        apiConsumer.close()
        print("Kafka api Web Consumer Error:", ex)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fName = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fName, exc_tb.tb_lineno)

    finally:
        eventData = getEventData(guid)['event']
        eventData['event'].set()


class TestClass:
    @staticmethod
    async def getData(request):
        params = {k: v[0] for k, v in dict(request.GET).items()}
        body = request.body.decode('utf-8')
        guid = str(uuid.uuid4())
        event = asyncio.Event()

        if request.method == "GET":
            deviceID = params["deviceID"] if "deviceID" in params else ""
        else:
            reqData = json.loads(body)
            deviceID = reqData[0]["machineID"]

        if deviceID == "" or deviceID == "default":
            return []

        else:
            params["mode"] = "mobile"
            queueData = {
                'url': request.path,
                'deviceID': deviceID,
                'params': params,
                'body': body,
                'method': request.method,
                'guid': guid,
                'result': []
            }
            queueEventData = {
                'guid': guid,
                'event': event,
            }
            listOfQueue.append(queueData)
            listOfQueueEvent.append(queueEventData)

            waiter_task = asyncio.create_task(kafkaPublisher(guid))
            asyncio.create_task(kafkaConsumer(guid))
            await waiter_task

            # data = getEventData(guid)['result']
            data = getEventData(guid)['data']
            # json_payload = {
            #     "machineID": "CNC-001"
            # }
            return data['result']

