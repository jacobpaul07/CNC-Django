def init():
    global startOPCUAService
    startOPCUAService = False

    global runWebSocket
    runWebSocket = False

    global OEE_JsonDateTimeFormat
    OEE_JsonDateTimeFormat = "%Y-%m-%d %H:%M:%S.%f"

    global OEE_JsonTimeFormat
    OEE_JsonTimeFormat = "%H:%M:%S.%f"

    global OEE_JsonDateFormat
    OEE_JsonDateFormat = "%Y-%m-%d"

    global OEE_OutputTimeFormat
    OEE_OutputTimeFormat = "%H:%M:%S"

    global OEE_OutputDateTimeFormat
    OEE_OutputDateTimeFormat = "%Y-%m-%d"

    global OEE_MongoDBDateTimeFormat
    OEE_MongoDBDateTimeFormat = "%Y-%m-%dT%H:%M:%S%z"

