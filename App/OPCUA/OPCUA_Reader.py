import json
import os
import sys
import threading
import datetime
from App.CNC_Calculation.MachineStatus import machineRunningStatus_Updater, getSeconds_fromTimeDifference
from App.OPCUA.index import readCalculation_file, readProductionPlanFile
from App.CNC_Calculation.APQ import Availability, Productivity, Quality, OeeCalculator
from App.Json_Class.index import read_setting
from kafka import KafkaProducer
from opcua import Client
from App.Json_Class.OPCUAParameters import OPCParameters
from App.Json_Class.OPCUAProperties import OPCProperties
from App.OPCUA.Output import StandardOutput
from App.OPCUA.ResultFormatter import dataValidation


def ReadOPCUA(Properties: OPCProperties, OPCTags: OPCParameters, threadsCount, callback):
    success = True
    datasList: list = []
    jsonObject = read_setting()
    kafkaJson = jsonObject.edgedevice.Service.Kafka
    bootstrap_servers: str = kafkaJson.bootstrap_servers
    producer = KafkaProducer(bootstrap_servers=[bootstrap_servers],
                             value_serializer=lambda x:
                             json.dumps(x).encode('utf-8'))

    if Properties.Enable == "true" or Properties.Enable == "True":
        url: str = Properties.url
        client = Client(url)
        currentTime = datetime.datetime.now()
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
                    args=[result]
                )
                thread.start()

                machineRunningStatus_Updater_thread = threading.Thread(
                    target=machineRunningStatus_Updater,
                    args=(result, ProductionPlan_Data)
                )
                machineRunningStatus_Updater_thread.start()

                Total_time = getSeconds_fromTimeDifference(Calculation_Data["TotalDuration"])
                Planned_Down_time = getSeconds_fromTimeDifference(Calculation_Data["Down"]["category"]["Planned"]["ActiveHours"])
                UnPlanned_Down_time = getSeconds_fromTimeDifference(Calculation_Data["Down"]["category"]["Unplanned"]["ActiveHours"])
                Total_Unplanned_Downtime = getSeconds_fromTimeDifference(Calculation_Data["Down"]["ActiveHours"])
                goodCount = int(Calculation_Data["goodCount"])
                badCount = int(Calculation_Data["badCount"])
                RunningDuration = getSeconds_fromTimeDifference(Calculation_Data["Running"]["ActiveHours"])
                DownDuration = getSeconds_fromTimeDifference(Calculation_Data["Down"]["ActiveHours"])

                Standard_Cycle_Time = float(result["IdealCycleTime"])
                Total_Produced_Components = goodCount + badCount

                '''AVAILABILITY CALCULATOR'''
                AvailPercent, Machine_Utilized_Time = Availability(Total_Unplanned_Downtime)
                '''PERFORMANCE CALCULATOR'''
                PerformPercent = Productivity(Standard_Cycle_Time, Total_Produced_Components, Machine_Utilized_Time)
                '''QUALITY CALCULATOR'''
                QualityPercent = Quality(goodCount, Total_Produced_Components)
                '''OEE CALCULATOR'''
                OEE = OeeCalculator(AvailPercent, PerformPercent, QualityPercent)

                availability = "{} %".format(AvailPercent)
                performance = "{} %".format(PerformPercent)
                quality = "{} %".format(round(QualityPercent, 2))
                targetOee = "80 %"
                oee = "{} %".format(round(OEE, 2))
                RunningDuration_formatted = Calculation_Data["Running"]["FormattedActiveHours"]
                DownTimeDuration_formatted = Calculation_Data["Down"]["FormattedActiveHours"]

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

                Output = StandardOutput(result=result,
                                        OeeArgs=OeeArgs,
                                        Calculation_Data=Calculation_Data,
                                        ProductionPlan_Data=ProductionPlan_Data,
                                        OutputArgs=OutputArgs)

                topicName: str = kafkaJson.topicName
                # Kafka Producer
                producer.send(topicName, value=Output)

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
