import sys
import time
import json
import os.path
import datetime
import pandas as pd

from watchdog.observers import Observer
from MongoDB_Main import Document as Doc
from watchdog.events import FileSystemEventHandler
from App.GeneralUtils.index import readCalculation_file, historyUpdateExcel
from App.GenericKafkaConsumer.GenericKafkaConsume import publish_to_replication_server


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

    def on_any_event(self, event):
        if event.is_directory:
            return None
        elif event.event_type == 'created':
            file_name = os.path.basename(event.src_path)
            # Event is created, you can process it now
            print("Watchdog received created event - % s." % event.src_path)
            start_excel_thread(file_name)


def excel_to_mongo(collection, path, file_path, history_collection):
    try:
        current_time = datetime.datetime.now()
        if os.path.isfile(path):
            df = pd.read_excel(path, na_filter=False, dtype=str)
            sheet_data = df.to_json(orient="records")
            loaded_data = json.loads(sheet_data)
            with open(file_path, "w+") as dbJsonFile:
                json.dump(loaded_data, dbJsonFile, indent=4)
                dbJsonFile.close()

            # Including Machine ID
            calculation_json = readCalculation_file()
            machine_id = calculation_json["MachineId"]
            loaded_list = []
            for obj in loaded_data:
                obj["machineID"] = machine_id
                loaded_list.append(obj)

            # Writing to DataBase
            Doc().DB_Collection_Drop(col=collection)
            # drop collection for replica
            replica_server_drop_collection(collection_name=collection, machine_id=machine_id)

            for write_obj in loaded_list:
                print(write_obj)
                Doc().DB_Write(data=write_obj, col=collection)
                # add new record in replica
                publish_to_replication_server(collection_name=collection, entry_mode="C", loaded_data=write_obj,
                                              device_id=machine_id, query={}, return_response=False)

            # Writing History to DataBase
            historyUpdateExcel(loadedData=loaded_list, historyCollection=history_collection,
                               currentTime=current_time, machineID=machine_id)

            print("Excel Sheet Uploaded Successfully")
            if os.path.isfile(path):
                os.remove(path)
                print("File Removed Successfully")
            print("File Doesn't Exist Anymore")

        else:
            print("excel not updated")
    except Exception as ex:
        print("Error- excel_to_mongo:", ex)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        f_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, f_name, exc_tb.tb_lineno)


def start_excel_thread(file_name):
    try:
        file_names_list = [
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
        files = list(filter(lambda x: (x["fileName"] == str(file_name)), file_names_list))
        if len(files) > 0:
            time.sleep(3)
            excel_to_mongo(collection=files[0]["collectionName"], path=files[0]["excelPath"],
                           file_path=files[0]["jsonPath"], history_collection=files[0]["HistoryDocument"])

    except Exception as ex:
        print("Error- ExcelFile:", ex)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        f_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, f_name, exc_tb.tb_lineno)


def replica_server_drop_collection(collection_name, machine_id):
    publish_to_replication_server(collection_name=collection_name, entry_mode="DC", loaded_data={},
                                  device_id=machine_id, query={}, return_response=False)
