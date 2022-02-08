import json
import time
from confluent_kafka import Producer

if __name__ == '__main__':
    config = {'bootstrap.servers': "192.168.201.120:9092"}
    # Create Producer instance
    producer = Producer(config)

    # Optional per-message delivery callback (triggered by poll() or flush())
    # when a message has been successfully delivered or permanently failed delivery (after retries).

    def delivery_callback(err, msg):
        if err:
            print('ERROR: Message failed delivery: {}'.format(err))


    output = {
        "machineID": "MID-01",
        "jobID": "JID-01",
        "operatorID": "OID-02",
        "shiftID": "SID-01",
        "running": {
            "activeHours": "00h 43m 23s",
            "data": [
                {
                    "name": "Running",
                    "value": 100.0,
                    "color": "#68C455",
                    "description": "Total 00h 43m 23s Hrs running"
                }
            ]
        },
        "downtime": {
            "activeHours": "00h 00m 00s",
            "data": [
                {
                    "name": "Down Time",
                    "value": 100.0,
                    "color": "#F8425F",
                    "description": "Total 0 mins unplanned time"
                }
            ]
        },
        "totalProduced": {
            "total": "32",
            "expected": "1305",
            "data": [
                {
                    "name": "Bad",
                    "value": 100.0,
                    "color": "#F8425F",
                    "description": "32"
                }
            ]
        },
        "oee": {
            "scheduled": {
                "runTime": "1305 minutes",
                "expectedCount": "1305",
                "productionRate": "1/ minute"
            },
            "fullfiled": {
                "currentRunTime": "43 minutes",
                "totalProduced": "32",
                "good": "0",
                "bad": "32"
            },
            "availability": "100.0 %",
            "performance": "74.42 %",
            "quality": "0.0 %",
            "targetOee": "75.0 %",
            "oee": "0.0 %"
        },
        "currentProductionGraph": {
            "data": [
                {
                    "name": "Bad",
                    "color": "#FF0000",
                    "showAxis": True,
                    "leftSide": False,
                    "data": [
                        [
                            "2021-12-21T11:30:00",
                            0.0
                        ],
                        [
                            "2021-12-21T12:30:00",
                            33.0
                        ]
                    ],
                    "type": "line"
                },
                {
                    "name": "Total Production",
                    "color": "#68C455",
                    "showAxis": False,
                    "leftSide": False,
                    "data": [
                        [
                            "2021-12-21T11:30:00",
                            0.0
                        ],
                        [
                            "2021-12-21T12:30:00",
                            33.0
                        ]
                    ],
                    "type": "line"
                }
            ]
        },
        "oeeGraph": {
            "data": [
                {
                    "name": "Availability",
                    "color": "#4BC2BE",
                    "showAxis": True,
                    "leftSide": True,
                    "data": [
                        [
                            "2021-12-21T11:30:00",
                            0.0
                        ],
                        [
                            "2021-12-21T12:15:07.572777",
                            75.21
                        ]
                    ],
                    "type": "line"
                },
                {
                    "name": "Performance",
                    "color": "#F8425F",
                    "showAxis": False,
                    "leftSide": False,
                    "data": [
                        [
                            "2021-12-21T11:30:00",
                            0.0
                        ],
                        [
                            "2021-12-21T12:15:07.572777",
                            73.33
                        ]
                    ],
                    "type": "line"
                },
                {
                    "name": "Quality",
                    "color": "#68C455",
                    "showAxis": False,
                    "leftSide": False,
                    "data": [
                        [
                            "2021-12-21T11:30:00",
                            0.0
                        ],
                        [
                            "2021-12-21T12:15:07.572777",
                            0.0
                        ]
                    ],
                    "type": "line"
                },
                {
                    "name": "OEE",
                    "color": "#7D30FA",
                    "showAxis": True,
                    "leftSide": False,
                    "data": [
                        [
                            "2021-12-21T11:30:00",
                            0.0
                        ],
                        [
                            "2021-12-21T12:15:07.572777",
                            0.0
                        ]
                    ],
                    "type": "line"
                }
            ]
        },
        "downtimeGraph": [
            {
                "name": "Running",
                "color": "#C8F3BF",
                "data": [
                    {
                        "x": "down",
                        "y": [
                            "2021-12-09T18:03:30.580000",
                            "2021-12-21T12:15:07.572777"
                        ],
                        "description": "18 hrs 11 mins 36 seconds running"
                    }
                ]
            }
        ]
    }

    while True:
        output_Str = json.dumps(output, indent=4)
        # Produce data by selecting random values from these lists.
        producer.produce(topic="LiveData", value=output_Str, callback=delivery_callback)
        # Block until the messages are sent.
        producer.poll(10000)
        producer.flush()
        time.sleep(5)
