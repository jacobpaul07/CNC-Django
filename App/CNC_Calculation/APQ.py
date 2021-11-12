import json


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
        availability = Machine_Utilized_Time / Production_Planned_Time
        availability_result = round(availability*100, 2)
    return availability_result, Machine_Utilized_Time


def Productivity(Standard_Cycle_Time, Total_Produced_Components, Machine_Utilized_Time):
    if Machine_Utilized_Time == 0:
        return 0

    else:
        productivity = (Standard_Cycle_Time * Total_Produced_Components)/Machine_Utilized_Time
        productivity_result = round(productivity*100, 2)
        return productivity_result


def Quality(goodCount, totalCount):
    if totalCount == 0:
        return 0
    else:
        qualityProduct = round((goodCount/totalCount)*100, 2)
        return qualityProduct


def OeeCalculator(AvailPercent, PerformPercent, QualityPercent):

    AvailablePercentage = AvailPercent / 100
    PerformancePercentage = PerformPercent / 100
    QualityPercentage = QualityPercent / 100
    OeePercentage: float = round((AvailablePercentage * PerformancePercentage * QualityPercentage * 100), 2)
    return OeePercentage

