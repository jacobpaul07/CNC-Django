import datetime
import json
import os
import sys
import time
import threading

from App.GeneralUtils.index import readWebDashBoard, write_web_dashboard
from App.globalsettings import GlobalFormats

MAX_IDLE_TIME = 300
MAX_IDLE_DAYS = 7
thread_lock_write = threading.Lock()


def web_device_status_monitor():
    time.sleep(10)
    device_status_verifier()
    thread = threading.Thread(target=web_device_status_monitor, args=())
    thread.start()


def device_status_verifier():
    device_status_list = read_device_status()

    if device_status_list:
        for index, device in enumerate(device_status_list):
            device_id = device["deviceID"]
            device_last_updated = device["lastUpdateTime"]

            time_difference = device_last_update_time_difference(device_last_updated)
            time_difference_seconds = time_difference.total_seconds()

            if time_difference_seconds > MAX_IDLE_TIME:
                device_status_list[index]["runningStatus"] = "False"
                web_dashboard_status_updater(device_id, time_difference)
            else:
                device_status_list[index]["runningStatus"] = "True"

        write_device_status(json_content=device_status_list)


def device_last_update_time_difference(device_last_updated):
    current_time = datetime.datetime.now()
    last_update_time = datetime.datetime.strptime(device_last_updated, GlobalFormats.oee_json_date_time_format())
    time_difference = current_time - last_update_time
    return time_difference


def web_dashboard_status_updater(device_id, time_difference):
    web_dashboard_list = readWebDashBoard()
    machine_data = web_dashboard_list["machineData"]
    time_difference_days = time_difference.days

    for index, machines in enumerate(machine_data):
        if machine_data[index]["machineID"] == device_id:
            if time_difference_days > MAX_IDLE_DAYS:
                del machine_data[index]

            else:
                machine_data[index]["status"] = "Idle"
                machine_data[index]["color"] = "#FF9448"
                machine_data[index]["statusType"] = "UnPlanned Stop"
                machine_data[index]["description"] = "Device Idle"
                # machine_data[index]["machineName"] = deviceID
                # machine_data[index]["location"] = "Floor 2"
                # machine_data[index]["availability"] = oee["availability"]
                # machine_data[index]["performance"] = oee["performance"]
                # machine_data[index]["quality"] = oee["quality"]
                # machine_data[index]["oee"] = oee["oee"]

    web_dashboard_list["machineData"] = machine_data
    write_web_dashboard(web_dashboard_list)


def read_device_status():
    try:
        file_path = './Webapp/JsonWeb/deviceStatusMonitor.json'
        with open(file_path) as f:
            json_string = json.load(f)
            f.close()
        return json_string

    except Exception as ex:
        print("Update Device Status List Error:", ex)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        f_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, f_name, exc_tb.tb_lineno)


def write_device_status(json_content):
    try:
        thread_lock_write.acquire()
        with open('./Webapp/JsonWeb/deviceStatusMonitor.json', "w+") as file:
            json.dump(json_content, file, indent=4)
            file.close()

    except Exception as ex:
        print("Write Device Status File Error: ", ex)

    finally:
        thread_lock_write.release()
