import datetime
import json
import os
import sys
import threading

from App.OPCUA.JsonClass import LiveData_fromDict

thread_Lock = threading.Lock()
thread_Lock_Avail = threading.Lock()
thread_Lock_Production = threading.Lock()


def read_setting():
    filePath = './App/JsonDataBase/package.json'
    with open(filePath) as f:
        json_string = json.load(f)
        a = LiveData_fromDict(json_string)
        f.close()
    return a


def read_json_file(filePath):
    filesize = os.path.getsize(filePath)
    if filesize == 0:
        return None
    else:
        with open(filePath) as f:
            json_string = json.load(f)
        return json_string


def write_json_file(jsonFileContent: str, filePath: str):
    json_object = json.dumps(jsonFileContent, indent=4)
    with open(filePath, 'w') as f:
        f.write(json_object)
        f.close()


def writeCalculation_file(jsonFileContent: str):
    thread_Lock.acquire()
    try:
        json_object = json.dumps(jsonFileContent, indent=4)
        with open("./App/JsonDataBase/CalculationData.json", 'w+') as f:
            f.write(json_object)
            f.close()
    except Exception as ex:
        print("writeCalculation_file Error", ex)
    finally:
        thread_Lock.release()


def readCalculation_file():
    try:
        fileStatus = os.path.isfile("./App/JsonDataBase/CalculationData.json")
        fileAvailabilityStatus = os.path.isfile("./App/JsonDataBase/AvailabilityData.json")
        current_time = datetime.datetime.now()
        LastUpdateTime = str(datetime.datetime.strptime(str(current_time), '%Y-%m-%d %H:%M:%S.%f'))
        # Availability File Creation
        if fileAvailabilityStatus is False:
            WriteAvailabilityFile([])
            writeProductionFile([])
        # Calculation File Creation
        if fileStatus is False:
            print("Recycled - New File Created")
            json_string = readDefaultCalculationJsonFile()
            json_string["RecycledDate"] = str(datetime.datetime.today().date())
            json_string["LastUpdatedTime"] = LastUpdateTime
            json_string["ProductionLastUpdateTime"] = LastUpdateTime
            writeCalculation_file(json_string)
            return json_string

        else:
            with open("./App/JsonDataBase/CalculationData.json", 'r') as f:
                json_string = json.load(f)
                RecycleTime = int(json_string["RecycleTime"])
                if current_time.hour == RecycleTime or current_time.hour > RecycleTime:
                    RecycledDate = json_string["RecycledDate"]
                    if str(RecycledDate) != str(datetime.datetime.today().date()):
                        print("Recycled the Machine Status")
                        # os.remove("./App/JsonDataBase/CalculationData.json")
                        WriteAvailabilityFile([])
                        writeProductionFile([])
                        # Read Default Calculation File
                        json_string = readDefaultCalculationJsonFile()
                        json_string["ProductionLastUpdateTime"] = LastUpdateTime
                        json_string["RecycledDate"] = str(datetime.datetime.today().date())
                        json_string["LastUpdatedTime"] = LastUpdateTime
                        writeCalculation_file(json_string)
            return json_string
    except Exception as ex:
        print("File read Error is :", ex)


def readProductionPlanFile():
    Path = "./App/JsonDataBase/ProductionPlan.json"
    with open(Path) as f:
        json_string = json.load(f)
    return json_string


def readDownReasonCodeFile():
    with open("./App/JsonDataBase/DownReasonCode.json", 'r') as file:
        reasonCodeList = json.load(file)
        file.close()
    return reasonCodeList


def readDefaultCalculationJsonFile():
    with open("./App/JsonDataBase/DefaultCalculationData.json") as file:
        json_string = json.load(file)
        file.close()
    return json_string


def readAvailabilityFile():
    try:
        thread_Lock_Avail.acquire()
        fileStatus = os.path.isfile("./App/JsonDataBase/AvailabilityData.json")
        if fileStatus:
            with open("./App/JsonDataBase/AvailabilityData.json", 'r') as file:
                reasonCodeList = json.load(file)
                file.close()
                return reasonCodeList
        else:
            reasonCodeList = []
            return reasonCodeList
    except Exception as ex:
        print(ex)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
    finally:
        thread_Lock_Avail.release()


def WriteAvailabilityFile(jsonContent):
    try:
        thread_Lock_Avail.acquire()

        with open("./App/JsonDataBase/AvailabilityData.json", "w+") as AvailabilityFiles:
            json.dump(jsonContent, AvailabilityFiles, indent=4)
            AvailabilityFiles.close()
    except Exception as ex:
        print("WriteAvailability File Error: ", ex)

    finally:
        thread_Lock_Avail.release()


def writeProductionFile(jsonContent):
    try:
        thread_Lock_Production.acquire()
        with open("./App/JsonDataBase/currentProduction.json", "w+") as ProductionFiles:
            json.dump(jsonContent, ProductionFiles, indent=4)
            ProductionFiles.close()
    except Exception as ex:
        print("Write Production File Error: ", ex)

    finally:
        thread_Lock_Production.release()


def readProductionFile():
    try:
        thread_Lock_Production.acquire()
        fileStatus = os.path.isfile("./App/JsonDataBase/currentProduction.json")
        if fileStatus:
            with open("./App/JsonDataBase/currentProduction.json", 'r') as file:
                reasonCodeList = json.load(file)

                file.close()
                return reasonCodeList
        else:
            reasonCodeList = []
            return reasonCodeList

    except Exception as ex:
        print(ex)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
    finally:
        thread_Lock_Production.release()


def readQualityCategory():
    filePath = './App/JsonDataBase/QualityCategory.json'
    with open(filePath) as f:
        json_string = json.load(f)
        f.close()
    return json_string
