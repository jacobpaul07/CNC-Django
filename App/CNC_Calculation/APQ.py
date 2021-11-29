import json

from App.CNC_Calculation.MachineStatus import getSeconds_fromTimeDifference
from App.OPCUA.index import readCalculation_file


def Availability(Total_Unplanned_Downtime):

    Path = "./App/JsonDataBase/ProductionPlan.json"
    with open(Path) as f:
        json_string = json.load(f)
    ProductionObject = list(filter(lambda x: (x["Category"] == "PRODUCTION_PLAN_TIME"), json_string))
    if len(ProductionObject) == 0:
        availability_result = 0
        Machine_Utilized_Time = 0
    else:
        Production_Planned_Time: float = float(ProductionObject[0]["InSeconds"])
        Machine_Utilized_Time: float = Production_Planned_Time - Total_Unplanned_Downtime
        availability_result = AvailabilityCalculation(Machine_Utilized_Time=Machine_Utilized_Time,
                                                      Production_Planned_Time=Production_Planned_Time)
    return abs(availability_result), Machine_Utilized_Time


def AvailabilityCalculation(Machine_Utilized_Time, Production_Planned_Time):
    if Production_Planned_Time == 0:
        return 0

    else:
        availability = Machine_Utilized_Time / Production_Planned_Time
        availability_result = round(availability * 100, 2)
        return availability_result


def Productivity(Standard_Cycle_Time, Total_Produced_Components, Machine_Utilized_Time):
    if Machine_Utilized_Time == 0:
        return 0

    else:
        Path = "./App/JsonDataBase/ProductionPlan.json"
        with open(Path) as f:
            json_string = json.load(f)
        IdealCycleObject = list(filter(lambda x: (x["Category"] == "IDEAL_CYCLE_TIME"), json_string))
        Standard_Cycle_Time = float(IdealCycleObject[0]["InSeconds"])
        Calculation_Data = readCalculation_file()
        Planned_Down_time = getSeconds_fromTimeDifference(
            Calculation_Data["Down"]["category"]["Planned"]["ActiveHours"])
        Machine_Utilized_Time = Machine_Utilized_Time - Planned_Down_time
        UtilisedTime_Minutes = int(Machine_Utilized_Time/60)
        UtilisedTime_Seconds = int(UtilisedTime_Minutes*60)
        productivity_result = ProductionCalculation(Standard_Cycle_Time, Total_Produced_Components, UtilisedTime_Seconds)
        return abs(productivity_result)


def ProductionCalculation(Standard_Cycle_Time, Total_Produced_Components, UtilisedTime_Seconds):
    if UtilisedTime_Seconds ==0:
        return 0
    else:
        productivity = (Standard_Cycle_Time * Total_Produced_Components) / UtilisedTime_Seconds
        productivity_result = round(productivity * 100, 2)
        return productivity_result


def Quality(goodCount, totalCount):
    if totalCount == 0:
        return 0
    else:
        qualityProduct = round((goodCount/totalCount)*100, 2)
        return abs(qualityProduct)


def OeeCalculator(AvailPercent, PerformPercent, QualityPercent):

    AvailablePercentage = AvailPercent / 100
    PerformancePercentage = PerformPercent / 100
    QualityPercentage = QualityPercent / 100
    OeePercentage: float = round((AvailablePercentage * PerformancePercentage * QualityPercentage * 100), 2)
    return OeePercentage

