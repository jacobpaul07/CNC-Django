
def globalSettings():
    global startOPCUAService
    startOPCUAService = False

    global runWebSocket
    runWebSocket = False

    global OEE_JsonDateTimeFormat
    OEE_JsonDateTimeFormat = "%Y-%m-%d %H:%M:%S.%f"

    global OEE_ExcelDateTimeFormat
    OEE_ExcelDateTimeFormat = "%Y-%m-%d %H:%M:%S"

    global OEE_ISOTimeFormat
    OEE_ISOTimeFormat = "%Y-%m-%dT%H:%M:%S.%f"

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

    global OEE_DateHourFormat
    OEE_DateHourFormat = "%Y-%m-%dT%H"

    global new_device_added
    new_device_added = False


class GlobalFormats:

    startOPCUAService = False
    runWebSocket = False
    new_device_added = False

    @staticmethod
    def oee_json_date_time_format():
        oee_json_date_time_format = "%Y-%m-%d %H:%M:%S.%f"
        return oee_json_date_time_format

    @staticmethod
    def oee_excel_date_time_format():
        oee_excel_date_time_format = "%Y-%m-%d %H:%M:%S"
        return oee_excel_date_time_format

    @staticmethod
    def oee_iso_time_format():
        oee_iso_time_format = "%Y-%m-%dT%H:%M:%S.%f"
        return oee_iso_time_format

    @staticmethod
    def oee_json_time_format():
        oee_json_time_format = "%H:%M:%S.%f"
        return oee_json_time_format

    @staticmethod
    def oee_json_date_format():
        oee_json_date_format = "%Y-%m-%d"
        return oee_json_date_format

    @staticmethod
    def oee_output_time_format():
        oee_output_time_format = "%H:%M:%S"
        return oee_output_time_format

    @staticmethod
    def oee_output_date_time_format():
        oee_output_date_time_format = "%Y-%m-%d"
        return oee_output_date_time_format

    @staticmethod
    def oee_mongo_db_date_time_format():
        oee_mongo_db_date_time_format = "%Y-%m-%dT%H:%M:%S%z"
        return oee_mongo_db_date_time_format

    @staticmethod
    def oee_date_hour_format():
        oee_date_hour_format = "%Y-%m-%dT%H"
        return oee_date_hour_format

