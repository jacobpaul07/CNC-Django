# Author - GopalaSutharsan
# First Commit - 22/10/2021
# Latest Change - 23/10/2021

import datetime
import threading
from MongoDB_Main import Document as Doc

col = "Availability"


def dataValidation(data):
    currenttime = datetime.datetime.now()
    previouspowerdata = ""
    previouspowerONOFFdata = ""

    if data["PowerOn_Status"] == "True":
        startData = Doc().ReadDBQuery(col=col, query={"Status": "Down", "Cycle": "Open"})
        stopData = Doc().ReadDBQuery(col=col, query={"Status": "Running", "Cycle": "Open"})

        for previouspowerdata in startData:
            print(previouspowerdata)
        for previouspowerONOFFdata in stopData:
            print(previouspowerONOFFdata)

        # If PreviousPowerDown is not there and PreviousPowerON is not there then do an INSERT
        if previouspowerdata == "" and previouspowerONOFFdata == "":
            print("No Data exists")
            starttime_temp = currenttime
            startpowerstatusjson = {"MID": "MD-01", "PowerOnStatus": "ON", "StartTime": starttime_temp,
                                    "StopTime": "", "Duration": "", "Status": "Running", "Cycle": "Open",
                                    "DownTimeCode": "", "Description": "", "Category": ""}
            Doc().DB_Write(col=col, data=startpowerstatusjson)

        else:
            print("data exists")
            endtime_temp = currenttime
            temp_starttime = previouspowerdata['StartTime']
            object_id = previouspowerdata['_id']
            duration_temp = endtime_temp - temp_starttime
            duration_temp_str = str(duration_temp)
            print(duration_temp_str)

            updateQuery = ({"_id": object_id}, {"$set": {"StopTime": endtime_temp, "Duration": duration_temp_str,
                                                         "Cycle": "Closed"}})

            Doc().UpateDBQuery(col, updateQuery)

            startpowerstatusjson = {"MID": "MD-01", "PowerOnStatus": "ON", "StartTime": endtime_temp,
                                    "StopTime": "", "Duration": "", "Status": "Running", "Cycle": "Open",
                                    "DownTimeCode": "", "Description": "", "Category": ""}
            Doc().DB_Write(col, startpowerstatusjson)


    elif data["PowerOn_Status"] == "False":
        endtime_temp = currenttime
        stopData = Doc().ReadDBQuery(col=col, query={"Status": "Down", "Cycle": "Open"})
        startData = Doc().ReadDBQuery(col=col, query={"Status": "Running", "Cycle": "Open"})
        for previouspowerdata in startData:
            print(previouspowerdata)

        for previouspowerONOFFdata in stopData:
            print(previouspowerONOFFdata)

        if previouspowerdata == "" and previouspowerONOFFdata == "":
            print("No data exists")

            stoppowerstatusjson = {"MID": "MD-01", "PowerOnStatus": "OFF", "StartTime": endtime_temp,
                                   "StopTime": "", "Duration": "", "Status": "Down", "Cycle": "Open",
                                   "DownTimeCode": "", "Description": "", "Category": ""}
            Doc().DB_Write(col, stoppowerstatusjson)

        else:
            temp_starttime = previouspowerdata['StartTime']
            object_id = previouspowerdata['_id']
            duration_temp = endtime_temp - temp_starttime
            duration_temp_str = str(duration_temp)
            print(duration_temp_str)

            updateQuery = ({"_id": object_id}, {"$set": {"StopTime": endtime_temp, "Duration": duration_temp_str,
                                                         "Cycle": "Closed"}})
            Doc().UpateDBQuery(col, updateQuery)

            stoppowerstatusjson = {"MID": "MD-01", "PowerOnStatus": "OFF", "StartTime": endtime_temp,
                                   "StopTime": "", "Duration": "", "Status": "Down", "Cycle": "Open",
                                   "DownTimeCode": "", "Description": "", "Category": ""}
            Doc().DB_Write(col, stoppowerstatusjson)


def updatedowntimereasoncode():
    global object_id
    updateQuery = ({"_id": object_id}, {"$set": {"DownTimeCode": "", "Description": "", "Category": ""}})
    Doc().UpateDBQuery(col, updateQuery)


def productivity():
    threading.Timer(10, productivity).start()
    global goodcount, badcount, totalcount

    qualitycode = client.get_node("ns=3;i=2000")
    qualitycode_var = qualitycode.get_value()
    print("Quality Code:%s" % qualitycode_var)

    if qualitycode_var == 1:
        goodcount += 1
    elif qualitycode_var == 0:
        badcount += 1

    totalcount = goodcount + badcount
    print("Good Count:%s,Bad Count:%s,Total Count:%s" % (goodcount, badcount, totalcount))

    productivityprct = (totalcount / expectedproduction) * 100
    print(productivityprct)

    return productivityprct


# 180 Secs (3 Mins) IdealCycTime
# 100 TotalProdComponents G + B
# 21,600 Secs (6 Hours or 3600 Mins) For now Hardcode, will get from Jacob
# Because there is no expectedproduction, this below formula will be used
def actualproductivity():
    threading.Timer(10, actualproductivity).start()
    actualprod = (idealcycletime * totalcount) / machineutilizedtime
    print(actualprod)


opcuaclient()
