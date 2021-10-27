import json
import threading
import datetime
from App.CNC_Calculation.MachineStatus import machineStatus
from App.OPCUA.index import read_json_file, write_json_file
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
    # producer = KafkaProducer(bootstrap_servers="localhost:9092")
    jsonObject = read_setting()
    kafkaJson = jsonObject.edgedevice.Service.Kafka
    bootstrap_servers: str = kafkaJson.bootstrap_servers
    producer = KafkaProducer(bootstrap_servers=[bootstrap_servers],
                             value_serializer=lambda x:
                             json.dumps(x).encode('utf-8'))

    if Properties.Enable == "true" or Properties.Enable == "True":
        url: str = Properties.url
        client = Client(url)
        # timeStamp = datetime.now().strftime("%Y-%m-%dT%I:%M:%S_%p")
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

            # dataValidation(result)

            # QC = result["QualityCode"]
            # if QC == 1001 or QC == 1003 or QC == 1005 or QC == 1:
            #     Doc().Increment_Value(col="Running", MID="MID-01", value="goodCount")
            # elif QC == 1002 or QC == 1004 or QC == 1006 or QC == 2:
            #     Doc().Increment_Value(col="Running", MID="MID-01", value="badCount")

            Running_Json = read_json_file("./App/JsonDataBase/Running.json")
            Down_Json = read_json_file("./App/JsonDataBase/Down.json")
            if Running_Json is None:
                json_insertData = MachineStatus(str(currentTime))
                write_json_file(filePath="./App/JsonDataBase/Running.json",
                                jsonFileContent=json_insertData)

            elif Down_Json is None:
                json_insertData = MachineStatus(str(currentTime))
                write_json_file(filePath="./App/JsonDataBase/Down.json",
                                jsonFileContent=json_insertData)

            # Running = Doc().ReadDBQuery(col="Running", query={"MachineId": "MID-01"})
            # Down = Doc().ReadDBQuery(col="Down", query={"MachineId": "MID-01"})
            #
            # if Running is None:
            #     insertData = MachineStatus(currentTime)
            #     Doc().DB_Write(col="Running", data=insertData)
            # elif Down is None:
            #     insertData = MachineStatus(currentTime)
            #     Doc().DB_Write(col="Down", data=insertData)
            elif Running_Json and Down_Json:

                machineStatus(result, Running_Json, Down_Json)
                QC = result["QualityCode"]
                if QC == 1001 or QC == 1003 or QC == 1005 or QC == 1:
                    Running_Json["goodCount"] = Running_Json["goodCount"] + 1
                    a_file = open("./App/JsonDataBase/Running.json", "w")
                    json.dump(Running_Json, a_file, indent=4)
                    # Doc().Increment_Value(col="Running", MID="MID-01", value="goodCount")
                elif QC == 1002 or QC == 1004 or QC == 1006 or QC == 2:
                    Running_Json["badCount"] = Running_Json["badCount"] + 1
                    a_file = open("./App/JsonDataBase/Running.json", "w")
                    json.dump(Running_Json, a_file, indent=4)
                    # Doc().Increment_Value(col="Running", MID="MID-01", value="badCount")

                RunningDuration_Str = Running_Json["TotalDuration"]
                RunningDuration = Duration_Calculator(RunningDuration_Str)
                DownDuration_Str = Down_Json["TotalDuration"]
                DownDuration = Duration_Calculator(DownDuration_Str)
                Total_time = RunningDuration + DownDuration
                Planned_Down_time = float(0)
                Total_Unplanned_Downtime = DownDuration
                AvailPercent, Machine_Utilized_Time = Availability(Total_time, Planned_Down_time,
                                                                   Total_Unplanned_Downtime)
                goodCount = int(Running_Json["goodCount"])
                badCount = int(Running_Json["badCount"])
                Total_Produced_Components = goodCount + badCount
                Standard_Cycle_Time = 60
                PerformPercent = Productivity(Standard_Cycle_Time, Total_Produced_Components, Machine_Utilized_Time)
                QualityPercent = Quality(goodCount, Total_Produced_Components)
                OEE = (((AvailPercent / 100) * (PerformPercent / 100) * (QualityPercent / 100)) * 100)

                availability = "{} %".format(AvailPercent)
                performance = "{} %".format(PerformPercent)
                quality = "{} %".format(round(QualityPercent, 2))
                targetOee = "88 %"
                oee = "{} %".format(round(OEE, 2))
                RunningDuration_formatted = DurationCalculatorFormatted(RunningDuration_Str)
                DownTimeDuration_formatted = DurationCalculatorFormatted(DownDuration_Str)
                OutputArgs = {
                    "TotalProducedTotal": Total_Produced_Components,
                    "GoodCount": goodCount,
                    "BadCount": badCount,
                    "RunningDuration": round(RunningDuration, 3),
                    "RunningDurationFormatted": RunningDuration_formatted,
                    "DownDuration": round(DownDuration, 3),
                    "DownTimeDurationFormatted": DownTimeDuration_formatted,
                    "TotalDuration": round(Total_time, 3)
                }
                Output = StandardOutput(result=result,
                                        availability=availability,
                                        performance=performance,
                                        quality=quality,
                                        targetOee=targetOee,
                                        OeePercentage=oee,
                                        OutputArgs=OutputArgs)

                if result["PowerOn_Status"] == "True":
                    activeHours = RunningDuration_Str
                else:
                    activeHours = DownDuration_Str

                tempJson = {
                        "machineStatus": result["PowerOn_Status"],
                        "LastUpdateTime": str(currentTime),
                        "ActiveHours": activeHours
                    }

                filePath = './App/OPCUA/tempCalculation.json'
                with open(filePath, "w") as f:
                    dumpedJson = json.dumps(tempJson, indent=4)
                    f.write(dumpedJson)

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
