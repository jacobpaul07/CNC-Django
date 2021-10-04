# Importing all the necessary Libs
import json
import os
import time
from datetime import datetime
from pytz import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from App.Json_Class.TCPProperties_dto import TCPProperties
from App.Json_Class.TCPdevice_dto import TCPdevice
from App.Json_Class.index import read_setting
from App.TCPReaders.modbusTcpReader import ReadTCP
import threading
import App.globalsettings as appsetting
from MongoDB_Main import Document as Doc

# Initializing The StopThread as boolean-False
stopThread: bool = False


# Main Modbus TCP Function
def modbus_tcp():
    # Read the config file objects
    data = read_setting()

    # Assigning TCP Properties to "tcp_properties" variable
    tcp_properties = data.edgedevice.DataCenter.TCP.properties

    if tcp_properties.Enable == "True" or tcp_properties.Enable == "true":

        # Initializing the loop total number of devices in the Config-file
        for dev in data.edgedevice.DataCenter.TCP.devices:

            # Checking if the device property is Enabled
            if dev.properties.Enable == "true" or dev.properties.Enable == "True":
                # Assigning the IP and Port
                SERVER_HOST = dev.properties.TCPIP.IPAdress
                SERVER_PORT = dev.properties.TCPIP.PortNumber

                # Declaring Threading count and failed attempts object
                threadsCount = {
                    "count": 0,
                    "failed": 0
                }

                # Initializing Threading
                thread = threading.Thread(
                    target=ReadTCP,
                    args=(SERVER_HOST, SERVER_PORT, dev, tcp_properties, threadsCount, threadCallBack))

                # Starting the Thread
                thread.start()


def sentLiveData(data):
    text_data = json.dumps(data, indent=4)

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)("notificationGroup", {
        "type": "chat_message",
        "message": text_data
    })


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
def threadCallBack(SERVER_HOST,
                   SERVER_PORT,
                   tcpDevices: TCPdevice,
                   tcpProperties: TCPProperties,
                   threadsCount,
                   result,
                   success):
    # Save the data to log file

    if appsetting.runWebSocket:
        sentLiveData(result)
    log(result)
    print(result)
    col = "ModbusTCP"
    now_utc = datetime.now(timezone('UTC'))
    # Convert to Asia/Kolkata time zone
    now_asia = str(now_utc.astimezone(timezone('Asia/Kolkata')))
    mongoData = {
        "timestamp": now_asia,
        "Log Data": result
    }
    Doc().DB_Write(mongoData, col)
    # Printing the thread ID
    # print(threading.get_ident())

    # Checking the device status for failure
    if not success:
        threadsCount["failed"] = threadsCount["failed"] + 1
        if threadsCount["failed"] > int(tcpProperties.RetryCount):
            recoveryTime = int(tcpProperties.AutoRecoverTimes)
            time.sleep(recoveryTime)
            threadsCount["failed"] = 0
            print("wait for recover failed and wait for auto recovery")
    else:
        threadsCount["failed"] = 0
        threadsCount["count"] = threadsCount["count"] + 1

    # print(threadsCount["count"])
    # print("stop thread", stopThread)

    timeout = int(tcpProperties.ScanTimems) / 1000
    time.sleep(timeout)
    # print("Test==", appsetting.startTcpService)
    if appsetting.startTcpService:
        # print("Restarted")
        # Initializing Threading
        thread = threading.Thread(
            target=ReadTCP,
            args=(SERVER_HOST, SERVER_PORT, tcpDevices, tcpProperties, threadsCount, threadCallBack,)
        )

        # Starting the Thread
        thread.start()

        # print("callback function called")
        # print("{}".format(threadsCount))
        # print(threading.get_ident())
