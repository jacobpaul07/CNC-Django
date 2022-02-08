# Importing all the necessary Libs
import os
import json
import time
import threading
from datetime import datetime
from App.globalsettings import GlobalFormats
from App.OPCUA.OPCUA_Reader import ReadOPCUA
from App.Json_Class.index import read_setting
from App.Json_Class.OPCUAParameters import OPCParameters
from App.Json_Class.OPCUAProperties import OPCProperties


# Initializing The StopThread as boolean-False
stopThread: bool = False


# Main Modbus TCP Function
def initialize_opcua():
    # Read the config file objects
    data = read_setting()
    # Assigning TCP Properties to "tcp_properties" variable
    opc_properties = data.edgedevice.DataService.OPCUA.Properties
    opc_parameters = data.edgedevice.DataService.OPCUA.Parameters

    if opc_properties.Enable == "True" or opc_properties.Enable == "true":
        # Declaring Threading count and failed attempts object
        threads_count = {
            "count": 0,
            "failed": 0
        }

        # Initializing Threading
        thread = threading.Thread(
            target=ReadOPCUA,
            args=(opc_properties, opc_parameters, threads_count, thread_call_back))

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
        with open(filepath) as feeds_json:
            feeds = json.load(feeds_json)
        feeds.append(result)

        with open(filepath, mode='w') as f:
            f.write(json.dumps(feeds, indent=2))


# Callback Function is defined
def thread_call_back(properties: OPCProperties,
                     parameters: OPCParameters,
                     threads_count,
                     result,
                     success):

    # Checking the device status for failure
    if not success:
        threads_count["failed"] = threads_count["failed"] + 1
        print("Connection Error")
        if threads_count["failed"] >= int(properties.RetryCount):
            recovery_time = float(properties.RecoveryTime)
            time.sleep(int(recovery_time))
            threads_count["failed"] = 0
            print("Thread Closed, Exceeded RecoveryTime")

    else:
        threads_count["failed"] = 0
        threads_count["count"] = threads_count["count"] + 1
    time.sleep(2)

    if GlobalFormats.startOPCUAService:
        # Initializing Threading
        thread = threading.Thread(
            target=ReadOPCUA,
            args=(properties, parameters, threads_count, thread_call_back,)
        )
        # Starting the Thread
        thread.start()
