# Importing all the necessary Libs
import json
import os
import time
from datetime import datetime
from App.Json_Class.OPCUAParameters import OPCParameters
from App.Json_Class.OPCUAProperties import OPCProperties
from App.Json_Class.index import read_setting
from App.OPCUA.OPCUA_Reader import ReadOPCUA
import threading
import App.globalsettings as appsetting

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

    # Checking the device status for failure
    if not success:
        threadsCount["failed"] = threadsCount["failed"] + 1
        print("Connection Error")
        if threadsCount["failed"] >= int(Properties.RetryCount):
            recoveryTime = float(Properties.RecoveryTime)
            time.sleep(int(recoveryTime))
            threadsCount["failed"] = 0
            print("Thread Closed, Exceeded RecoveryTime")
            # appsetting.startOPCUAService = False

    else:
        threadsCount["failed"] = 0
        threadsCount["count"] = threadsCount["count"] + 1
    timeout = float(Properties.UpdateTime)

    time.sleep(timeout)

    if appsetting.startOPCUAService:
        # Initializing Threading
        thread = threading.Thread(
            target=ReadOPCUA,
            args=(Properties, Parameters, threadsCount, threadCallBack,)
        )
        # Starting the Thread
        thread.start()



