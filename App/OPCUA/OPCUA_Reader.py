import json
import os
import sys
import threading
import datetime
from copy import copy
# from App.Excel import ReadFromExcel
from App.CNC_Calculation.MachineStatus import machineRunningStatus_Updater, getSeconds_fromTimeDifference
from App.OPCUA.index import readCalculation_file, readProductionPlanFile, readAvailabilityFile, readDownReasonCodeFile, \
    readProductionFile, readQualityCategory, readDefaultQualityCategory
from App.CNC_Calculation.APQ import Availability, Productivity, Quality, OeeCalculator
from App.Json_Class.index import read_setting
from kafka import KafkaProducer
from opcua import Client
from App.Json_Class.OPCUAParameters import OPCParameters
from App.Json_Class.OPCUAProperties import OPCProperties
from App.OPCUA.Output import StandardOutput
from App.OPCUA.ResultFormatter import dataValidation
from MongoDB_Main import Document as Doc
import App.globalsettings as gs



def ReadOPCUA(Properties: OPCProperties, OPCTags: OPCParameters, threadsCount, callback):
    currentTime: datetime = datetime.datetime.now()
    success = True
    datasList: list = []
    jsonObject = read_setting()
    kafkaJson = jsonObject.edgedevice.Service.Kafka
    bootstrap_servers: str = kafkaJson.bootstrap_servers

    if Properties.Enable == "true" or Properties.Enable == "True":
        url: str = Properties.url
        client = Client(url)
        try:
            client.connect()
            # read 8 registers at address 0, store result in regs list
            for tags in OPCTags.MeasurementTag:
                nameSpace = tags.NameSpace
                identifier = tags.Identifier
                DisplayName = tags.DisplayName
                register = client.get_node("ns={0};i={1}".format(nameSpace, identifier))
                registerValue = register.get_value()

                data = {
                    "DisplayName": DisplayName,
                    "value": registerValue
                }
                datasList.append(data)

            # if success display registers
            if datasList:
                HEADERS = ["CycleStart_Status", "DownTime_ReasonCode", "DownTime_Status", "EmgStop_Status",
                           "IdealCycleTime",
                           "JobID", "MachineID", "OperatorID", "PowerOn_Status", "ProductionStart", "QualityCode",
                           "ShiftID"]

                # Result dictionary
                result = {}
                for index, header in enumerate(HEADERS):
                    result[header] = str(datasList[index]["value"])
                print("Result", result)

                Calculation_Data = readCalculation_file()
                ProductionPlan_Data = readProductionPlanFile()

                thread = threading.Thread(
                    target=dataValidation,
                    args=(result, currentTime)
                )
                thread.start()

                machineRunningStatus_Updater_thread = threading.Thread(
                    target=machineRunningStatus_Updater,
                    args=(result, ProductionPlan_Data, currentTime)
                )
                machineRunningStatus_Updater_thread.start()

                Total_time = getSeconds_fromTimeDifference(Calculation_Data["TotalDuration"])
                Planned_Down_time = getSeconds_fromTimeDifference(
                    Calculation_Data["Down"]["category"]["Planned"]["ActiveHours"])
                UnPlanned_Down_time = getSeconds_fromTimeDifference(
                    Calculation_Data["Down"]["category"]["Unplanned"]["ActiveHours"])
                Total_Unplanned_Downtime = getSeconds_fromTimeDifference(Calculation_Data["Down"]["ActiveHours"])
                goodCount = int(Calculation_Data["goodCount"])
                badCount = int(Calculation_Data["badCount"])
                RunningDuration = getSeconds_fromTimeDifference(Calculation_Data["Running"]["ActiveHours"])
                DownDuration = getSeconds_fromTimeDifference(Calculation_Data["Down"]["ActiveHours"])

                Standard_Cycle_Time = float(result["IdealCycleTime"])
                Total_Produced_Components = goodCount + badCount

                '''AVAILABILITY CALCULATOR'''
                AvailPercent, Machine_Utilized_Time = Availability(UnPlanned_Down_time)
                Availability_Formatted = AvailPercent if AvailPercent <= 100.00 else 100.00
                '''PERFORMANCE CALCULATOR'''
                PerformPercent = Productivity(Standard_Cycle_Time, Total_Produced_Components, Machine_Utilized_Time)
                Performance_Formatted = PerformPercent if PerformPercent <= 100.00 else 100.00
                '''QUALITY CALCULATOR'''
                QualityPercent = Quality(goodCount, Total_Produced_Components)
                Quality_Formatted = QualityPercent if QualityPercent <= 100.00 else 100.00
                '''OEE CALCULATOR'''
                OEE = OeeCalculator(AvailPercent, PerformPercent, QualityPercent)
                OEE_Formatted = OEE if OEE <= 100.00 else 100.00

                availability = "{} %".format(Availability_Formatted)
                performance = "{} %".format(Performance_Formatted)
                quality = "{} %".format(round(Quality_Formatted, 2))
                targetOee = "80 %"
                oee = "{} %".format(round(OEE_Formatted, 2))
                print("\n")
                print("Availability: {}, Performance: {}, Quality: {}, OEE: {}".format(availability, performance,
                                                                                       quality, oee))
                RunningDuration_formatted = Calculation_Data["Running"]["FormattedActiveHours"]
                DownTimeDuration_formatted = Calculation_Data["Down"]["FormattedActiveHours"]

                availabilityJson = readAvailabilityFile()
                reasonCodeList: list = readDownReasonCodeFile()
                productionFile = readProductionFile()
                qualityCategories = readQualityCategory()
                defaultQualityCategories = readDefaultQualityCategory()
                availabilityJson = closeAvailabilityDocument(availabilityJson, currentTime)

                OutputArgs = {
                    "TotalProducedTotal": Total_Produced_Components,
                    "GoodCount": goodCount,
                    "BadCount": badCount,
                    "RunningDuration": RunningDuration,
                    "RunningDurationFormatted": RunningDuration_formatted,
                    "DownDuration": DownDuration,
                    "DownTimeDurationFormatted": DownTimeDuration_formatted,
                    "TotalDuration": Total_time,
                    "PlannedDowntime": Planned_Down_time,
                    "UnPlannedDowntime": UnPlanned_Down_time,
                }

                OeeArgs = {
                    "availability": availability,
                    "performance": performance,
                    "quality": quality,
                    "targetOee": targetOee,
                    "OeePercentage": oee
                }

                DisplayArgs = {
                    "mode": "Live",
                    "fromDateTime": "",
                    "toDateTime": ""
                }
                rawDbBackUp = {
                    "result": result,
                    "OeeArgs": OeeArgs,
                    "Calculation_Data":  Calculation_Data,
                    "ProductionPlan_Data": ProductionPlan_Data,
                    "OutputArgs": OutputArgs,
                    "DisplayArgs": DisplayArgs,
                    "currentTime": currentTime,
                    "availabilityJson": availabilityJson,
                    "reasonCodeList": reasonCodeList,
                    "productionFile": productionFile,
                    "qualityCategories": qualityCategories,
                    "defaultQualityCategories": defaultQualityCategories,
                }

                Output = StandardOutput(result=result,
                                        OeeArgs=OeeArgs,
                                        Calculation_Data=Calculation_Data,
                                        ProductionPlan_Data=ProductionPlan_Data,
                                        OutputArgs=OutputArgs,
                                        DisplayArgs=DisplayArgs,
                                        currentTime=currentTime,
                                        availabilityJson=availabilityJson,
                                        reasonCodeList=reasonCodeList,
                                        productionFile=productionFile,
                                        qualityCategories=qualityCategories,
                                        defaultQualityCategories=defaultQualityCategories,
                                        )
                recycleHour = int(Calculation_Data["RecycleTime"])

                topicName: str = kafkaJson.topicName
                # Kafka Producer
                producer = KafkaProducer(bootstrap_servers=[bootstrap_servers],
                                         value_serializer=lambda x: json.dumps(x).encode('utf-8'))
                producer.send(topicName, value=Output, )
                DbLogsThread(loadValue=Output,
                             rawBackUp=rawDbBackUp,
                             recycleHour=recycleHour)

        except Exception as exception:
            success = False
            print("OPCUA Reader - Device is not Connected Error:", exception)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)

        thread = threading.Thread(
            target=callback,
            args=(Properties, OPCTags, threadsCount, datasList, success)
        )
        thread.start()

    return datasList



def DbLogsThread(loadValue, rawBackUp, recycleHour: int):

    timeStamp = datetime.datetime.now()
    loadValue["Timestamp"] = timeStamp
    loadValue["RecycleHour"] = recycleHour

    col = "Logs"
    col1 = "LogsRawBackUp"
    thread = threading.Thread(
        target=Doc().DB_Write,
        args=(loadValue, col)
    )
    thread.start()

    thread1 = threading.Thread(
        target=Doc().DB_Write,
        args=(rawBackUp, col1)
    )
    thread1.start()


def closeAvailabilityDocument(availabilityDoc,currentTime):
    for index, availableObj in enumerate(availabilityDoc):
        if availableObj["Cycle"] == "Open":
            startTime = datetime.datetime.strptime(availableObj["StartTime"], gs.OEE_JsonDateTimeFormat)
            stopTime = datetime.datetime.strftime(currentTime, gs.OEE_JsonDateTimeFormat)
            Duration = currentTime - startTime
            Duration_fmt = str(Duration)
            availabilityDoc[index]["Duration"] = Duration_fmt
            availabilityDoc[index]["StopTime"] = stopTime
            availabilityDoc[index]["Cycle"] = "Closed"

    return availabilityDoc