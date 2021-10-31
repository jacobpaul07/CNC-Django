import json


def read_setting():
    filePath = './App/JsonDataBase/readWrite.json'
    with open(filePath) as f:
        json_string = json.load(f)
        # dumpedValue = json.dumps(json_string)
        f.close()
    return json_string


def write_setting(jsonFileContent: str):
    filePath = './App/JsonDataBase/readWrite.json'
    json_object = json.dumps(jsonFileContent, indent=4)
    with open(filePath, 'w') as f:
        f.write(json_object)
        f.close()




