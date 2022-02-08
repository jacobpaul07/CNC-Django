import datetime
import os
import sys
import threading
import time

from App.GeneralUtils.ResultFormatter import DurationCalculatorFormatted, productionCount_DBUpdater, productionCount_Log
from App.GeneralUtils.index import readCalculation_file, writeCalculation_file, readDownReasonCodeFile, readAvailabilityFile, \
    WriteAvailabilityFile, readQualityCategory, readProductionFile, writeProductionFile, readDefaultDownCodeJsonFile
from MongoDB_Main import Document as Doc
from App.globalsettings import GlobalFormats


def down_time_particular_time_data_updater(reason_code_list, calculation_data, availability_json,
                                           specific_date: datetime):
    try:
        read_calculation_data_json = calculation_data
        machine_id = read_calculation_data_json["MachineId"]
        recycle_hour = int(read_calculation_data_json["RecycleTime"])
        down_time_doc: list = Doc().getDowntimeDocumentForSpecificDate(RecycledHour=recycle_hour,
                                                                       specificDate=specific_date,
                                                                       machineID=machine_id)

        result = {
            "TotalDownTime": "",
            "TotalDownTImeFormatted": "",
            "TotalPlanned": "",
            "TotalPlannedFormatted": "",
            "TotalUnplanned": "",
            "TotalUnplannedFormatted": "",
            "PlannedDetails": [],
            "UnplannedDetails": []
        }

        planned_document_list = []
        unplanned_document_list = []

        # Only For Summary
        un_planned_list = list(filter(lambda x: (x["DownTimeCode"] == ""), down_time_doc))
        planned_list = list(filter(lambda x: (x["DownTimeCode"] != ""), down_time_doc))

        # updating the list of docs WITHOUT DOWNTIME CODE
        total_unknown_time = datetime.timedelta()
        if len(un_planned_list) > 0:
            for doc in un_planned_list:
                if doc["Duration"] != "":
                    doc_unknown_duration = datetime.datetime.strptime(
                        doc["Duration"], GlobalFormats.oee_json_time_format())
                    total_unknown_time = total_unknown_time + datetime.timedelta(hours=doc_unknown_duration.hour,
                                                                                 minutes=doc_unknown_duration.minute,
                                                                                 seconds=doc_unknown_duration.second)
            unknown_document = {
                "DownCode": str(0),
                "DownReasons": "",
                "color": "",
                "ActiveHours": str(total_unknown_time),
                "FormattedActiveHours": DurationCalculatorFormatted(str(total_unknown_time))
            }
            unplanned_document_list.append(unknown_document)
            result["TotalUnplanned"] = str(total_unknown_time)
            result["TotalUnplannedFormatted"] = DurationCalculatorFormatted(str(total_unknown_time))

        reason_codes = (list(str(x["DownTimeCode"]) for x in planned_list))
        reason_codes_list = (list(set(reason_codes)))
        total_planned_time = datetime.timedelta()
        total_un_planned_time = datetime.timedelta()
        for reasonCode in reason_codes_list:
            total_duration = datetime.timedelta(hours=0, minutes=0, seconds=0, microseconds=0)
            reason_code_data = list(filter(lambda x: (str(x["DownTimeCode"]) == reasonCode), planned_list))
            for doc in reason_code_data:
                if doc["Duration"] != "":
                    doc_duration = datetime.datetime.strptime(str(doc["Duration"]), "%H:%M:%S.%f")
                    total_duration = total_duration + datetime.timedelta(
                        hours=doc_duration.hour,
                        minutes=doc_duration.minute,
                        seconds=doc_duration.second)

            planned_reason_code_doc = list(filter(lambda x: (str(x["DownCode"]) == reasonCode and
                                                             str(x["Category"]) == "Planned DownTime"),
                                                  reason_code_list))

            un_planned_reason_code_doc = list(filter(lambda x: (str(x["DownCode"]) == reasonCode and
                                                                str(x["Category"]) == "UnPlanned DownTime"),
                                                     reason_code_list))

            if len(planned_reason_code_doc) > 0:
                planned_document = {
                    "DownCode": str(reasonCode),
                    "DownReasons": planned_reason_code_doc[0]["DownCodeReason"],
                    "color": planned_reason_code_doc[0]["color"],
                    "ActiveHours": str(total_duration),
                    "FormattedActiveHours": DurationCalculatorFormatted(str(total_duration))
                }
                planned_document_list.append(planned_document)
                total_planned_time = total_planned_time + total_duration

            else:
                unplanned_document = {
                    "DownCode": str(reasonCode),
                    "DownReasons": un_planned_reason_code_doc[0]["DownCodeReason"],
                    "color": un_planned_reason_code_doc[0]["color"],
                    "ActiveHours": str(total_duration),
                    "FormattedActiveHours": DurationCalculatorFormatted(str(total_duration))
                }
                unplanned_document_list.append(unplanned_document)
                total_un_planned_time = total_un_planned_time + total_duration

        total_un_planned_time = total_un_planned_time + total_unknown_time

        result["UnplannedDetails"] = unplanned_document_list
        result["PlannedDetails"] = planned_document_list
        result["TotalPlanned"] = str(total_planned_time)
        result["TotalPlannedFormatted"] = DurationCalculatorFormatted(str(total_planned_time))
        result["TotalUnplanned"] = str(total_un_planned_time)
        result["TotalUnplannedFormatted"] = DurationCalculatorFormatted(str(total_un_planned_time))
        total_planned = datetime.datetime.strptime(result["TotalPlanned"], GlobalFormats.oee_output_time_format())
        total_unplanned = datetime.datetime.strptime(result["TotalUnplanned"], GlobalFormats.oee_output_time_format())

        total_planned_delta = datetime.timedelta(hours=total_planned.hour,
                                                 minutes=total_planned.minute,
                                                 seconds=total_planned.second)
        total_unplanned_delta = datetime.timedelta(hours=total_unplanned.hour,
                                                   minutes=total_unplanned.minute,
                                                   seconds=total_unplanned.second)
        total_down_time = str(total_planned_delta + total_unplanned_delta)
        total_down_time_formatted = DurationCalculatorFormatted(total_down_time)

        result["TotalDownTime"] = total_down_time
        result["TotalDownTImeFormatted"] = total_down_time_formatted

        read_calculation_data_json_new = calculation_data
        read_calculation_data_json_new["Down"]["category"]["Planned"]["Details"] = result["PlannedDetails"]
        read_calculation_data_json_new["Down"]["category"]["Planned"]["ActiveHours"] = result["TotalPlanned"]
        read_calculation_data_json_new["Down"]["category"]["Planned"]["FormattedActiveHours"] = result[
            "TotalPlannedFormatted"]

        read_calculation_data_json_new["Down"]["category"]["Unplanned"]["Details"] = result["UnplannedDetails"]
        read_calculation_data_json_new["Down"]["category"]["Unplanned"]["ActiveHours"] = result["TotalUnplanned"]
        read_calculation_data_json_new["Down"]["category"]["Unplanned"]["FormattedActiveHours"] = result[
            "TotalUnplannedFormatted"]

        # For full detailed
        for index, availObj in enumerate(availability_json):
            avail_status = availObj["Status"]
            avail_cycle = availObj["Cycle"]

            if avail_status != "Running" and avail_cycle == "Closed":
                start_time = availObj["StartTime"]
                end_time = availObj["StopTime"]

                start_time = start_time[:-3] + "000"
                end_time = end_time[:-3] + "000"

                db_doc = list(filter(lambda x: (
                        x["Status"] == avail_status and
                        x["Cycle"] == avail_cycle and
                        str(x["StartTime"]) == start_time and
                        str(x["StopTime"] == end_time)), down_time_doc))
                if len(db_doc) > 0:
                    cdoc = db_doc[0]
                    down_code = cdoc["DownTimeCode"]
                    doc_reason_code_doc = list(filter(lambda x: (str(x["DownCode"]) == down_code), reason_code_list))
                    default_reason_code_doc = readDefaultDownCodeJsonFile()[0]
                    color = doc_reason_code_doc[0]["color"] if len(doc_reason_code_doc) > 0 else \
                        default_reason_code_doc["color"]
                    availability_json[index]["DownTimeCode"] = cdoc["DownTimeCode"]
                    availability_json[index]["Description"] = cdoc["Description"]
                    availability_json[index]["Category"] = cdoc["Category"]
                    availability_json[index]["color"] = color

        return_data = {
            "calculationData": read_calculation_data_json_new,
            "availabilityJson": availability_json,
            "result": result
        }
        return return_data

    except Exception as ex:
        print("Error in StandardOutput-Output.py", ex)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, file_name, exc_tb.tb_lineno)


def down_time_reason_updater():
    # Read DownCodeReason Json File
    reason_code_list = readDownReasonCodeFile()
    # Read CalculationData Json File
    read_calculation_data_json = readCalculation_file()
    availability_json = readAvailabilityFile()
    specific_date = datetime.datetime.now()
    result = down_time_particular_time_data_updater(reason_code_list=reason_code_list,
                                                    calculation_data=read_calculation_data_json,
                                                    availability_json=availability_json,
                                                    specific_date=specific_date)
    read_calculation_data_json_new = result["calculationData"]
    availability_json_new = result["availabilityJson"]
    writeCalculation_file(jsonFileContent=read_calculation_data_json_new)
    WriteAvailabilityFile(jsonContent=availability_json_new)


def start_timer():
    thread = threading.Thread(
        target=update_timer,
        args=()
    )
    thread.start()


def total_duration_calculator(t1: datetime, t2: datetime):
    t1_delta = datetime.timedelta(hours=t1.hour,
                                  minutes=t1.minute,
                                  seconds=t1.second)

    t2_delta = datetime.timedelta(hours=t2.hour,
                                  minutes=t2.minute,
                                  seconds=t2.second)

    total_duration_delta = t1_delta + t2_delta
    total_duration_days = total_duration_delta.days
    if total_duration_days != 0:
        total_duration_delta = total_duration_delta - datetime.timedelta(days=total_duration_days)
    return total_duration_delta


def duration_calculator(active_hours, last_update_time_stamp, current_time_stamp):
    try:
        # LastUpdateTime and Time Difference Calculation
        time_zero = datetime.datetime.strptime('00:00:00', GlobalFormats.oee_output_time_format())
        last_update_time = datetime.datetime.strptime(last_update_time_stamp, GlobalFormats.oee_json_date_time_format())
        last_update_time = last_update_time - datetime.timedelta(seconds=0)
        temp_time = current_time_stamp - last_update_time
        temp_time_days = temp_time.days
        if temp_time_days != 0:
            temp_time = temp_time - datetime.timedelta(days=temp_time_days)
        temp = str(temp_time)
        time_difference = temp.split('.')[0]
        t1 = datetime.datetime.strptime(active_hours, GlobalFormats.oee_output_time_format())
        t2 = datetime.datetime.strptime(time_difference, GlobalFormats.oee_output_time_format())
        active_hours = str((t1 - time_zero + t2).time())
        active_hours_str = DurationCalculatorFormatted(active_hours)
        return active_hours, active_hours_str

    except Exception as ex:
        print("Error in duration_calculator - MachineStatus.py", ex)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)


def update_timer():
    try:
        current_time_stamp = datetime.datetime.now()
        ''' Read CalculationData.json '''
        read_calculation_data_json = readCalculation_file()
        machine_status = read_calculation_data_json["MachineStatus"]
        timestamp = read_calculation_data_json["LastUpdatedTime"]
        # Check the machine Status

        if machine_status == "True":
            active_hours = read_calculation_data_json["Running"]["ActiveHours"]
        else:
            active_hours = read_calculation_data_json["Down"]["ActiveHours"]

        # Duration Calculator Function
        active_hours, active_hours_str = duration_calculator(active_hours=active_hours,
                                                             last_update_time_stamp=timestamp,
                                                             current_time_stamp=current_time_stamp)

        # Running & Down - Active Hrs Update
        if machine_status == "True":
            read_calculation_data_json["Running"]["ActiveHours"] = active_hours
            read_calculation_data_json["Running"]["FormattedActiveHours"] = active_hours_str
        else:
            read_calculation_data_json["Down"]["ActiveHours"] = active_hours
            read_calculation_data_json["Down"]["FormattedActiveHours"] = active_hours_str
            read_calculation_data_json = planned_unplanned_calculation(read_calculation_data_json, current_time_stamp)

        running_active_hrs = datetime.datetime.strptime(read_calculation_data_json["Running"]["ActiveHours"],
                                                        GlobalFormats.oee_output_time_format())
        down_active_hrs = datetime.datetime.strptime(read_calculation_data_json["Down"]["ActiveHours"],
                                                     GlobalFormats.oee_output_time_format())

        # Total Duration Calculator Function
        total_duration = total_duration_calculator(t1=running_active_hrs, t2=down_active_hrs)
        read_calculation_data_json["TotalDuration"] = str(total_duration)
        read_calculation_data_json["LastUpdatedTime"] = datetime.datetime.strftime(
            current_time_stamp, GlobalFormats.oee_json_date_time_format())
        writeCalculation_file(jsonFileContent=read_calculation_data_json)

    except Exception as ex:
        print("Error in update_timer - MachineStatus.py", ex)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

    time.sleep(1)

    thread = threading.Thread(
        target=start_timer,
        args=()
    )
    thread.start()


def planned_unplanned_calculation(read_calculation_data_json, current_time_stamp):
    timestamp = read_calculation_data_json["LastUpdatedTime"]
    down_reason_code = read_calculation_data_json["DownTimeReasonCode"]
    if down_reason_code != "0" and down_reason_code != "":
        reason_code_list = readDownReasonCodeFile()
        planned_details = list(filter(lambda x: (str(x["DownCode"]) == str(down_reason_code) and
                                                 str(x["Category"]) == "Planned DownTime"), reason_code_list))

        un_planned_details = list(filter(lambda x: (str(x["DownCode"]) == str(down_reason_code) and
                                                    str(x["Category"]) == "UnPlanned DownTime"), reason_code_list))

        if len(un_planned_details) > 0:
            flag = "UnPlanned"
            active_hours = read_calculation_data_json["Down"]["category"]["Unplanned"]["ActiveHours"]
            planned_details_calculation(read_calculation_data_json, un_planned_details[0], current_time_stamp, flag)
        elif len(planned_details) > 0:
            flag = "Planned"
            active_hours = read_calculation_data_json["Down"]["category"]["Planned"]["ActiveHours"]
            planned_details_calculation(read_calculation_data_json, planned_details[0], current_time_stamp, flag)
        else:
            active_hours = read_calculation_data_json["Down"]["category"]["Unplanned"]["ActiveHours"]
            unknown_details_calculation(read_calculation_data_json, current_time_stamp)

        # Duration Calculator Function
        active_hours, active_hours_str = duration_calculator(active_hours=active_hours,
                                                             last_update_time_stamp=timestamp,
                                                             current_time_stamp=current_time_stamp)

        # Running & Down - Active Hrs Update
        if len(planned_details) > 0:
            read_calculation_data_json["Down"]["category"]["Planned"]["ActiveHours"] = active_hours
            read_calculation_data_json["Down"]["category"]["Planned"]["FormattedActiveHours"] = active_hours_str

        else:
            read_calculation_data_json["Down"]["category"]["Unplanned"]["ActiveHours"] = active_hours
            read_calculation_data_json["Down"]["category"]["Unplanned"]["FormattedActiveHours"] = active_hours_str

    return read_calculation_data_json


def planned_details_calculation(read_calculation_data_json, planned_details, current_time_stamp, flag):
    reason_exist = False
    timestamp = read_calculation_data_json["LastUpdatedTime"]
    active_hours = "00:00:01"
    active_hours_str = "00h 00m 01s"
    if flag == "Planned":
        planned_object: list = read_calculation_data_json["Down"]["category"]["Planned"]["Details"]
    else:
        planned_object: list = read_calculation_data_json["Down"]["category"]["Unplanned"]["Details"]
    for obj in planned_object:
        if str(obj["DownCode"]) == str(planned_details["DownCode"]):
            active_hrs = obj["ActiveHours"]
            active_hours, active_hours_str = duration_calculator(active_hours=active_hrs,
                                                                 last_update_time_stamp=timestamp,
                                                                 current_time_stamp=current_time_stamp)
            obj["ActiveHours"] = active_hours
            obj["FormattedActiveHours"] = active_hours_str
            reason_exist = True

    if not reason_exist:
        new_planned_object = {
            "DownCode": str(planned_details["DownCode"]),
            "DownReasons": planned_details["DownCodeReason"],
            "color": planned_details["color"],
            "ActiveHours": active_hours,
            "FormattedActiveHours": active_hours_str
        }
        planned_object.append(new_planned_object)

    if flag == "Planned":
        read_calculation_data_json["Down"]["category"]["Planned"]["Details"] = planned_object
    else:
        read_calculation_data_json["Down"]["category"]["Unplanned"]["Details"] = planned_object

    return read_calculation_data_json


def unknown_details_calculation(read_calculation_data_json, current_time_stamp):
    reason_exist = False
    timestamp = read_calculation_data_json["LastUpdatedTime"]
    active_hours = "00:00:01"
    active_hours_str = "00h 00m 01s"

    unplanned_object: list = read_calculation_data_json["Down"]["category"]["Unplanned"]["Details"]

    for obj in unplanned_object:
        if str(obj["DownCode"]) == "Unplanned":
            active_hrs = obj["ActiveHours"]
            active_hours, active_hours_str = duration_calculator(active_hours=active_hrs,
                                                                 last_update_time_stamp=timestamp,
                                                                 current_time_stamp=current_time_stamp)
            obj["ActiveHours"] = active_hours
            obj["FormattedActiveHours"] = active_hours_str
            reason_exist = True

    if not reason_exist:
        new_planned_object = {
            "DownCode": "Unplanned",
            "DownReasons": "Unplanned",
            "color": "#bc07ed",
            "ActiveHours": active_hours,
            "FormattedActiveHours": active_hours_str
        }
        unplanned_object.append(new_planned_object)

    read_calculation_data_json["Down"]["category"]["Unplanned"]["Details"] = unplanned_object
    return read_calculation_data_json


def machine_running_status_updater(data, production_plan_data, current_time):
    thread = threading.Thread(target=update_availability_json_file, args=(data, current_time))
    thread.start()

    current_date = str(datetime.datetime.today().date())
    machine_id = data["MachineID"]
    job_id = data["JobID"]
    operator_id = data["OperatorID"]
    shift_id = data["ShiftID"]
    machine_status = data["PowerOn_Status"]
    down_time_reason_code = data["DownTime_ReasonCode"]
    read_calculation_data_json = readCalculation_file()
    read_calculation_data_json["MachineId"] = machine_id
    read_calculation_data_json["jobID"] = job_id
    read_calculation_data_json["operatorID"] = operator_id
    read_calculation_data_json["shiftID"] = shift_id
    read_calculation_data_json["MachineStatus"] = machine_status
    read_calculation_data_json["DownTimeReasonCode"] = down_time_reason_code
    read_calculation_data_json["CurrentDate"] = current_date

    if machine_status == "True":
        read_calculation_data_json = production_count_updater(data, read_calculation_data_json, production_plan_data,
                                                              current_time)
    writeCalculation_file(read_calculation_data_json)


def production_count_updater(data, read_calculation_data_json, production_plan_data, current_time):
    last_update_time = str(datetime.datetime.strptime(str(current_time), GlobalFormats.oee_json_date_time_format()))
    total_seconds_of_now = datetime.timedelta(hours=current_time.hour,
                                              minutes=current_time.minute,
                                              seconds=current_time.second)

    production_ideal_cycle_object = list(filter(lambda x: (x["Category"] == "IDEAL_CYCLE_TIME"), production_plan_data))
    cycle_time: int = int(float(production_ideal_cycle_object[0]["InSeconds"]))
    production_last_update_time = read_calculation_data_json["ProductionLastUpdateTime"]
    # print(ProductionLastUpdateTime)
    production_last_update_time_dt = datetime.datetime.strptime(production_last_update_time,
                                                                GlobalFormats.oee_json_date_time_format())
    production_last_update_time_seconds = datetime.timedelta(hours=production_last_update_time_dt.hour,
                                                             minutes=production_last_update_time_dt.minute,
                                                             seconds=production_last_update_time_dt.second)
    difference = total_seconds_of_now - production_last_update_time_seconds
    # print("IDEAL-TIME Difference:", abs(difference.total_seconds()))
    time_difference = abs(difference.total_seconds())
    if time_difference >= cycle_time:

        read_calculation_data_json["ProductionLastUpdateTime"] = last_update_time
        qc = data["QualityCode"]
        # read the QualityCategory File
        quality_category = readQualityCategory()
        quality_doc = list(filter(lambda x: (str(x["qualityCode"]) == str(qc)), quality_category))

        machine_id = read_calculation_data_json["MachineId"]
        job_id = read_calculation_data_json["jobID"]
        operator_id = read_calculation_data_json["operatorID"]
        shift_id = read_calculation_data_json["shiftID"]

        ''' Future Implementations'''
        # Have to change the CalculationData.json for Multiple categories in QualityCode
        if len(quality_doc) == 0:
            read_calculation_data_json["badCount"] = read_calculation_data_json["badCount"] + 1
            write_production_log(qc=qc, category="bad", count=1, current_time=current_time)
            # function to send production count --> mongoDB
        else:
            write_production_log(qc=qc, category=quality_doc[0]["category"], count=1, current_time=current_time)
            productionCount_Log(MID=machine_id, SID=shift_id, JID=job_id, OID=operator_id,
                                Category=str(quality_doc[0]["category"]).lower(),
                                TimeStamp=current_time, QualityCode=qc)

            if str(quality_doc[0]["category"]).lower() == "good":
                read_calculation_data_json["goodCount"] = read_calculation_data_json["goodCount"] + 1
                current_date = str(read_calculation_data_json["CurrentDate"])
                productionCount_DBUpdater(category="good", date=current_date, qualityCode="1",
                                          qualityId="ID001", MachineID=machine_id)
            else:
                read_calculation_data_json["badCount"] = read_calculation_data_json["badCount"] + 1
                current_date = str(read_calculation_data_json["CurrentDate"])
                productionCount_DBUpdater(category="bad", date=current_date, qualityCode="2",
                                          qualityId="ID002", MachineID=machine_id)

    return read_calculation_data_json


def write_production_log(qc, category, count, current_time):
    production_json: list = readProductionFile()
    new_production = {
        "productionTime": str(current_time),
        "category": category,
        "count": count,
        "qualityCode": qc
    }
    production_json.append(new_production)
    writeProductionFile(production_json)


def get_seconds_from_time_difference(timestamp_str):
    updated_time = datetime.datetime.strptime(timestamp_str, GlobalFormats.oee_output_time_format())
    result = datetime.timedelta(hours=updated_time.hour,
                                minutes=updated_time.minute,
                                seconds=updated_time.second).total_seconds()
    return result


def update_availability_json_file(parameter, current_time):
    timestamp = current_time
    start_time = timestamp.strftime(GlobalFormats.oee_json_date_time_format())
    # Read DownCodeReason Json File
    running_color = "#C8F3BF"
    un_planned_color = "#F8425F"
    availability_json: list = readAvailabilityFile()

    if parameter["PowerOn_Status"] == "False":
        reason_code = parameter["DownTime_ReasonCode"]
        reason_code_list = readDownReasonCodeFile()
        reason_code_doc = list(filter(lambda x: (str(x["DownCode"]) == reason_code), reason_code_list))

        if len(reason_code_doc) == 0:
            reason_code = ""
            reason_description = "Unplanned"
            color = un_planned_color
        else:
            reason_description = reason_code_doc[0]["DownCodeReason"]
            color = reason_code_doc[0]["color"]

        if len(availability_json) == 0:
            availability_json = [{
                "machineID": parameter["MachineID"], "PowerOnStatus": "OFF", "StartTime": start_time,
                "StopTime": "", "Duration": "", "Status": "Down", "Cycle": "Open",
                "DownTimeCode": reason_code, "Description": reason_description, "Category": "", "color": color}]

            WriteAvailabilityFile(availability_json)
        else:
            previous_document = availability_json[-1]
            previous_down_time_code = previous_document['DownTimeCode']

            if previous_down_time_code != reason_code:
                response_object = find_and_update_open_document(availability_json=availability_json,
                                                                cycle_status="Open",
                                                                running_status="Down",
                                                                timestamp=timestamp
                                                                )
            else:
                response_object = find_and_update_open_document(availability_json=availability_json,
                                                                cycle_status="Open",
                                                                running_status="Running",
                                                                timestamp=timestamp
                                                                )

            availability_json = response_object["availabilityJson"]
            document_found = response_object["cycleDocumentIsAvailable"]
            if document_found is True:
                availability_doc = {
                    "machineID": parameter["MachineID"], "PowerOnStatus": "OFF", "StartTime": start_time,
                    "StopTime": "", "Duration": "", "Status": "Down", "Cycle": "Open",
                    "DownTimeCode": reason_code, "Description": reason_description, "Category": "", "color": color}

                availability_json.append(availability_doc)
                WriteAvailabilityFile(availability_json)
    else:

        if len(availability_json) == 0:
            availability_json = [{
                "machineID": parameter["MachineID"], "PowerOnStatus": "ON", "StartTime": start_time,
                "StopTime": "", "Duration": "", "Status": "Running", "Cycle": "Open",
                "DownTimeCode": "", "Description": "", "Category": "", "color": running_color}]

            WriteAvailabilityFile(availability_json)
        else:

            response_object = find_and_update_open_document(availability_json=availability_json,
                                                            cycle_status="Open",
                                                            running_status="Down",
                                                            timestamp=timestamp)

            availability_json = response_object["availabilityJson"]
            document_found = response_object["cycleDocumentIsAvailable"]

            if document_found is True:
                availability_doc = {
                    "machineID": parameter["MachineID"], "PowerOnStatus": "ON", "StartTime": start_time,
                    "StopTime": "", "Duration": "", "Status": "Running", "Cycle": "Open",
                    "DownTimeCode": "", "Description": "", "Category": "", "color": running_color}

                availability_json.append(availability_doc)
                WriteAvailabilityFile(availability_json)


def find_and_update_open_document(availability_json, cycle_status, running_status, timestamp):
    current_cycle_index = 0
    current_cycle_doc = None

    for i, obj in enumerate(availability_json):
        # obj = availabilityJson[i]
        if obj["Cycle"] == cycle_status and obj["Status"] == running_status:
            current_cycle_index = i
            current_cycle_doc = obj

    cycle_document_is_available = current_cycle_doc is not None
    if cycle_document_is_available:
        temp_end_time = timestamp
        temp_start_time = current_cycle_doc["StartTime"]
        temp_start_time_datetime = datetime.datetime.strptime(str(temp_start_time),
                                                              GlobalFormats.oee_json_date_time_format())

        temp_duration = temp_end_time - temp_start_time_datetime
        temp_time_days = temp_duration.days
        if temp_time_days != 0:
            temp_duration = temp_duration - datetime.timedelta(days=temp_time_days)

        temp_duration_str = str(temp_duration)

        current_cycle_doc["StopTime"] = str(temp_end_time)
        current_cycle_doc["Duration"] = str(temp_duration_str)
        current_cycle_doc["Cycle"] = "Closed"
        availability_json[current_cycle_index] = current_cycle_doc

    return_object = {
        "availabilityJson": availability_json,
        "cycleDocumentIsAvailable": cycle_document_is_available
    }

    return return_object
