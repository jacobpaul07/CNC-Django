import json
import threading
import datetime
from App.CNC_Calculation.MachineStatus import machineStatus
from MongoDB_Main import Document as Doc
from App.CNC_Calculation.APQ import Availability, Productivity, Quality
from App.Json_Class.index import read_setting
from kafka import KafkaProducer
from opcua import Client
from App.Json_Class.OPCUAParameters import OPCParameters
from App.Json_Class.OPCUAProperties import OPCProperties
from App.OPCUA.Output import StandardOutput
from App.OPCUA.ResultFormatter import dataValidation, MachineStatus, Duration_Calculator


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
                    result[header] = datasList[index]["value"]

                returnValue = dataValidation(result)
                machineStatus(result)
                QC = result["QualityCode"]
                if QC == 1001 or QC == 1003 or QC == 1005 or QC == 1:
                    Doc().Increment_Value(col="Running", MID="MID-01", value="goodCount")
                elif QC == 1002 or QC == 1004 or QC == 1006 or QC == 2:
                    Doc().Increment_Value(col="Running", MID="MID-01", value="badCount")

                Running = Doc().ReadDBQuery(col="Running", query={"MachineId": "MID-01"})
                Down = Doc().ReadDBQuery(col="Down", query={"MachineId": "MID-01"})
                if Running is None:
                    insertData = MachineStatus(currentTime)
                    Doc().DB_Write(col="Running", data=insertData)
                elif Down is None:
                    insertData = MachineStatus(currentTime)
                    Doc().DB_Write(col="Down", data=insertData)
                elif Running and Down:
                    RunningDuration_Str = Running["TotalDuration"]
                    RunningDuration = Duration_Calculator(RunningDuration_Str)
                    DownDuration_Str = Down["TotalDuration"]
                    DownDuration = Duration_Calculator(DownDuration_Str)
                    Total_time = RunningDuration + DownDuration
                    Planned_Down_time = float(0)
                    Total_Unplanned_Downtime = DownDuration
                    AvailPercent, Machine_Utilized_Time = Availability(Total_time, Planned_Down_time,
                                                                       Total_Unplanned_Downtime)
                    goodCount = int(Running["goodCount"])
                    badCount = int(Running["badCount"])
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

                    OutputArgs = {
                        "TotalProducedTotal": Total_Produced_Components,
                        "GoodCount": goodCount,
                        "BadCount": badCount,
                        "RunningDuration": round(RunningDuration, 3),
                        "DownDuration": round(DownDuration, 3),
                        "TotalDuration": round(Total_time, 3)
                    }

                    Output = StandardOutput(result=result,
                                            availability=availability,
                                            performance=performance,
                                            quality=quality,
                                            targetOee=targetOee,
                                            OeePercentage=oee,
                                            OutputArgs=OutputArgs)

                    topicName: str = kafkaJson.topicName
                    producer.send(topicName, value=Output)
                # print("Kafka Producer Status", val)
                # print(str(datasList))

        except Exception as exception:
            success = False
            print("Device is not Connected Error:", exception)
        # Encoding as byte Data for KAFKA
        # encoded_data = json.dumps(datasList).encode('utf-8')

        thread = threading.Thread(
            target=callback,
            args=(Properties, OPCTags, threadsCount, datasList, success)
        )
        thread.start()

    return datasList
