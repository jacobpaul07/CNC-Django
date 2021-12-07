import os
import json
from App.Json_Class.Edge import *


def read_setting():
    filePath = './App/JsonConfiguration/JSONCONFIG.json'
    with open(filePath) as f:
        json_string = json.load(f)
        a = Edgefromdict(json_string)
        f.close()
    return a


def write_setting(jsonFileContent: str):
    filePath = './App/JsonConfiguration/JSONCONFIG.json'
    json_object = json.dumps(jsonFileContent, indent=4)
    with open(filePath, 'w') as f:
        f.write(json_object)
        f.close()




