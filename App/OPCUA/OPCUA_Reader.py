import json
import threading
import datetime
from App.CNC_Calculation.MachineStatus import machineStatus, machineRunningStatus_Updater, getSeconds_fromTimeDifference
from App.OPCUA.index import read_json_file, write_json_file, readCalculation_file
from MongoDB_Main import Document as Doc
from App.CNC_Calculation.APQ import Availability, Productivity, Quality
from App.Json_Class.index import read_setting
from kafka import KafkaProducer
from opcua import Client
from App.Json_Class.OPCUAParameters import OPCParameters
from App.Json_Class.OPCUAProperties import OPCProperties
from App.OPCUA.Output import StandardOutput
from App.OPCUA.ResultFormatter import dataValidation, MachineStatus, Duration_Calculator, DurationCalculatorFormatted


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
        # try:
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
                result[header] = datasList[index]["value"]

            thread = threading.Thread(
                target=dataValidation,
                args=[result]
            )
            thread.start()

            machineRunningStatus_Updater_thread = threading.Thread(
                target=machineRunningStatus_Updater,
                args=[result]
            )
            machineRunningStatus_Updater_thread.start()

            Calculation_Data = readCalculation_file()

            Total_time = getSeconds_fromTimeDifference(Calculation_Data["TotalDuration"])
            Planned_Down_time = float(0)
            Total_Unplanned_Downtime = getSeconds_fromTimeDifference(Calculation_Data["Down"]["ActiveHours"])
            goodCount = int(Calculation_Data["goodCount"])
            badCount = int(Calculation_Data["badCount"])
            RunningDuration = getSeconds_fromTimeDifference(Calculation_Data["Running"]["ActiveHours"])
            DownDuration = getSeconds_fromTimeDifference(Calculation_Data["Down"]["ActiveHours"])

            Standard_Cycle_Time = 60
            Total_Produced_Components = goodCount + badCount

            AvailPercent, Machine_Utilized_Time = Availability(Total_time, Planned_Down_time,
                                                               Total_Unplanned_Downtime)
            PerformPercent = Productivity(Standard_Cycle_Time, Total_Produced_Components, Machine_Utilized_Time)
            QualityPercent = Quality(goodCount, Total_Produced_Components)
            OEE = (((AvailPercent / 100) * (PerformPercent / 100) * (QualityPercent / 100)) * 100)

            availability = "{} %".format(AvailPercent)
            performance = "{} %".format(PerformPercent)
            quality = "{} %".format(round(QualityPercent, 2))
            targetOee = "88 %"
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
                "TotalDuration": Total_time
            }
            Output = StandardOutput(result=result,
                                    availability=availability,
                                    performance=performance,
                                    quality=quality,
                                    targetOee=targetOee,
                                    OeePercentage=oee,
                                    OutputArgs=OutputArgs)

            # if result["PowerOn_Status"] == "True":
            #     activeHours = RunningDuration_Str
            # else:
            #     activeHours = DownDuration_Str
            #
            # tempJson = {
            #         "machineStatus": result["PowerOn_Status"],
            #         "LastUpdateTime": str(currentTime),
            #         "ActiveHours": activeHours
            #     }
            #
            # filePath = './App/OPCUA/tempCalculation.json'
            # with open(filePath, "w") as f:
            #     dumpedJson = json.dumps(tempJson, indent=4)
            #     f.write(dumpedJson)

            topicName: str = kafkaJson.topicName
            # Kafka Producer
            producer.send(topicName, value=Output)

        # except Exception as exception:
        #     success = False
        #     print("Device is not Connected Error:", exception)
        # Encoding as byte Data for KAFKA
        # encoded_data = json.dumps(datasList).encode('utf-8')

        thread = threading.Thread(
            target=callback,
            args=(Properties, OPCTags, threadsCount, datasList, success)
        )
        thread.start()

    return datasList
