import os
import sys
import threading
import dateutil.parser
from MongoDB_Main import Document as Doc


def DbLogsCreatorThread(loadValue):
    try:
        loadValue["Timestamp"] = dateutil.parser.parse(loadValue["Timestamp"])
        logsBackupCollectionName = "Logs"
        threadLogsBackup = threading.Thread(
            target=Doc().DB_Write,
            args=(loadValue, logsBackupCollectionName)
        )
        threadLogsBackup.start()
    except Exception as ex:
        print("Error in DbLogsCreatorThread-LogsCreator.py", ex)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, file_name, exc_tb.tb_lineno)


