import datetime
import json
import os
import threading

from App.OPCUA.JsonClass import LiveData_fromDict

thread_Lock = threading.Lock()

def read_setting():
    filePath = './App/OPCUA/package.json'
    with open(filePath) as f:
        json_string = json.load(f)
        a = LiveData_fromDict(json_string)
        f.close()
    return a


def write_setting(jsonFileContent: str):
    filePath = './App/OPCUA/package.json'
    json_object = json.dumps(jsonFileContent, indent=4)
    with open(filePath, 'w') as f:
        f.write(json_object)
        f.close()


def read_temp_file():
    filePath = './App/OPCUA/tempCalculation.json'
    with open(filePath) as f:
        json_string = json.load(f)
        f.close()
    return json_string


def write_temp_file(jsonFileContent: str):
    filePath = './App/OPCUA/tempCalculation.json'
    json_object = json.dumps(jsonFileContent, indent=4)
    with open(filePath, 'w') as f:
        f.write(json_object)
        f.close()


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

    thread_Lock.acquire()
    try:
        fileStatus = os.path.isfile("./App/JsonDataBase/CalculationData.json")
        current_time = datetime.datetime.now()
        if fileStatus is False:
            print("Recycled Main Condition")
            with open("./App/JsonDataBase/DefaultCalculationData.json", 'r') as file:
                json_string = json.load(file)
                file.close()

            with open("./App/JsonDataBase/CalculationData.json", "w+") as files:
                json_string["RecycledDate"] = str(datetime.datetime.today().date())
                json_string["LastUpdatedTime"] = str(datetime.datetime.strptime(str(current_time), '%Y-%m-%d %H:%M:%S.%f'))
                json.dump(json_string, files, indent=4)
                files.close()
                # create.write(json_string)

            return json_string

        else:
            with open("./App/JsonDataBase/CalculationData.json", 'r') as f:
                json_string = json.load(f)

                if current_time.hour == int(json_string["RecycleTime"]):
                    RecycledDate = json_string["RecycledDate"]
                    if str(RecycledDate) != str(datetime.datetime.today().date()):
                        print("Recycled Else Condition")
                        # os.remove("./App/JsonDataBase/CalculationData.json")
                        with open("./App/JsonDataBase/DefaultCalculationData.json") as file:
                            json_string = json.load(file)
                            file.close()

                        with open("./App/JsonDataBase/CalculationData.json", "w+") as create:
                            json_string["RecycledDate"] = str(datetime.datetime.today().date())
                            json_string["LastUpdatedTime"] = str(datetime.datetime.strptime(str(current_time),'%Y-%m-%d %H:%M:%S.%f'))
                            json.dump(json_string, create, indent=4)
                            create.close()
                            # create.write(json_string)
    except Exception as ex:
        print("File read Error is :", ex)
    finally:
        thread_Lock.release()
    return json_string



