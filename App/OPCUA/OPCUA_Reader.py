import json
import os
import sys
import threading
import datetime
import dateutil.parser

from App.CNC_Calculation.MachineStatus import machine_running_status_updater, get_seconds_from_time_difference
from App.GeneralUtils.index import readCalculation_file, readProductionPlanFile, readAvailabilityFile, \
    readDownReasonCodeFile, \
    readProductionFile, readQualityCategory, readDefaultQualityCategory
from App.CNC_Calculation.APQ import Availability, Productivity, Quality, OeeCalculator
from App.Json_Class.index import read_setting
from opcua import Client
from App.Json_Class.OPCUAParameters import OPCParameters
from App.Json_Class.OPCUAProperties import OPCProperties
from App.OPCUA.Output import StandardOutput
from App.GeneralUtils.ResultFormatter import dataValidation
from MongoDB_Main import Document as Doc
from App.globalsettings import GlobalFormats
from confluent_kafka import Producer


def publishToKafka(kafkaServer: str, kafkaTopic: str, message):
    try:
        config = {'bootstrap.servers': kafkaServer}
        # Create Producer instance
        producer = Producer(config)

        # Optional per-message delivery callback (triggered by poll() or flush())
        # when a message has been successfully delivered or permanently failed delivery (after retries).

        def delivery_callback(err, msg):
            if err:
                print('ERROR: Message failed delivery: {}'.format(err))

        # Produce data by selecting random values from these lists.
        producer.produce(topic=kafkaTopic, value=message, callback=delivery_callback)
        # Block until the messages are sent.
        producer.poll(10000)
        producer.flush()

    except Exception as ex:
        print("Kafka Producer Error: ", ex)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fName = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fName, exc_tb.tb_lineno)


def ReadOPCUA(Properties: OPCProperties, OPCTags: OPCParameters, threadsCount, callback):
    currentTime: datetime = datetime.datetime.now()
    print("TimeStamp", currentTime)
    success = True
    datas_list: list = []

    if Properties.Enable == "true" or Properties.Enable == "True":
        url: str = Properties.url
        client = Client(url)
        try:
            client.connect()
            # read 8 registers at address 0, store result in regs list
            for tags in OPCTags.MeasurementTag:
                name_space = tags.NameSpace
                identifier = tags.Identifier
                DisplayName = tags.DisplayName
                register = client.get_node("ns={0};i={1}".format(name_space, identifier))
                register_value = register.get_value()

                data = {
                    "DisplayName": DisplayName,
                    "value": register_value
                }
                datas_list.append(data)

            # if success display registers
            format_data_and_send_to_kafka(datas_list=datas_list, currentTime=currentTime)


        except Exception as exception:
            success = False
            print("OPCUA Reader - Device is not Connected Error:", exception)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fName = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fName, exc_tb.tb_lineno)

        thread = threading.Thread(
            target=callback,
            args=(Properties, OPCTags, threadsCount, datas_list, success)
        )
        thread.start()
    return datas_list


def format_data_and_send_to_kafka(datas_list, currentTime):
    try:

        json_object = read_setting()
        kafka_json = json_object.edgedevice.Service.Kafka
        bootstrap_servers: str = kafka_json.bootstrap_servers
        cloud_enabled: str = kafka_json.cloudEnabled
        cloud_servers: str = kafka_json.cloudServers

        if datas_list:
            headers = ["CycleStart_Status", "DownTime_ReasonCode", "DownTime_Status", "EmgStop_Status",
                       "IdealCycleTime",
                       "JobID", "MachineID", "OperatorID", "PowerOn_Status", "ProductionStart", "QualityCode",
                       "ShiftID"]

            # Result dictionary
            result = {}
            for index, header in enumerate(headers):
                result[header] = str(datas_list[index]["value"])
            print("Result", result)

            Calculation_Data = readCalculation_file()
            ProductionPlan_Data = readProductionPlanFile()

            # DB Write Function
            thread = threading.Thread(
                target=dataValidation,
                args=(result, currentTime)
            )
            thread.start()

            machine_running_status_updater_thread = threading.Thread(
                target=machine_running_status_updater,
                args=(result, ProductionPlan_Data, currentTime)
            )
            machine_running_status_updater_thread.start()

            total_time = get_seconds_from_time_difference(Calculation_Data["TotalDuration"])
            planned_down_time = get_seconds_from_time_difference(
                Calculation_Data["Down"]["category"]["Planned"]["ActiveHours"])
            un_planned_down_time = get_seconds_from_time_difference(
                Calculation_Data["Down"]["category"]["Unplanned"]["ActiveHours"])
            # Total_Unplanned_Downtime = get_seconds_from_time_difference(Calculation_Data["Down"]["ActiveHours"])
            goodCount = int(Calculation_Data["goodCount"])
            badCount = int(Calculation_Data["badCount"])
            RunningDuration = get_seconds_from_time_difference(Calculation_Data["Running"]["ActiveHours"])
            DownDuration = get_seconds_from_time_difference(Calculation_Data["Down"]["ActiveHours"])

            standard_cycle_time = float(result["IdealCycleTime"])
            total_produced_components = goodCount + badCount

            '''AVAILABILITY CALCULATOR'''
            avail_percent, machine_utilized_time = Availability(un_planned_down_time)
            availability_formatted = avail_percent if avail_percent <= 100.00 else 100.00
            '''PERFORMANCE CALCULATOR'''
            perform_percent = Productivity(standard_cycle_time, total_produced_components, total_time)
            performance_formatted = perform_percent if perform_percent <= 100.00 else 100.00
            '''QUALITY CALCULATOR'''
            quality_percent = Quality(goodCount, total_produced_components)
            quality_formatted = quality_percent if quality_percent <= 100.00 else 100.00
            '''OEE CALCULATOR'''
            OEE = OeeCalculator(avail_percent, perform_percent, quality_percent)
            oee_formatted = OEE if OEE <= 100.00 else 100.00

            availability = "{}".format(availability_formatted)
            performance = "{}".format(performance_formatted)
            quality = "{}".format(round(quality_formatted, 2))
            production_object = list(filter(lambda x: (x["Category"] == "TARGET_OEE"), ProductionPlan_Data))
            if len(production_object) == 0:
                targetOee = "100.0"
            else:
                target = float(production_object[0]["InSeconds"])
                targetOee = "{}".format(round(target, 2))
            oee = "{}".format(round(oee_formatted, 2))
            # print("Availability: {}, Performance: {}, Quality: {}, OEE: {}, TargetOee: {}".format(
            #     availability, performance, quality, oee, targetOee))
            running_duration_formatted = Calculation_Data["Running"]["FormattedActiveHours"]
            down_time_duration_formatted = Calculation_Data["Down"]["FormattedActiveHours"]

            availabilityJson = readAvailabilityFile()
            reasonCodeList: list = readDownReasonCodeFile()
            productionFile = readProductionFile()
            qualityCategories = readQualityCategory()
            defaultQualityCategories = readDefaultQualityCategory()
            availabilityJson = closeAvailabilityDocument(availabilityJson, currentTime)

            output_args = {
                "TotalProducedTotal": total_produced_components,
                "GoodCount": goodCount,
                "BadCount": badCount,
                "RunningDuration": RunningDuration,
                "RunningDurationFormatted": running_duration_formatted,
                "DownDuration": DownDuration,
                "DownTimeDurationFormatted": down_time_duration_formatted,
                "TotalDuration": total_time,
                "PlannedDowntime": planned_down_time,
                "UnPlannedDowntime": un_planned_down_time,
            }

            oee_args = {
                "availability": availability,
                "performance": performance,
                "quality": quality,
                "targetOee": targetOee,
                "OeePercentage": oee
            }

            display_args = {
                "mode": "Live",
                "fromDateTime": "",
                "toDateTime": ""
            }

            recycle_hour = int(Calculation_Data["RecycleTime"])
            output = StandardOutput(result=result,
                                    OeeArgs=oee_args,
                                    Calculation_Data=Calculation_Data,
                                    ProductionPlan_Data=ProductionPlan_Data,
                                    OutputArgs=output_args,
                                    DisplayArgs=display_args,
                                    currentTime=currentTime,
                                    availabilityJson=availabilityJson,
                                    reasonCodeList=reasonCodeList,
                                    productionFile=productionFile,
                                    qualityCategories=qualityCategories,
                                    defaultQualityCategories=defaultQualityCategories,
                                    recycleHour=recycle_hour)

            # Kafka Producer Local
            topic_name: str = kafka_json.topicName
            kafka_message = json.dumps(output, indent=4)
            publishToKafka(kafkaServer=bootstrap_servers, kafkaTopic=topic_name, message=kafka_message)
            print("Kafka Produced --> 'local'")

            # Kafka Producer Web
            if cloud_enabled == "True":
                publishToKafka(kafkaServer=cloud_servers, kafkaTopic=topic_name, message=kafka_message)
                print("Kafka Produced --> 'WEB'")
            db_logs_thread(load_value=output)

    except Exception as exception:
        print("OPCUA Reader - Device is not Connected Error:", exception)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fName = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fName, exc_tb.tb_lineno)


def db_logs_thread(load_value):
    load_value["Timestamp"] = dateutil.parser.parse(load_value["Timestamp"])
    logs_backup_collection_name = "Logs"
    thread_logs_backup = threading.Thread(
        target=Doc().DB_Write,
        args=(load_value, logs_backup_collection_name)
    )
    thread_logs_backup.start()


def closeAvailabilityDocument(availabilityDoc, currentTime):
    for index, availableObj in enumerate(availabilityDoc):
        if availableObj["Cycle"] == "Open":
            start_time = datetime.datetime.strptime(availableObj["StartTime"],
                                                    GlobalFormats.oee_json_date_time_format())
            stop_time = datetime.datetime.strftime(currentTime, GlobalFormats.oee_json_date_time_format())
            duration = currentTime - start_time

            different_days = int(duration.days)
            if different_days != 0:
                duration = duration - datetime.timedelta(days=different_days)

            duration_fmt = str(duration)
            availabilityDoc[index]["Duration"] = duration_fmt
            availabilityDoc[index]["StopTime"] = stop_time
            availabilityDoc[index]["Cycle"] = "Closed"

    return availabilityDoc
