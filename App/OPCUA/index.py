import datetime
import json
import os
import sys
import threading
import App.globalsettings as gs
from App.OPCUA.JsonClass import LiveData_fromDict

thread_Lock = threading.Lock()
thread_Lock_Avail = threading.Lock()
thread_Lock_Production = threading.Lock()
thread_Lock_DB = threading.Lock()
thread_Lock_ProductionPlan = threading.Lock()

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
        fileStatus = os.path.isfile("./App/LiveJsonDataBase/CalculationData.json")
        fileAvailabilityStatus = os.path.isfile("./App/LiveJsonDataBase/AvailabilityData.json")
        current_time = datetime.datetime.now()
        LastUpdateTime = str(datetime.datetime.strptime(str(current_time), gs.OEE_JsonDateTimeFormat))
        RecycleDateTime = LastUpdateTime
        # Availability File Creation
        if fileAvailabilityStatus is False:
            WriteAvailabilityFile([])
            writeProductionFile([])
        # Calculation File Creation
        if fileStatus is False:
            print("Recycled - New File Created")
            json_string = readDefaultCalculationJsonFile()
            json_string["RecycledDate"] = RecycleDateTime
            json_string["LastUpdatedTime"] = LastUpdateTime
            json_string["ProductionLastUpdateTime"] = LastUpdateTime
            CalcFile = json.dumps(json_string, indent=4)
            with open("./App/LiveJsonDataBase/CalculationData.json", 'w+') as af:
                af.write(CalcFile)
                af.close()
            productionPlanUpdater(current_time=current_time)
            return json_string

        else:
            with open("./App/LiveJsonDataBase/CalculationData.json", 'r') as f:
                json_string = json.load(f)
                RecycleTime = int(json_string["RecycleTime"])

                if current_time.hour == RecycleTime or current_time.hour > RecycleTime:

                    RecycledDate = datetime.datetime.strptime(json_string["RecycledDate"], gs.OEE_JsonDateTimeFormat)

                    RecycledDate_fmt = datetime.datetime.strftime(RecycledDate, gs.OEE_JsonDateFormat)
                    currentDate = str(datetime.datetime.strftime(datetime.datetime.now(), gs.OEE_JsonDateFormat))

                    if str(RecycledDate_fmt) != currentDate:
                        # Read Production Plan Json File
                        productionPlanUpdater(current_time=current_time)

                        print("Recycled the Machine Status")
                        # os.remove("./App/JsonDataBase/CalculationData.json")
                        # Write Calculation Data Json
                        CalcFile = json.dumps([], indent=4)
                        with open("./App/LiveJsonDataBase/CalculationData.json", 'w+') as af:
                            af.write(CalcFile)
                            af.close()
                        writeProductionFile([])

                        # Read Default Calculation File
                        json_string = readDefaultCalculationJsonFile()
                        json_string["ProductionLastUpdateTime"] = LastUpdateTime
                        json_string["RecycledDate"] = RecycleDateTime
                        json_string["LastUpdatedTime"] = LastUpdateTime
                        # Write Calculation Data File
                        CalcFile = json.dumps(json_string, indent=4)
                        with open("./App/LiveJsonDataBase/CalculationData.json", 'w+') as af:
                            af.write(CalcFile)
                            af.close()
            return json_string

    except Exception as ex:
        print("File read Error is :", ex)

    finally:
        thread_Lock.release()


def productionPlanUpdater(current_time):
    try:
        productionPlanJsonPath = "./App/JsonDataBase/ProductionPlan.json"
        if os.path.isfile(productionPlanJsonPath):
            productionPlan = readProductionPlanFile()

            for index, shifts in enumerate(productionPlan):

                tempTime = current_time
                shiftStartTimeStr = shifts["ShiftStartTime"]
                shiftEndTimeStr = shifts["ShiftEndTime"]

                shiftStartTime = datetime.datetime.strptime(shiftStartTimeStr, gs.OEE_ExcelDateTimeFormat)
                shiftEndTime = datetime.datetime.strptime(shiftEndTimeStr, gs.OEE_ExcelDateTimeFormat)

                beforeRecycle = False

                '''Future Implementation'''
                """Implement recycle Time to check the update before 6 AM"""
                if shiftStartTime.time().hour <= current_time.time().hour:
                    beforeRecycle = True

                shiftStartTimeDifferenceDelta = tempTime.date() - shiftStartTime.date()
                shiftEndTimeStrDifferenceDelta = tempTime.date() - shiftEndTime.date()
                shiftStartEndDifferenceDelta = shiftEndTime.date() - shiftStartTime.date()

                shiftStartEndDayInt = int(shiftStartEndDifferenceDelta.days)
                shiftStartTimeDayInt = int(shiftStartTimeDifferenceDelta.days)
                shiftEndTimeDayInt = int(shiftEndTimeStrDifferenceDelta.days + shiftStartEndDayInt)

                # if beforeRecycle:
                #     shiftStartEndDayInt = shiftStartEndDayInt * (-shiftStartEndDayInt)
                #     shiftStartTimeDayInt = shiftStartTimeDayInt * (-shiftStartTimeDayInt)
                #     shiftEndTimeDayInt = shiftEndTimeDayInt * (-shiftEndTimeDayInt)

                shiftStartTime = shiftStartTime + datetime.timedelta(days=shiftStartTimeDayInt)
                shiftEndTime = shiftEndTime + datetime.timedelta(days=shiftEndTimeDayInt)

                productionPlan[index]["ShiftStartTime"] = str(shiftStartTime)
                productionPlan[index]["ShiftEndTime"] = str(shiftEndTime)

            productionPlanDumped = json.dumps(productionPlan, indent=4)
            with open(productionPlanJsonPath, 'w+') as pf:
                pf.write(productionPlanDumped)
                pf.close()
            print("Production Plan Updated for the Next Date Automatically")
    except Exception as exception:
        print("App/OPCUA/index.py --> productionPlanUpdater :", exception)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fName = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fName, exc_tb.tb_lineno)


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
        fileStatus = os.path.isfile("./App/LiveJsonDataBase/AvailabilityData.json")
        if fileStatus:
            with open("./App/LiveJsonDataBase/AvailabilityData.json", 'r') as file:
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
