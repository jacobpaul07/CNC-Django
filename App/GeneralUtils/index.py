import datetime
import json
import os
import sys
import threading
import bson
import App.globalsettings as gs
from App.GeneralUtils.JsonClass import LiveData_fromDict
from MongoDB_Main import Document as Doc

thread_Lock = threading.Lock()
thread_Lock_Avail = threading.Lock()
thread_Lock_Production = threading.Lock()
thread_Lock_DB = threading.Lock()
thread_Lock_ProductionPlan = threading.Lock()
thread_Lock_web_dashboard = threading.Lock()


def get_device_id():
    calculation_json = readCalculation_file()
    machine_id = calculation_json["MachineId"]
    return machine_id


def read_setting():
    file_path = './App/JsonDataBase/package.json'
    with open(file_path) as f:
        json_string = json.load(f)
        a = LiveData_fromDict(json_string)
        f.close()
    return a


def read_json_file(file_path):
    filesize = os.path.getsize(file_path)
    if filesize == 0:
        return None
    else:
        with open(file_path) as f:
            json_string = json.load(f)
        return json_string


def write_json_file(jsonFileContent: str, filePath: str):
    thread_Lock_DB.acquire()
    # json_object = json.dumps(jsonFileContent, indent=4)
    with open(filePath, 'w') as f:
        f.write(jsonFileContent)
        f.close()
    thread_Lock_DB.release()


def writeCalculation_file(jsonFileContent: str):
    thread_Lock.acquire()
    try:
        json_object = json.dumps(jsonFileContent, indent=4)
        with open("./App/LiveJsonDataBase/CalculationData.json", 'w+') as f:
            f.write(json_object)
            f.close()
    except Exception as ex:
        print("writeCalculation_file Error", ex)
    finally:
        thread_Lock.release()


def readCalculation_file():
    try:
        thread_Lock.acquire()
        file_status = os.path.isfile("./App/LiveJsonDataBase/CalculationData.json")
        file_availability_status = os.path.isfile("./App/LiveJsonDataBase/AvailabilityData.json")
        current_time = datetime.datetime.now()
        last_update_time = str(datetime.datetime.strptime(str(current_time), gs.OEE_JsonDateTimeFormat))
        recycle_date_time = last_update_time
        # Availability File Creation
        if file_availability_status is False:
            WriteAvailabilityFile([])
            writeProductionFile([])
        # Calculation File Creation
        if file_status is False:
            print("Recycled - New File Created")
            json_string = readDefaultCalculationJsonFile()
            json_string["RecycledDate"] = recycle_date_time
            json_string["LastUpdatedTime"] = last_update_time
            json_string["ProductionLastUpdateTime"] = last_update_time
            calc_file = json.dumps(json_string, indent=4)
            with open("./App/LiveJsonDataBase/CalculationData.json", 'w+') as af:
                af.write(calc_file)
                af.close()
            productionPlanUpdater(current_time=current_time, machineID="")
            return json_string

        else:
            with open("./App/LiveJsonDataBase/CalculationData.json", 'r') as f:
                json_string = json.load(f)
                RecycleTime = int(json_string["RecycleTime"])

                if current_time.hour == RecycleTime or current_time.hour > RecycleTime:

                    RecycledDate = datetime.datetime.strptime(json_string["RecycledDate"], gs.OEE_JsonDateTimeFormat)
                    machineID = json_string["MachineId"]
                    recycled_date_fmt = datetime.datetime.strftime(RecycledDate, gs.OEE_JsonDateFormat)
                    current_date = str(datetime.datetime.strftime(datetime.datetime.now(), gs.OEE_JsonDateFormat))

                    if str(recycled_date_fmt) != current_date:
                        # Read Production Plan Json File

                        productionPlanUpdater(current_time=current_time, machineID=machineID)

                        print("Recycled the Machine Status")
                        # os.remove("./App/JsonDataBase/CalculationData.json")
                        # Write Calculation Data Json
                        calc_file = json.dumps([], indent=4)
                        with open("./App/LiveJsonDataBase/CalculationData.json", 'w+') as af:
                            af.write(calc_file)
                            af.close()
                        writeProductionFile([])

                        # Read Default Calculation File
                        json_string = readDefaultCalculationJsonFile()
                        json_string["ProductionLastUpdateTime"] = last_update_time
                        json_string["RecycledDate"] = recycle_date_time
                        json_string["LastUpdatedTime"] = last_update_time
                        # Write Calculation Data File
                        calc_file = json.dumps(json_string, indent=4)
                        with open("./App/LiveJsonDataBase/CalculationData.json", 'w+') as af:
                            af.write(calc_file)
                            af.close()
            return json_string

    except Exception as ex:
        print("File read Error is :", ex)

    finally:
        thread_Lock.release()


def productionPlanUpdater(current_time, machineID):
    try:
        production_plan_json_path = "./App/JsonDataBase/ProductionPlan.json"
        col = "ProductionPlan"
        down_time_code_col = "DownTimeCode"
        quality_code_col = "QualityCode"
        read_query = {"machineID": machineID}
        # productionPlanDoc = Doc().Read_Document(col=col)
        productionPlanDoc = Doc().Read_Multiple_Document(col=col, query=read_query)
        down_time_code_doc = Doc().Read_Multiple_Document(col=down_time_code_col, query=read_query)
        quality_code_doc = Doc().Read_Multiple_Document(col=quality_code_col, query=read_query)

        # Close Availability Document
        close_availability_doc(machine_id=machineID)
        if os.path.isfile(production_plan_json_path):
            production_plan = readProductionPlanFile()

            for index, shifts in enumerate(production_plan):

                temp_time = current_time
                shift_start_time_str = shifts["ShiftStartTime"]
                shift_end_time_str = shifts["ShiftEndTime"]

                shift_start_time = datetime.datetime.strptime(shift_start_time_str, gs.OEE_ExcelDateTimeFormat)
                shift_end_time = datetime.datetime.strptime(shift_end_time_str, gs.OEE_ExcelDateTimeFormat)

                beforeRecycle = False
                '''Future Implementation'''
                """Implement recycle Time to check the update before 6 AM"""
                if shift_start_time.time().hour <= current_time.time().hour:
                    beforeRecycle = True

                shift_start_time_difference_delta = temp_time.date() - shift_start_time.date()
                shift_end_time_str_difference_delta = temp_time.date() - shift_end_time.date()
                shift_start_end_difference_delta = shift_end_time.date() - shift_start_time.date()

                shift_start_end_day_int = int(shift_start_end_difference_delta.days)
                shift_start_time_day_int = int(shift_start_time_difference_delta.days)
                shift_end_time_day_int = int(shift_end_time_str_difference_delta.days + shift_start_end_day_int)

                shift_start_time = shift_start_time + datetime.timedelta(days=shift_start_time_day_int)
                shift_end_time = shift_end_time + datetime.timedelta(days=shift_end_time_day_int)

                production_plan[index]["ShiftStartTime"] = str(shift_start_time)
                production_plan[index]["ShiftEndTime"] = str(shift_end_time)
                production_plan[index]["machineID"] = str(machineID)

                # Production Plan Database Update
                production_name = shifts["Name"]
                production_name_obj = list(filter(lambda x: (x["Name"] == production_name), productionPlanDoc))
                if len(production_name_obj) > 0:
                    production_obj = production_name_obj[0]
                    object_id = bson.ObjectId(production_obj["_id"])
                    replacement_data = {
                        "ShiftStartTime": str(shift_start_time),
                        "ShiftEndTime": str(shift_end_time)
                    }
                    query = {"$and": [{"_id": object_id}, {"machineID": machineID}]}
                    data = {"$set": replacement_data}
                    Doc().UpdateDBQuery(col=col, query=query, updateData=data)

            production_plan_dumped = json.dumps(production_plan, indent=4)

            with open(production_plan_json_path, 'w+') as pf:
                pf.write(production_plan_dumped)
                pf.close()

            # Production Plan History Database
            historyUpdateExcel(loadedData=production_plan,
                               historyCollection="ProductionPlanHistory",
                               currentTime=current_time, machineID=machineID)
            print("Production Plan Updated for the Next Date Automatically")

            historyUpdateExcel(loadedData=down_time_code_doc,
                               historyCollection="DownTimeCodeHistory",
                               currentTime=current_time, machineID=machineID)
            print("DownTime Code Updated for the Next Date Automatically")

            historyUpdateExcel(loadedData=quality_code_doc,
                               historyCollection="QualityCodeHistory",
                               currentTime=current_time, machineID=machineID)
            print("Quality Code Updated for the Next Date Automatically")


    except Exception as exception:
        print("App/OPCUA/index.py --> productionPlanUpdater :", exception)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        f_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, f_name, exc_tb.tb_lineno)


def readProductionPlanFile():
    thread_Lock_ProductionPlan.acquire()
    try:
        Path = "./App/JsonDataBase/ProductionPlan.json"
        with open(Path) as f:
            json_string = json.load(f)
        return json_string
    except Exception as ex:
        print("Error", ex)
    finally:
        thread_Lock_ProductionPlan.release()


def readDownReasonCodeFile():
    with open("./App/JsonDataBase/DownReasonCode.json", 'r') as file:
        reason_code_list = json.load(file)
        file.close()
    return reason_code_list


def readDefaultCalculationJsonFile():
    with open("./App/JsonDataBase/DefaultCalculationData.json") as file:
        json_string = json.load(file)
        file.close()
    return json_string


def readDefaultDownCodeJsonFile():
    with open("./App/JsonDataBase/DefaultDownReasonCode.json") as file:
        json_string = json.load(file)
        file.close()
    return json_string


def readAvailabilityFile():
    try:
        thread_Lock_Avail.acquire()
        file_status = os.path.isfile("./App/LiveJsonDataBase/AvailabilityData.json")
        if file_status:
            with open("./App/LiveJsonDataBase/AvailabilityData.json", 'r') as file:
                reason_code_list = json.load(file)
                file.close()
                return reason_code_list
        else:
            reason_code_list = []
            return reason_code_list
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

        with open("./App/LiveJsonDataBase/AvailabilityData.json", "w+") as AvailabilityFiles:
            json.dump(jsonContent, AvailabilityFiles, indent=4)
            AvailabilityFiles.close()
    except Exception as ex:
        print("WriteAvailability File Error: ", ex)

    finally:
        thread_Lock_Avail.release()


def writeProductionFile(jsonContent):
    try:
        thread_Lock_Production.acquire()
        with open("./App/LiveJsonDataBase/currentProduction.json", "w+") as ProductionFiles:
            json.dump(jsonContent, ProductionFiles, indent=4)
            ProductionFiles.close()
    except Exception as ex:
        print("Write Production File Error: ", ex)

    finally:
        thread_Lock_Production.release()


def readProductionFile():
    try:
        thread_Lock_Production.acquire()
        fileStatus = os.path.isfile("./App/LiveJsonDataBase/currentProduction.json")
        if fileStatus:
            with open("./App/LiveJsonDataBase/currentProduction.json", 'r') as file:
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


def readDefaultQualityCategory():
    filePath = './App/JsonDataBase/DefaultQualityCategory.json'
    with open(filePath) as f:
        json_string = json.load(f)
        f.close()
    return json_string


def historyUpdateExcel(loadedData, historyCollection, currentTime, machineID):
    try:
        updated_list = []

        for obj in loadedData:
            obj["timeStamp"] = currentTime
            updated_list.append(obj)

        Doc().historyUpdateExcelDocuments(date=currentTime, historyCollection=historyCollection,
                                          updatedDocument=updated_list, machineID=machineID)
    except Exception as ex:
        print("Error- historyUpdateExcel:", ex)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        f_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, f_name, exc_tb.tb_lineno)


def readWebDashBoard():
    f = open('./Webapp/JsonWeb/webDashBoard.json', "r")
    data = json.loads(f.read())
    # jsonResponse = json.dumps(data, indent=4)
    return data


def write_web_dashboard(web_dashboard_data):
    try:
        thread_Lock_web_dashboard.acquire()
        web_dash_board_path = "./Webapp/JsonWeb/webDashBoard.json"
        with open(web_dash_board_path, "w+") as webDashFile:
            json.dump(web_dashboard_data, webDashFile, indent=4)
            webDashFile.close()

    except Exception as ex:
        print("generate Dashboard Summary Error:", ex)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        f_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, f_name, exc_tb.tb_lineno)

    finally:
        thread_Lock_web_dashboard.release()


def readDeviceList():
    f = open('./Webapp/JsonWeb/devicelist.json', "r")
    data = json.loads(f.read())
    # jsonResponse = json.dumps(data, indent=4)
    return data

def close_availability_doc(machine_id):
    try:
        current_time: datetime = datetime.datetime.now()
        col = "Availability"
        open_data = Doc().ReadDBQuery(col=col, query={"Cycle": "Open", "machineID": machine_id})

        if open_data:
            temp_start_time = open_data['StartTime']
            reference_id = open_data['ReferenceID']
            object_id = open_data['_id']
            temp_duration = str(current_time - temp_start_time)
            update_data = ({"$set": {"StopTime": current_time,
                                     "Duration": temp_duration,
                                     "Cycle": "Closed"}})
            query = {"$and": [{"_id": object_id}, {"machineID": machine_id}]}
            query_cloud = {"$and": [{"_id": reference_id}, {"machineID": machine_id}]}
            Doc().update_query_local_and_cloud(col=col, query=query, update_data=update_data,
                                               query_cloud=query_cloud, machine_id=machine_id)
    except Exception as ex:
        print("Error in App/ResultFormatter.py -> close_availability_doc", ex)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, file_name, exc_tb.tb_lineno)