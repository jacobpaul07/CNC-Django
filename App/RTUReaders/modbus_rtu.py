# Importing all the necessary Libs
import json
import os
import time
from datetime import datetime
from pytz import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from App.Json_Class.COMDevices_dto import COMdevice
from App.Json_Class.COMProperties_dto import COMPORTProperties
from App.Json_Class.SerialPortSetting_dto import SerialPortSettings
import threading
import App.globalsettings as appsetting
from App.Json_Class.COMPort_dto import Comport
from App.Json_Class.index import read_setting
from App.RTUReaders.modbusRtuReader import ReadRTU
from MongoDB_Main import Document as Doc
# Initializing The StopThread as boolean-False
stopThread: bool = False


def modbus_rtu():
    data = read_setting()
    ports = ["COM1", "COM2"]

    for com in ports:

        comport: Comport = getattr(data.edgedevice.DataCenter, com)
        serial_port_setting1 = comport.properties.SerialPortSetting
        comProperties: COMPORTProperties = comport.properties
        if comport.properties.Enable == "True" or comport.properties.Enable == "true":
            for dev in comport.devices:
                if dev.properties.Enable == "True" or dev.properties.Enable == "true":
                    # Declaring Threading count and failed attempts object
                    threadsCount = {
                        "count": 0,
                        "failed": 0
                    }

                    # Initializing Threading
                    thread = threading.Thread(
                        target=ReadRTU,
                        args=(serial_port_setting1, dev, comProperties, threadsCount, threadCallBack, com))

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
    filepath = './App/log/RTU/{}.json'.format(filename)

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
def threadCallBack(settings: SerialPortSettings,
                   ComDevices: COMdevice,
                   comProperties: COMPORTProperties,
                   threadsCount,
                   result,
                   success,
                   com):
    # Save the data to log file
    if appsetting.runWebSocket:
        sentLiveData(result)

    log(result)
    print(result)
    col = "ModbusRTU"
    now_utc = datetime.now(timezone('UTC'))
    # Convert to Asia/Kolkata time zone
    now_asia = str(now_utc.astimezone(timezone('Asia/Kolkata')))
    mongoData = {
        "timestamp": now_asia,
        "Log Data": result
    }
    Doc().DB_Write(mongoData, col)
    # print("COM Data", result)
    # Printing the thread ID
    # print(threading.get_ident())

    # Checking the device status for failure
    if not success:
        threadsCount["failed"] = threadsCount["failed"] + 1
        if threadsCount["failed"] > int(comProperties.RetryCount):
            recoveryTime = int(comProperties.AutoRecoverTimes)
            time.sleep(recoveryTime)
            threadsCount["failed"] = 0
            print("wait for recover failed and wait for auto recovery")
    else:
        threadsCount["failed"] = 0
        threadsCount["count"] = threadsCount["count"] + 1

    # print(threadsCount["count"])
    # print("stop thread", stopThread)

    timeout = int(comProperties.ScanTimems) / 1000
    time.sleep(timeout)
    # print("Test==", appsetting.startRtuService)
    if appsetting.startRtuService:
        # print("Restarted")
        # Initializing Threading
        thread = threading.Thread(
            target=ReadRTU,
            args=(settings, ComDevices, comProperties, threadsCount, threadCallBack, com)
        )

        # Starting the Thread
        thread.start()

        # print("callback function called")
        # print("{}".format(threadsCount))
        # print(threading.get_ident())
