import threading
import os.path
import pandas as pd
import pymongo
import json
from configparser import ConfigParser
from App.OPCUA.index import write_json_file

client = pymongo.MongoClient("mongodb://localhost:27016")

configration = ConfigParser()
configfilepath = "filepath.ini"
configration.read(configfilepath)

qualitypath = "./App/Excel/QualityCode/QualityCode.xlsx"
productionpath = "./App/Excel/DownCode/DownCode.xlsx"
downcodepath = "./App/Excel/ProductionPlan/ProductionPlan.xlsx"

qualityJsonPath = "./App/JsonDataBase/QualityCategory.json"
productionJsonPath = "./App/JsonDataBase/ProductionPlan.json"
downCodeJsonPath = "./App/JsonDataBase/DownReasonCode.json"

db = client["CNC"]
qualitycollection = db['Quality']
productionplancollection = db['ProductionPlan']
downcodecollection = db['DownCode']


def ExceltoMongo(collection, path, filePath):
    threading.Timer(5, function=ExceltoMongo, args=collection)

    if os.path.isfile(path):
        collection.drop()
        df = pd.read_excel(path, na_filter=False, dtype=str)
        sheetdata = df.to_json(orient="records")
        loadedData = json.loads(sheetdata)
        collection.insert_many(loadedData)
        os.remove(path)
        write_json_file(jsonFileContent=loadedData, filePath=filePath)
        value = 'data updated'
    else:
        value = 'no updates'
    print(value)


# thread to start the process
threading.Timer(5.0, ExceltoMongo, args=(downcodecollection, downcodepath, downCodeJsonPath)).start()
threading.Timer(5.0, ExceltoMongo, args=(qualitycollection, qualitypath, qualityJsonPath)).start()
threading.Timer(5.0, ExceltoMongo, args=(productionplancollection, productionpath, productionJsonPath)).start()
