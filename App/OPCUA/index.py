import json
import os

from App.OPCUA.JsonClass import LiveData_fromDict


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
