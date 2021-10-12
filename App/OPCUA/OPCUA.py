# Importing all the necessary Libs
import json
import os
import time
from datetime import datetime

from pytz import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from App.Json_Class.OPCUAParameters import OPCParameters
from App.Json_Class.OPCUAProperties import OPCProperties
from App.Json_Class.index import read_setting
from App.OPCUA.OPCUA_Reader import ReadOPCUA
import threading
import App.globalsettings as appsetting
from MongoDB_Main import Document as Doc


# Initializing The StopThread as boolean-False
stopThread: bool = False


# Main Modbus TCP Function
def Opc_UA():
    # Read the config file objects
    data = read_setting()
    # Assigning TCP Properties to "tcp_properties" variable
    opc_properties = data.edgedevice.DataService.OPCUA.Properties
    opc_parameters = data.edgedevice.DataService.OPCUA.Parameters

    if opc_properties.Enable == "True" or opc_properties.Enable == "true":
        # Declaring Threading count and failed attempts object
        threadsCount = {
            "count": 0,
            "failed": 0
        }

        # Initializing Threading
        thread = threading.Thread(
            target=ReadOPCUA,
            args=(opc_properties, opc_parameters, threadsCount, threadCallBack))

        # Starting the Thread
        thread.start()

# def sentLiveData(data):
#     text_data = json.dumps(data, indent=4)
#
#     channel_layer = get_channel_layer()
#     async_to_sync(channel_layer.group_send)("notificationGroup", {
#         "type": "chat_message",
#         "message": text_data
#     })


# log definition
def log(result):
    date = datetime.now().strftime("%Y_%m_%d")
    filename = f"log_{date}"
    filepath = './App/log/OPCUA/{}.json'.format(filename)

    a = []
    if not os.path.isfile(filepath):
        a.append(result)
        with open(filepath, mode='w') as f:
            f.write(json.dumps(a, indent=2))
    else:
        with open(filepath) as feedsjson:
            feeds = json.load(feedsjson)
        feeds.append(result)

        with open(filepath, mode='w') as f:
            f.write(json.dumps(feeds, indent=2))


# Callback Function is defined
def threadCallBack(Properties: OPCProperties,
                   Parameters: OPCParameters,
                   threadsCount,
                   result,
                   success):

    # Save the data to log file
    # if appsetting.runWebSocket:
    #     sentLiveData(result)
    # log(result)
    col = "OPCUA"
    now_utc = datetime.now(timezone('UTC'))
    # Convert to Asia/Kolkata time zone
    now_asia = str(now_utc.astimezone(timezone('Asia/Kolkata')))
    mongoData = {
        "timestamp": now_asia,
        "Log Data": result
    }
    # consumer = KafkaConsumer('test')
    # for message in consumer:
    #     print(message)

    Doc().DB_Write(mongoData, col)
    # Printing the thread ID
    # print(threading.get_ident())

    # Checking the device status for failure
    if not success:
        threadsCount["failed"] = threadsCount["failed"] + 1
        if threadsCount["failed"] > int(Properties.RetryCount):
            recoveryTime = float(Properties.RecoveryTime)
            time.sleep(recoveryTime)
            threadsCount["failed"] = 0
            print("wait for recover failed and wait for auto recovery")
    else:
        threadsCount["failed"] = 0
        threadsCount["count"] = threadsCount["count"] + 1

    # print(threadsCount["count"])
    # print("stop thread", stopThread)

    timeout = float(Properties.UpdateTime)
    time.sleep(timeout)
    # print("Test==", appsetting.startTcpService)
    if appsetting.startOPCUAService:
        # print("Restarted")
        # Initializing Threading
        thread = threading.Thread(
            target=ReadOPCUA,
            args=(Properties, Parameters, threadsCount, threadCallBack,)
        )

        # Starting the Thread
        thread.start()

        # print("callback function called")
        # print("{}".format(threadsCount))
        # print(threading.get_ident())
