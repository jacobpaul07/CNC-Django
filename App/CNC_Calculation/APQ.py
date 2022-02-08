import os
import sys
from App.CNC_Calculation.MachineStatus import get_seconds_from_time_difference
from App.GeneralUtils.index import readCalculation_file, readProductionPlanFile


def Availability(Total_Unplanned_Downtime):

    production_plan_data = readProductionPlanFile()
    production_object = list(filter(lambda x: (x["Category"] == "PRODUCTION_PLAN_TIME"), production_plan_data))
    if len(production_object) == 0:
        availability_result = 0
        machine_utilized_time = 0
    else:
        production_planned_time: float = float(production_object[0]["InSeconds"])
        machine_utilized_time: float = production_planned_time - Total_Unplanned_Downtime
        availability_result = AvailabilityCalculation(Machine_Utilized_Time=machine_utilized_time,
                                                      Production_Planned_Time=production_planned_time)
    return abs(availability_result), machine_utilized_time


def AvailabilityCalculation(Machine_Utilized_Time, Production_Planned_Time):
    if Production_Planned_Time == 0:
        return 0

    else:
        availability = Machine_Utilized_Time / Production_Planned_Time
        availability_result = round(availability * 100, 2)
        return availability_result


def Productivity(standard_cycle_time, total_produced_components, machine_utilized_time):
    try:
        if machine_utilized_time == 0:
            return 0

        else:
            production_plan_data = readProductionPlanFile()
            ideal_cycle_object = list(filter(lambda x: (x["Category"] == "IDEAL_CYCLE_TIME"), production_plan_data))
            standard_cycle_time = float(ideal_cycle_object[0]["InSeconds"])
            calculation_data = readCalculation_file()
            planned_down_time = get_seconds_from_time_difference(
                calculation_data["Down"]["category"]["Planned"]["ActiveHours"])
            machine_utilized_time = machine_utilized_time - planned_down_time
            utilised_time_minutes = int(machine_utilized_time / 60)
            utilised_time_seconds = int(utilised_time_minutes*60)
            productivity_result = ProductionCalculation(standard_cycle_time, total_produced_components,
                                                        utilised_time_seconds)
            return abs(productivity_result)
    except Exception as exception:
        print("APQ.py - Productivity Error:", exception)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        f_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, f_name, exc_tb.tb_lineno)


def ProductionCalculation(standard_cycle_time, total_produced_components, utilised_time_seconds):
    if utilised_time_seconds == 0:
        return 0
    else:
        productivity = (standard_cycle_time * total_produced_components) / utilised_time_seconds
        productivity_result = round(productivity * 100, 2)
        return productivity_result


def Quality(good_count, total_count):
    if total_count == 0:
        return 0
    else:
        quality_product = round((good_count / total_count) * 100, 2)
        return abs(quality_product)


def OeeCalculator(avail_percent, perform_percent, quality_percent):

    available_percentage = avail_percent / 100
    performance_percentage = perform_percent / 100
    quality_percentage = quality_percent / 100
    oee_percentage: float = round((available_percentage * performance_percentage * quality_percentage * 100), 2)
    return oee_percentage

