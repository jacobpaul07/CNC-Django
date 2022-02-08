import json
import datetime
from App.globalsettings import GlobalFormats
from django.http import HttpResponse
from rest_framework.views import APIView
from MongoDB_Main import Document as Doc
from App.CNC_Calculation.MachineApi import MachineApi
from App.GeneralUtils.index import readCalculation_file, get_device_id
from App.CNC_Calculation.APQ import AvailabilityCalculation, ProductionCalculation, Quality, OeeCalculator
from App.GeneralUtils.ResultFormatter import DurationCalculatorFormatted1, Duration_Converter_Formatted, get_duration


class GetMachineId(APIView):
    @staticmethod
    def get(request):
        read_calculation_data_json = readCalculation_file()

        default_data = {
            "machineID": read_calculation_data_json["MachineId"]
        }
        json_response = json.dumps(default_data, indent=4)
        return HttpResponse(json_response, "application/json")


class GetProductionReport(APIView):
    @staticmethod
    def get(request):

        chart_details = [
            {
                "name": "good",
                "color": "#68C455",
                "showAxis": True,
                "leftSide": False
            },
            {
                "name": "bad",
                "color": "#F8425F",
                "showAxis": True,
                "leftSide": False
            },
            {
                "name": "totalproduction",
                "color": "#7D30FA",
                "showAxis": True,
                "leftSide": False
            },
            {
                "name": "expected",
                "color": "#2C203F",
                "showAxis": True,
                "leftSide": False
            }
        ]
        params = get_args_from_params(request=request)
        from_date = params["from_date"]
        to_date = params["to_date"]
        device_id = params["device_id"]
        device_id = device_id.replace("_", "-")

        # DataBase Documents
        production_history_documents = MachineApi.get_production_history(from_date=from_date, to_date=to_date,
                                                                         machine_id=device_id)
        availability_document = Doc().Read_Availability_Document(fromDate=from_date, toDate=to_date,
                                                                 machineID=device_id)
        # DownTimeDocument = Doc().DB_Read(col="DownTimeCode")
        down_time_document = Doc().Read_Multiple_Document(col="DownTimeCode", query={"machineID": device_id})
        quality_document = Doc().Read_Productivity_Document(startDateTime=from_date, EndDateTime=to_date,
                                                            machineID=device_id)

        production_report_list = []
        index = 0
        day_count = (to_date - from_date).days + 1
        # it is a date loop
        for singleDate in (from_date + datetime.timedelta(n) for n in range(day_count)):

            index = index + 1
            current_date = datetime.datetime.strftime(singleDate, GlobalFormats.oee_output_date_time_format())

            current_date_production_history = list(filter(lambda x: (
                    datetime.datetime.strftime(x["timeStamp"], GlobalFormats.oee_output_date_time_format()) == current_date),
                                                          production_history_documents))

            production_plan = current_date_production_history
            standard_cycle_list = list(filter(lambda x: (x["Category"] == "IDEAL_CYCLE_TIME"), production_plan))
            shift_list = list(filter(lambda x: (x["Category"] == "SHIFT"), production_plan))
            standard_cycle_time = 0 if len(standard_cycle_list) == 0 else float(standard_cycle_list[0]["InSeconds"])

            ''' multiple operators and Jobs are not handled, need to be implemented in future'''

            for shifts in shift_list:
                shift_name = shifts["Name"]
                duration = shifts["InSeconds"]
                shift_start_time_str = shifts["ShiftStartTime"]
                shift_end_time_str = shifts["ShiftEndTime"]
                shift_start_time = datetime.datetime.strptime(shift_start_time_str, GlobalFormats.oee_excel_date_time_format())
                shift_end_time = datetime.datetime.strptime(shift_end_time_str, GlobalFormats.oee_excel_date_time_format())

                shift_start_time_tz = datetime.datetime.strptime(shift_start_time_str,
                                                                 GlobalFormats.oee_excel_date_time_format()).replace(tzinfo=None)
                shift_end_time_tz = datetime.datetime.strptime(shift_end_time_str,
                                                               GlobalFormats.oee_excel_date_time_format()).replace(tzinfo=None)

                shift_availability = list(filter(lambda x: (x["StartTime"] >= shift_start_time_tz or
                                                            x["StopTime"] <= shift_end_time_tz), availability_document))

                operator_code = "-" if len(shift_availability) == 0 else shift_availability[0]["OID"]
                job_code = "-" if len(shift_availability) == 0 else shift_availability[0]["JID"]

                quality_document_list = list(filter(lambda x: (
                        shift_start_time <= x["timeStamp"] <= shift_end_time), quality_document))

                good_count_list = list(
                    filter(lambda x: (str(x["category"]).lower() == "good"), quality_document_list))
                bad_count_list = list(
                    filter(lambda x: (str(x["category"]).lower() == "bad"), quality_document_list))

                good_production_count = len(good_count_list)
                bad_production_count = len(bad_count_list)
                total_production_count = int(good_production_count + bad_production_count)

                # Unplanned down duration begin
                un_planned_down_object = list(filter(lambda x: (x["StartTime"] >= shift_start_time_tz and
                                                                x["StopTime"] <= shift_end_time_tz and
                                                                x["DownTimeCode"] == "" and x["Status"] == "Down"),
                                                     shift_availability))

                planned_down_object = list(filter(lambda x: (x["StartTime"] >= shift_start_time_tz and
                                                             x["StopTime"] <= shift_end_time_tz and
                                                             x["DownTimeCode"] != "" and x["Status"] == "Down"),
                                                  shift_availability))

                for planned_obj in planned_down_object:
                    category_list = list(
                        filter(lambda x: (x["DownCode"] == planned_obj["DownTimeCode"]), down_time_document))
                    if len(category_list) > 0:
                        if category_list[0]["Category"] == "UnPlanned DownTime":
                            un_planned_down_object.append(planned_obj)

                un_planned_down_duration_delta = datetime.timedelta()
                for durationTime in un_planned_down_object:
                    un_planned_duration_time_str = durationTime["Duration"]
                    un_planned_duration_delta = datetime.datetime.strptime(
                        un_planned_duration_time_str, GlobalFormats.oee_json_time_format())
                    un_planned_down_duration_delta = un_planned_down_duration_delta + datetime.timedelta(
                        hours=un_planned_duration_delta.hour,
                        minutes=un_planned_duration_delta.minute,
                        seconds=un_planned_duration_delta.second)
                # Unplanned down duration end

                run_time_report = list(filter(lambda x: (x["Status"] == "Running"), shift_availability))

                total_running_duration_delta = datetime.timedelta()
                for durationTime in run_time_report:
                    running_duration_time_str = durationTime["Duration"]
                    running_duration_delta = datetime.datetime.strptime(
                        running_duration_time_str, GlobalFormats.oee_json_time_format())
                    total_running_duration_delta = total_running_duration_delta + datetime.timedelta(
                        hours=running_duration_delta.hour,
                        minutes=running_duration_delta.minute,
                        seconds=running_duration_delta.second)
                total_running_duration_str = str(total_running_duration_delta)
                total_running_duration_formatted_str = DurationCalculatorFormatted1(
                    durationStr=total_running_duration_str)
                # Running duration end

                production_planned_time = float(duration)
                total_unplanned_downtime = float(
                    un_planned_down_duration_delta.total_seconds())
                machine_utilized_time: float = production_planned_time - total_unplanned_downtime
                availability = AvailabilityCalculation(Machine_Utilized_Time=machine_utilized_time,
                                                       Production_Planned_Time=production_planned_time)

                performance = ProductionCalculation(standard_cycle_time=standard_cycle_time,
                                                    total_produced_components=total_production_count,
                                                    utilised_time_seconds=machine_utilized_time)

                quality = Quality(good_count=good_production_count,
                                  total_count=total_production_count)

                oee = OeeCalculator(
                    avail_percent=availability, perform_percent=performance, quality_percent=quality)

                expected_count: int = int(
                    production_planned_time / standard_cycle_time)
                planned_production_time, planned_production_time_formatted = Duration_Converter_Formatted(
                    production_planned_time)

                data = {
                    "sno": str(index),
                    "date": str(current_date),
                    "shiftCode": str(shift_name),
                    "operatorCode": str(operator_code),
                    "jobCode": str(job_code),
                    "plannedProductionTime": str(duration).replace(":", "."),
                    "machineutilizeTime": str(total_running_duration_str).replace(":", "."),
                    "plannedProductionTimeFormatted": str(planned_production_time_formatted),
                    "machineutilizeTimeFormatted": total_running_duration_formatted_str,
                    "availabilityRate": str(availability),
                    "performanceRate": str(performance),
                    "qualityRate": str(quality),
                    "oee": str(oee),
                    "expected": str(expected_count),
                    "good": str(good_production_count),
                    "bad": str(bad_production_count),
                    "totalProduction": str(total_production_count),
                }

                production_report_list.append(data)

        # Final Result Object
        return_data = {
            "chartdetails": chart_details,
            "data": production_report_list,
        }

        json_response = json.dumps(return_data, indent=4)
        return HttpResponse(json_response, "application/json")


class GetOeeReport(APIView):
    @staticmethod
    def get(request):
        params = get_args_from_params(request=request)
        from_date = params["from_date"]
        to_date = params["to_date"]
        device_id = params["device_id"]
        device_id = device_id.replace("_", "-")

        heat_chart_details = [
            {
                "from": 0,
                "to": 80,
                "name": "Below 80%",
                "color": "#E18484"
            },
            {
                "from": 81,
                "to": 99,
                "name": "81% to 99%",
                "color": "#F9C464"
            },
            {
                "from": 100,
                "to": 100,
                "name": "100%",
                "color": "#83F769"
            }
        ]

        color_json = [
            {
                "name": "target",
                "color": "#9C97A6",
                "showAxis": False,
                "leftSide": False
            },
            {
                "name": "availability",
                "color": "#00FF00",
                "showAxis": True,
                "leftSide": True
            },
            {
                "name": "performance",
                "color": "#F8425F",
                "showAxis": False,
                "leftSide": False
            },
            {
                "name": "quality",
                "color": "#68C455",
                "showAxis": False,
                "leftSide": False
            },
            {
                "name": "oee",
                "color": "#7D30FA",
                "showAxis": True,
                "leftSide": False
            }
        ]

        production_history_documents = MachineApi.get_production_history(
            from_date=from_date, to_date=to_date, machine_id=device_id)

        ooe_hour_report = Doc().Read_DbLogs(fromDate=from_date, toDate=to_date, machineID=device_id)
        down_time_document = Doc().Read_Multiple_Document(col="DownTimeCode", query={"machineID": device_id})
        quality_document = Doc().Read_Quality_Document(fromDate=from_date, toDate=to_date, machineID=device_id)
        down_time_report = MachineApi.get_down_time_report(from_date=from_date, to_date=to_date, status="Down",
                                                           machine_id=device_id)
        oee_report_list = []
        head_map_list = []
        index = 0
        day_count = (to_date - from_date).days + 1

        for singleDate in (from_date + datetime.timedelta(n) for n in range(day_count)):
            index = index + 1
            current_date = datetime.datetime.strftime(singleDate, GlobalFormats.oee_output_date_time_format())
            current_date_str = datetime.datetime.strftime(singleDate, GlobalFormats.oee_output_date_time_format())

            current_date_production_history = list(filter(lambda x: (
                    datetime.datetime.strftime(x["timeStamp"], GlobalFormats.oee_output_date_time_format()) == current_date),
                                                          production_history_documents))

            production_plan = current_date_production_history

            target_list = list(
                filter(lambda x: (x["Category"] == "TARGET_OEE"), production_plan))
            production_list = list(
                filter(lambda x: (x["Category"] == "PRODUCTION_PLAN_TIME"), production_plan))
            standard_cycle_list = list(
                filter(lambda x: (x["Category"] == "IDEAL_CYCLE_TIME"), production_plan))

            target_percent = 0 if len(target_list) == 0 else float(target_list[0]["InSeconds"])
            production_time = 0 if len(production_list) == 0 else float(production_list[0]["InSeconds"])
            standard_cycle_time = 0 if len(standard_cycle_list) == 0 else float(standard_cycle_list[0]["InSeconds"])

            oee_report_data = oee_report_gen(from_date=from_date,
                                             current_date_str=current_date_str,
                                             quality_document=quality_document,
                                             down_time_report=down_time_report,
                                             down_time_document=down_time_document,
                                             production_time=production_time,
                                             standard_cycle_time=standard_cycle_time,
                                             mode="date", from_time=0, to_time=0)

            data = {
                "sno": str(index),
                "date": str(current_date_str),
                "target": str(target_percent),
                "availability": oee_report_data["availability"],
                "performance": oee_report_data["performance"],
                "quality": oee_report_data["quality"],
                "oee": oee_report_data["oee"]
            }
            oee_report_list.append(data)

            # Heat Map Begins Here
            from_date_time = datetime.datetime(year=singleDate.year, month=singleDate.month, day=singleDate.day,
                                               hour=0, minute=0, second=0)
            to_datetime = datetime.datetime(year=singleDate.year, month=singleDate.month, day=singleDate.day,
                                            hour=23, minute=59, second=59)
            temp_time = from_date_time
            while temp_time < to_datetime:
                old_temp = temp_time
                temp_time = temp_time + datetime.timedelta(hours=1)

                if temp_time > to_datetime:
                    temp_time = to_datetime

                tmp_from_date_time = old_temp

                ''' APQ percentage from History '''
                oee_hour = tmp_from_date_time.hour
                oee_heat_map_data = oee_history_heat_map(date=tmp_from_date_time, hour=oee_hour,
                                                         ooe_hour_report=ooe_hour_report)
                heat_map_time_formatted = tmp_from_date_time.strftime("%I %p")

                # Heat Map Ends Here
                heatmap = {
                    "date": str(singleDate.date()),
                    "time": str(heat_map_time_formatted),
                    "target": str(target_percent),
                    "availability": oee_heat_map_data["availability"],
                    "performance": oee_heat_map_data["performance"],
                    "quality": oee_heat_map_data["quality"],
                    "oee": oee_heat_map_data["oee"]
                }
                head_map_list.append(heatmap)

        return_data = {
            "heatchartdetails": heat_chart_details,
            "chartdetails": color_json,
            "data": oee_report_list,
            "heatmap": head_map_list
        }
        json_response = json.dumps(return_data, indent=4, skipkeys=True)
        return HttpResponse(json_response, "application/json")


class GetDownTimeReport(APIView):
    @staticmethod
    def get(request):

        params = get_args_from_params(request=request)
        from_date = params["from_date"]
        to_date = params["to_date"]
        device_id = params["device_id"]
        device_id = device_id.replace("_", "-")

        # DownTimeDocument = Doc().DB_Read(col="DownTimeCode")
        down_time_document = Doc().Read_Multiple_Document(col="DownTimeCode", query={"machineID": device_id})

        color_json = [
            {
                "name": "Planned DownTime",
                "color": "#7D30FA",
                "showAxis": True,
                "leftSide": False
            },
            {
                "name": "UnPlanned DownTime",
                "color": "#F8425F",
                "showAxis": True,
                "leftSide": False
            }]

        production_history_documents = MachineApi.get_production_history(
            from_date=from_date, to_date=to_date, machine_id=device_id)

        down_time_report = MachineApi.get_down_time_report(
            from_date=from_date, to_date=to_date, status="Down", machine_id=device_id)
        run_time_report = MachineApi.get_down_time_report(
            from_date=from_date, to_date=to_date, status="Running", machine_id=device_id)
        reason_codes = (list(str(x["DownTimeCode"]) for x in down_time_report))
        reason_codes_list = (list(set(reason_codes)))
        index = 0
        down_data_report_list = []
        for obj in reason_codes_list:
            index += 1
            down_id = obj
            down_object = list(
                filter(lambda x: (x["DownTimeCode"] == down_id), down_time_report))
            down_name = down_object[0]["Description"]

            category_list = list(
                filter(lambda x: (x["DownCode"] == down_id), down_time_document))
            category = "UnPlanned DownTime" if len(
                category_list) == 0 else category_list[0]["Category"]
            percentage = "80"

            down_time_calculated = down_time_duration_calculation_with_formatted(down_object, "Duration")
            total_duration_str = down_time_calculated["duration"]
            total_duration_formatted_str = down_time_calculated["durationFormatted"]

            down_id = "0" if down_id == "" else down_id
            data = {
                "sno": int(index),
                "downId": down_id,
                "downName": down_name,
                "downDescription": down_name,
                "category": category,
                "totalDownTimeFormatted": total_duration_formatted_str,
                "totalDownTime": total_duration_str.replace(":", "."),
                "percentage": percentage
            }
            down_data_report_list.append(data)

        down_dates = (list(
            datetime.datetime.strftime(x["StartTime"], GlobalFormats.oee_output_date_time_format()) for x in down_time_report))

        down_dates_list = (list(set(down_dates)))
        index = 0
        date_wise_report_list = []
        for obj in down_dates_list:
            index += 1
            down_date_str = obj
            current_date_time_tz = datetime.datetime.strptime(
                down_date_str, GlobalFormats.oee_output_date_time_format()).replace(tzinfo=None)

            # total down duration begin
            total_down_object = list(filter(lambda x: (
                    datetime.datetime.strftime(x["StartTime"], GlobalFormats.oee_output_date_time_format()) == down_date_str),
                                            down_time_report))

            down_time_calculated = down_time_duration_calculation_with_formatted(total_down_object, "Duration")
            total_down_duration_str = down_time_calculated["duration"]
            total_duration_formatted_str = down_time_calculated["durationFormatted"]
            # total down duration end

            # planned down duration begin
            temp_planned_down_object = list(filter(lambda x: (
                    datetime.datetime.strftime(x["StartTime"], GlobalFormats.oee_output_date_time_format()) == down_date_str and
                    x["DownTimeCode"] != ""), down_time_report))

            planned_down_object = []
            for plannedObj in temp_planned_down_object:
                category_list = list(filter(lambda x: (
                        x["DownCode"] == plannedObj["DownTimeCode"]), down_time_document))
                if len(category_list) > 0:
                    if category_list[0]["Category"] == "Planned DownTime":
                        planned_down_object.append(plannedObj)

            planned_down_time_calculated = down_time_duration_calculation_with_formatted(
                planned_down_object, "Duration")
            planned_down_duration_str = planned_down_time_calculated["duration"]
            planned_duration_formatted_str = planned_down_time_calculated["durationFormatted"]
            # planned down duration end

            # Unplanned down duration begin
            un_planned_down_object = list(filter(lambda x: (
                    datetime.datetime.strftime(x["StartTime"], GlobalFormats.oee_output_date_time_format()) == down_date_str and
                    x["DownTimeCode"] == ""), down_time_report))

            temp_planned_down_object = list(filter(lambda x: (
                    datetime.datetime.strftime(x["StartTime"], GlobalFormats.oee_output_date_time_format()) == down_date_str and
                    x["DownTimeCode"] != ""), down_time_report))

            for plannedObj in temp_planned_down_object:
                category_list = list(filter(lambda x: (
                        x["DownCode"] == plannedObj["DownTimeCode"]), down_time_document))
                if len(category_list) > 0:
                    if category_list[0]["Category"] == "UnPlanned DownTime":
                        un_planned_down_object.append(plannedObj)

            un_planned_down_time_cal = down_time_duration_calculation_with_formatted(un_planned_down_object, "Duration")
            un_planned_down_duration_delta = un_planned_down_time_cal["durationDelta"]
            un_planned_down_duration_str = un_planned_down_time_cal["duration"]
            un_planned_duration_formatted_str = un_planned_down_time_cal["durationFormatted"]

            # Unplanned down duration end

            # Running duration begin
            running_object = list(filter(lambda x: (
                    datetime.datetime.strftime(x["StartTime"], GlobalFormats.oee_output_date_time_format()) == down_date_str),
                                         run_time_report))

            running_calculated = down_time_duration_calculation_with_formatted(running_object, "Duration")
            total_running_duration_str = running_calculated["duration"]
            total_running_duration_formatted_str = running_calculated["durationFormatted"]
            # Running duration end

            current_date_production_history = list(filter(lambda x: (
                    x["timeStamp"] >= current_date_time_tz >= x["timeStamp"]), production_history_documents))
            production_plan = current_date_production_history
            production_list = list(
                filter(lambda x: (x["Category"] == "PRODUCTION_PLAN_TIME"), production_plan))

            production_time = 0 if len(production_list) == 0 else float(production_list[0]["InSeconds"])

            production_planned_time = float(production_time)
            total_unplanned_downtime = float(un_planned_down_duration_delta.total_seconds())
            machine_utilized_time: float = production_planned_time - total_unplanned_downtime
            availability = AvailabilityCalculation(Machine_Utilized_Time=machine_utilized_time,
                                                   Production_Planned_Time=production_planned_time)
            availability_absolute = abs(availability)
            availability_str = "100" if availability_absolute > 100 else str(availability_absolute)

            date_wise_data = {
                "sno": index,
                "date": down_date_str,
                "machineRunningFormatted": total_running_duration_formatted_str,
                "machineRunning": total_running_duration_str.replace(':', '.'),
                "plannedDownTimeFormatted": planned_duration_formatted_str,
                "plannedDownTime": planned_down_duration_str.replace(":", "."),
                "unPlannedDownTimeFormatted": un_planned_duration_formatted_str,
                "unPlannedDownTime": un_planned_down_duration_str.replace(":", "."),
                "totalDownTimeFormatted": total_duration_formatted_str,
                "totalDownTime": total_down_duration_str.replace(":", "."),
                "availability": str(availability_str)
            }
            date_wise_report_list.append(date_wise_data)

        # Final Result Object
        return_data = {
            "chartdetails": color_json,
            "data": down_data_report_list,
            "datewise": date_wise_report_list
        }

        json_response = json.dumps(return_data, indent=4)
        return HttpResponse(json_response, "application/json")


def down_time_duration_calculation_with_formatted(calculation_object, field):
    total_down_duration_delta = datetime.timedelta()
    for durationTime in calculation_object:
        total_duration_time_str = durationTime[field]
        total_duration_delta = datetime.datetime.strptime(
            total_duration_time_str, GlobalFormats.oee_json_time_format())
        total_down_duration_delta = total_down_duration_delta + datetime.timedelta(hours=total_duration_delta.hour,
                                                                                   minutes=total_duration_delta.minute,
                                                                                   seconds=total_duration_delta.second)
    total_duration_obj = get_duration(
        duration=int(total_down_duration_delta.total_seconds()), formats="hm", separator=" ")
    total_duration_formatted_str = total_duration_obj["formatted"]
    total_down_duration_str = total_duration_obj["raw"]
    # totalDurationFormattedStr = DurationCalculatorFormatted1(durationStr=totalDownDurationStr)
    output = {
        'durationDelta': total_down_duration_delta,
        'duration': total_down_duration_str,
        'durationFormatted': total_duration_formatted_str
    }
    return output


def oee_history_heat_map(date, hour, ooe_hour_report):
    # from_time_formatted = datetime.datetime(year=from_time.year, month=from_time.month, day=from_time.day,
    #                                         hour=from_time.hour, minute=from_time.minute, second=from_time.second,
    #                                         tzinfo=datetime.timezone.utc)
    from_date_str = datetime.datetime.strftime(date, GlobalFormats.oee_json_date_format())
    db_log = list(filter(lambda x: (
            datetime.datetime.strftime(x["datewithhour"]["date"], GlobalFormats.oee_json_date_format()) == from_date_str and
            x["datewithhour"]["hour"] == hour), ooe_hour_report))

    if len(db_log) == 0:
        data = {
            "date": str(from_date_str),
            "availability": str("0"),
            "performance": str("0"),
            "quality": str("0"),
            "oee": str("0")
        }

    else:
        oee_obj = db_log[0]["oee"]
        availability = str(oee_obj["availability"]).replace("%", "").strip()
        performance = str(oee_obj["performance"]).replace("%", "").strip()
        quality = str(oee_obj["quality"]).replace("%", "").strip()
        oee = str(oee_obj["oee"]).replace("%", "").strip()
        data = {
            "date": str(from_date_str),
            "availability": availability,
            "performance": performance,
            "quality": quality,
            "oee": oee
        }
    return data


def oee_report_gen(from_date, current_date_str, quality_document, down_time_report, down_time_document,
                   production_time, standard_cycle_time, mode, from_time, to_time):
    total_production_count = 0
    good_production_count = 0

    today_production_list = list(
        filter(lambda x: (x["date"] == current_date_str), quality_document))
    for production in today_production_list:
        if production["category"] == "good":
            good_production_count = good_production_count + int(production["productioncount"])
        total_production_count = total_production_count + int(production["productioncount"])

    # Unplanned down duration begin
    if mode == "date":
        un_planned_down_object = list(filter(lambda x: (
                datetime.datetime.strftime(x["StartTime"], GlobalFormats.oee_output_date_time_format()) == from_date and
                x["DownTimeCode"] == ""), down_time_report))

        planned_down_object = list(filter(lambda x: (
                datetime.datetime.strftime(x["StartTime"], GlobalFormats.oee_output_date_time_format()) == from_date and
                x["DownTimeCode"] != ""), down_time_report))

    else:
        un_planned_down_object = list(filter(lambda x: (x["StartTime"] >= from_time and
                                                        x["StopTime"] <= to_time and
                                                        x["DownTimeCode"] == ""), down_time_report))

        planned_down_object = list(filter(lambda x: (x["StartTime"] >= from_time and
                                                     x["StopTime"] <= to_time and
                                                     x["DownTimeCode"] != ""), down_time_report))

    for planned_obj in planned_down_object:
        category_list = list(filter(lambda x: (
                x["DownCode"] == planned_obj["DownTimeCode"]), down_time_document))
        if len(category_list) > 0:
            if category_list[0]["Category"] == "UnPlanned DownTime":
                un_planned_down_object.append(planned_obj)

    un_planned_down_duration_delta = datetime.timedelta()
    for durationTime in un_planned_down_object:
        un_planned_duration_time_str = durationTime["Duration"]
        un_planned_duration_delta = datetime.datetime.strptime(
            un_planned_duration_time_str, GlobalFormats.oee_json_time_format())
        un_planned_down_duration_delta = un_planned_down_duration_delta + datetime.timedelta(
            hours=un_planned_duration_delta.hour,
            minutes=un_planned_duration_delta.minute,
            seconds=un_planned_duration_delta.second)
    # Unplanned down duration end

    production_planned_time = float(production_time)
    total_unplanned_downtime = float(
        un_planned_down_duration_delta.total_seconds())
    machine_utilized_time: float = production_planned_time - total_unplanned_downtime
    availability = AvailabilityCalculation(Machine_Utilized_Time=machine_utilized_time,
                                           Production_Planned_Time=production_planned_time)

    performance = ProductionCalculation(standard_cycle_time=standard_cycle_time,
                                        total_produced_components=total_production_count,
                                        utilised_time_seconds=machine_utilized_time)

    quality = Quality(good_count=good_production_count,
                      total_count=total_production_count)

    oee = OeeCalculator(avail_percent=availability,
                        perform_percent=performance, quality_percent=quality)

    data = {
        "date": str(current_date_str),
        "availability": str(availability),
        "performance": str(performance),
        "quality": str(quality),
        "oee": str(oee)
    }
    return data


def get_args_from_params(request):
    request_params = {k: v[0] for k, v in dict(request.GET).items()}
    param_from_date = request_params["fromDate"]
    param_to_date = request_params["toDate"]
    mode = request_params["mode"] if "mode" in request_params else ""
    params_device_id = request_params["deviceID"] if "deviceID" in request_params else ""
    device_id = params_device_id if mode == "web" else get_device_id()
    from_date = datetime.datetime.strptime(param_from_date, GlobalFormats.oee_mongo_db_date_time_format())
    to_date = datetime.datetime.strptime(param_to_date, GlobalFormats.oee_mongo_db_date_time_format())

    params = {
        "from_date": from_date,
        "to_date": to_date,
        "device_id": device_id
    }
    return params
