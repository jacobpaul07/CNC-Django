import datetime
import sys
import os.path
import pandas as pd
import json

from App.OPCUA.index import readCalculation_file, historyUpdateExcel
from MongoDB_Main import Document as Doc
import os.path
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class OnMyWatch:
    # Set the directory on watch
    watchDirectory = "./App/Excel/"

    def __init__(self):
        self.observer = Observer()
        # self.watchDirectory = watchDirectory

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.watchDirectory, recursive=True)
        self.observer.start()


class Handler(FileSystemEventHandler):

    @staticmethod
    def on_any_event(event):
        fileName = None
        if event.is_directory:
            return None
        elif event.event_type == 'created':
            fileName = os.path.basename(event.src_path)
            # Event is created, you can process it now
            print("Watchdog received created event - % s." % event.src_path)
            startExcelThread(fileName)


def ExceltoMongo(collection, path, filePath, historyCollection):
    try:
        currentTime = datetime.datetime.now()
        if os.path.isfile(path):
            df = pd.read_excel(path, na_filter=False, dtype=str)
            sheetdata = df.to_json(orient="records")
            loadedData = json.loads(sheetdata)
            with open(filePath, "w+") as dbJsonFile:
                json.dump(loadedData, dbJsonFile, indent=4)
                dbJsonFile.close()

            # Including Machine ID
            calculationJson = readCalculation_file()
            machineID = calculationJson["MachineId"]
            loadedList = []
            for obj in loadedData:
                obj["machineID"] = machineID
                loadedList.append(obj)

            # Writing to DataBase
            Doc().DB_Collection_Drop(col=collection)
            Doc().DB_Write_Many(data=loadedList, col=collection)

            # Writing History to DataBase
            historyUpdateExcel(loadedData=loadedList, historyCollection=historyCollection, currentTime=currentTime)

            print("Excel Sheet Uploaded Successfully")
            if os.path.isfile(path):
                os.remove(path)
                print("File Removed Successfully")
            print("File Doesn't Exist Anymore")

        else:
            print("excel not updated")
    except Exception as ex:
        print("Error- ExceltoMongo:", ex)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)


def startExcelThread(fileName):
    try:
        fileNamesList = [
            {
                "jsonPath": "./App/JsonDataBase/QualityCategory.json",
                "excelPath": "./App/Excel/QualityCode/QualityCode.xlsx",
                "fileName": "QualityCode.xlsx",
                "collectionName": "QualityCode",
                "HistoryDocument": "QualityCodeHistory"
            },
            {
                "jsonPath": "./App/JsonDataBase/ProductionPlan.json",
                "excelPath": "./App/Excel/ProductionPlan/ProductionPlan.xlsx",
                "fileName": "ProductionPlan.xlsx",
                "collectionName": "ProductionPlan",
                "HistoryDocument": "ProductionPlanHistory"
            },
            {
                "jsonPath": "./App/JsonDataBase/DownReasonCode.json",
                "excelPath": "./App/Excel/DownCode/DownCode.xlsx",
                "fileName": "DownCode.xlsx",
                "collectionName": "DownTimeCode",
                "HistoryDocument": "DownTimeCodeHistory"
            }
        ]

        print("Excel Update Started")
        files = list(filter(lambda x: (x["fileName"] == str(fileName)), fileNamesList))
        if len(files) > 0:
            time.sleep(3)
            ExceltoMongo(files[0]["collectionName"], files[0]["excelPath"],
                         files[0]["jsonPath"], files[0]["HistoryDocument"])

    except Exception as ex:
        print("Error- ExcelFile:", ex)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)




