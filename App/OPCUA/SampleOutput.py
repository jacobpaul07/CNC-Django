import json
from typing import List
from App.OPCUA.JsonClass import LiveData, Downtime
from App.CNC_Calculation.DowntimeDatum import DowntimeDatum


def SampleOutput(result, availability, performance, quality, targetOee, oee):
    Data = {
        "topic": "test",
        "partition": 0,
        "offset": 221,
        "timestamp": {"$numberLong": "1634567314354"},
        "timestamp_type": 0,
        "key": "null",
        "value": [
            {"DisplayName": "CycleStart_Status", "value": "True", "timestamp": "2021-10-18T02:28:34_PM"},
            {"DisplayName": "DownTime_ReasonCode", "value": 10, "timestamp": "2021-10-18T02:28:34_PM"},
            {"DisplayName": "DownTime_Status", "value": "True", "timestamp": "2021-10-18T02:28:34_PM"},
            {"DisplayName": "EmgStop_Status", "value": "True", "timestamp": "2021-10-18T02:28:34_PM"},
            {"DisplayName": "IdealCycleTime", "value": 180, "timestamp": "2021-10-18T02:28:34_PM"},
            {"DisplayName": "JobID", "value": 500, "timestamp": "2021-10-18T02:28:34_PM"},
            {"DisplayName": "MachineID", "value": 1002, "timestamp": "2021-10-18T02:28:34_PM"},
            {"DisplayName": "OperatorID", "value": 1001, "timestamp": "2021-10-18T02:28:34_PM"},
            {"DisplayName": "PowerOn_Status", "value": "False", "timestamp": "2021-10-18T02:28:34_PM"},
            {"DisplayName": "ProductionStart", "value": "False", "timestamp": "2021-10-18T02:28:34_PM"},
            {"DisplayName": "QualityCode", "value": 1005, "timestamp": "2021-10-18T02:28:34_PM"},
            {"DisplayName": "ShiftID", "value": 1, "timestamp": "2021-10-18T02:28:34_PM"}
        ],
        "headers": [],
        "checksum": {"$numberLong": "3052508005"},
        "serialized_key_size": -1, "serialized_value_size": 1055,
        "serialized_header_size": -1,
        "dateTime": "2021-10-18T14:28:34.402+00:00"
    }

    HEADERS = ["CycleStart_Status", "DownTime_ReasonCode", "DownTime_Status", "EmgStop_Status", "IdealCycleTime",
               "JobID", "MachineID", "OperatorID", "PowerOn_Status", "ProductionStart", "QualityCode", "ShiftID"]
    # Result dictionary
    result = {}
    for index, header in enumerate(HEADERS):
        result[header] = Data["value"][index]["value"]
    print(result)

    LiveData.machine_id = "MID-01"
    LiveData.job_id = "JB-01"
    LiveData.operator_id = "OID-01"
    LiveData.shift_id = "SID-01"

    machineRunningData = [
        {"name": "running", "value": 70, "color": "#348f07", "description": "total 7 Hrs running"},
        {"name": "planned", "value": 20, "color": "#1d0aa8", "description": "total 2 Hrs planned down"},
        {"name": "unplanning", "value": 10, "color": "#e80505", "description": "total 2 Hrs planned down"}
    ]

    machineDownData = [
        {"name": "Lunch", "value": 33, "color": "#7D30FA", "description": "total 30 mins Lunch"},
        {"name": "Tea Break", "value": 33, "color": "#F8425F", "description": "total 30 mins Tea break"},
        {"name": "Mechanical Breakdown", "value": 33, "color": "#F8B53A",
         "description": "Total 30 mins mechanical down time"}
    ]

    machineProducedData = [
        {"name": "Good", "value": 70, "color": "#7D30FA", "description": "7000 tons"},
        {"name": "Bad", "value": 30, "color": "#F8425F", "description": "3000 tons"}
    ]

    currentProduction = {
        "data": [
            {
                "name": "Quality Product",
                "color": "#00FF00",
                "type": 'line',
                "showAxis": True,
                "leftSide": True,
                "data": [50, 100, 150, 200, 250, 300, 350, 460]
            },
            {
                "name": "Waster Product",
                "color": "#0000FF",
                "type": 'line',
                "showAxis": False,
                "leftSide": False,
                "data": [10, 29, 37, 36, 44, 45, 50, 58]
            },
            {
                "name": "Bad Product",
                "color": "#FF0000",
                "type": 'line',
                "showAxis": True,
                "leftSide": False,
                "data": [50, 29, 37, 36, 44, 45, 50, 58]
            }
        ],
        "categories": [1, 2, 3, 4, 5, 6, 7, 8]

    }

    oeeProduction = {
        "data": [
            {
                "name": "Availability",
                "color": "#87CEEB",
                "showAxis": True,
                "leftSide": True,
                "data": [1.4, 2, 2.5, 1.5, 2.5, 2.8, 3.8, 4.6]
            },
            {
                "name": "Performance",
                "color": "#FF0000",
                "showAxis": False,
                "leftSide": False,
                "data": [20, 29, 37, 36, 44, 45, 50, 58]
            },
            {
                "name": "Quality",
                "color": "#00FF00",
                "showAxis": False,
                "leftSide": False,
                "data": [20, 29, 37, 36, 44, 45, 50, 58]
            },
            {
                "name": "OEE %",
                "color": "#0000FF",
                "showAxis": True,
                "leftSide": False,
                "data": [20, 29, 37, 36, 44, 45, 50, 58]
            }
        ],
        "categories": [1, 2, 3, 4, 5, 6, 7, 8]

    }

    downTimeProduction = [
        {
            "name": 'Running',
            "color": "#00FF00",
            "data": [
                {
                    "x": 'down',
                    "y": [6, 7],
                    "description": "1hr Machine Running"
                },
                {
                    "x": 'down',
                    "y": [8, 10],
                    "description": "2hr Machine Running"
                },
                {
                    "x": 'down',
                    "y": [12, 16],
                    "description": "4hr Machine Running"
                },
            ]
        },
        {
            "name": 'Planned',
            "color": "#FFFF00",
            "data": [
                {
                    "x": 'down',
                    "y": [7, 7.10],
                    "description": "10 mins Tea Break"
                },
                {
                    "x": 'down',
                    "y": [9, 9.30],
                    "description": "30 mins Breakfast"
                },

            ]
        },
        {
            "name": 'UnPlanned',
            "color": "#FF0000",
            "data": [
                {
                    "x": 'down',
                    "y": [12, 12.30],
                    "description": "30 mins down for undefined reason"
                },

            ]
        },

    ]

    defaultLiveData = {
        "machineID": result["MachineID"],
        "jobID": result["JobID"],
        "operatorID": result["OperatorID"],
        "shiftID": result["ShiftID"],
        "running": {
            "activeHours": "3h 45m 20s",
            "data": machineRunningData
        },
        "downtime": {
            "activeHours": "6h 30m 10s",
            "data": machineDownData
        },
        "totalProduced": {
            "total": " 675",
            "data": machineProducedData
        },
        "oee": {
            "scheduled": {
                "runTime": "675.00 minutes",
                "expectedCount": "13500 Quality tons",
                "productionRate": "20 tons/minutes"
            },
            "fullfiled": {
                "currentRunTime": "269 minutes",
                "totalProduced": "4940.00 tons",
                "good": "4915.30",
                "bad": "24.70 "

            },
            "availability": str(availability),
            "performance": str(performance),
            "quality": str(quality),
            "targetOee": str(targetOee),
            "oee": str(oee)
        },
        "currentProductionGraph": currentProduction,
        "oeeGraph": oeeProduction,
        "downtimeGraph": downTimeProduction

    }

    return defaultLiveData


# machine_id = "MID-01"
# job_id = "JB-01"
# operator_id = "OID-01"
# shift_id = "SID-01"
#
# machineRunningData = [
#     {"name": "running", "value": "70", "color": "#348f07", "description": "total 7 Hrs running"},
#     {"name": "planned", "value": "20", "color": "#1d0aa8", "description": "total 2 Hrs planned down"},
#     {"name": "unplanning", "value": "10", "color": "#e80505", "description": "total 2 Hrs planned down"}
# ]
# activehours = "3h"
# running: Downtime = Downtime(activehours)
#
# newData = LiveData(machine_id,job_id,operator_id, shift_id, running)
#
# val1 = {"name": "running", "value": "70", "color": "#348f07", "description": "total 7 Hrs running"}
# Running = newData.running
#
# print(Running)
