import ast
import os
import threading
import pandas as pd
import pymongo
import json
from configparser import ConfigParser

client = pymongo.MongoClient("mongodb://localhost:27016")

configration = ConfigParser()
configfilepath = "D:/CNC-OEE/CNC-Django/App/filepath.ini"
configration.read(configfilepath)


quality = 'D:/CNC-OEE/OeeExcellSheets/qualitycode/QualityCode.xlsx'
downcode = 'D:/CNC-OEE/OeeExcellSheets/downcode/DownCode.xlsx'
productionplan = 'D:/CNC-OEE/OeeExcellSheets/productionplan/ProductionPlan.xlsx'

db = client["CNC"]
filecollection = db['Filepath']
qualitycollection = db['Quality']
productionplancollection = db['ProductionPlan']
downcodecollection = db['DownCode']

print(os.path.isfile(quality))

def ExceltoMongo(collection, path):

    if os.path.isfile(path):
        pd.read_excel(open(downcode, 'rb'), sheet_name='Sheet1')
        collection.drop()
        df = pd.read_excel(path)
        sheetdata = df.to_dict(orient="records")
        datastr = str(sheetdata)
        replaced_data = datastr.replace("NaT", "null")
        inptdata = ast.literal_eval(json.dumps(replaced_data))
        data_dict = json.loads(inptdata)
        collection.insert_many(data_dict)
        os.remove(path)
        value = 'data updated'
    else:
        value = 'no updates'
        print(value)

    return value


ExceltoMongo(qualitycollection, quality)
ExceltoMongo(downcodecollection, downcode)
ExceltoMongo(productionplancollection, productionplan)
