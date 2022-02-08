# Importing all the necessary Libs
import time
import threading

from App.Json_Class.OPCUAParameters import OPCParameters
from App.Json_Class.OPCUAProperties import OPCProperties
from App.MTConnect.MT_Connect_Listner import read_mtconnect
from App.globalsettings import GlobalFormats
from App.Json_Class.index import read_setting

# Initializing The StopThread as boolean-False
stopThread: bool = False


# Main Modbus TCP Function
def initialize_mtconnect():
    # Read the config file objects
    data = read_setting()
    # Assigning TCP Properties to "tcp_properties" variable
    mtconnect_properties = data.edgedevice.DataService.MTConnect.Properties
    mtconnect_parameters = data.edgedevice.DataService.MTConnect.Parameters

    if mtconnect_properties.Enable == "True" or mtconnect_properties.Enable == "true":
        # Declaring Threading count and failed attempts object
        threads_count = {
            "count": 0,
            "failed": 0
        }

        # Initializing Threading
        thread = threading.Thread(
            target=read_mtconnect,
            args=(mtconnect_properties, mtconnect_parameters, threads_count, thread_call_back))

        # Starting the Thread
        thread.start()


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
            target=read_mtconnect,
            args=(properties, parameters, threads_count, thread_call_back,)
        )
        # Starting the Thread
        thread.start()
