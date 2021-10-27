def Availability(Total_time, Planned_Down_time, Total_Unplanned_Downtime):
    Production_Planned_Time: float = Total_time - Planned_Down_time
    Machine_Utilized_Time: float = Production_Planned_Time - Total_Unplanned_Downtime
    if Production_Planned_Time == 0:
        availability_result = 0
    else:
        availability = Machine_Utilized_Time / Production_Planned_Time
        availability_result = round(availability*100, 2)
    print("Availability", availability_result)
    return availability_result, Machine_Utilized_Time


def Productivity(Standard_Cycle_Time, Total_Produced_Components, Machine_Utilized_Time):
    if Machine_Utilized_Time == 0:
        return 0

    else:
        productivity = (Standard_Cycle_Time * Total_Produced_Components)/Machine_Utilized_Time
        productivity_result = round(productivity, 2)
        print("Productivity", productivity_result)
        return productivity_result


def Quality(goodCount, totalCount):
    if totalCount == 0:
        return 0
    else:
        qualityProduct = (goodCount/totalCount)*100
        print("Quality", qualityProduct)
        return qualityProduct
