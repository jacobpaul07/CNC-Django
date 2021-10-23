import json
from kafka import KafkaConsumer
from pytz import timezone
from datetime import datetime
from App.GeneralUtilities import timestamp
from App.OPCUA.SampleOutput import SampleOutput
from MongoDB_Main import Document as Doc
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
            # print("Topic Name=%s,Message=%s" % (msg.topic, msg.value))
            # print('consumer data received')

            receivedValue = msg.value.decode('utf8')
            loadValue: list = json.loads(receivedValue)
            sentLiveData(loadValue)

            # col = "AbsoluteData"
            # now_utc: str = datetime.now(timezone('UTC')).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
            # Append Timestamp to the Output
            # Output["timestamp"] = now_utc
            # Doc().DB_Write(Output, col)

            # HEADERS = ["CycleStart_Status", "DownTime_ReasonCode", "DownTime_Status", "EmgStop_Status",
            #            "IdealCycleTime",
            #            "JobID", "MachineID", "OperatorID", "PowerOn_Status", "ProductionStart", "QualityCode",
            #            "ShiftID"]
            # # Result dictionary
            # formattedResult = {}
            # for index, header in enumerate(HEADERS):
            #     formattedResult[header] = loadValue[index]["value"]
            #
            # now_utc = datetime.now(timezone('UTC')).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
            #
            # MachineID = formattedResult["MachineID"]
            # OperatorID = formattedResult["OperatorID"]
            # JobID = formattedResult["JobID"]
            # ShiftID = formattedResult["ShiftID"]
            #
            # availability = "58 %"
            # performance = "68 %"
            # quality = "78 %"
            # targetOee = "88 %"
            # oee = "65 %"
            #
            # # Output = SampleOutput(formattedResult, availability, performance, quality, targetOee, oee)

            print("Kafka Consumed Successfully")

    except Exception as ex:
        print("Error Occurred", ex)
