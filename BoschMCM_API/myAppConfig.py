import os
import threading
import time
from django.apps import AppConfig
from Webapp.views import StartOpcService
from App.GeneralUtils.index import get_device_id
from App.CNC_Calculation.ReadFromExcel import OnMyWatch
from Webapp.webDeviceStatusMonitor import web_device_status_monitor


class MyAppConfig(AppConfig):
    name = "BoschMCM_API"
    started = False

    def ready(self):
        if not self.started:
            self.started = True
            # Mobile Mode
            if os.environ['ApplicationMode'] != "web":
                thread = threading.Thread(target=wait_for_machine_id, args=())
                thread.start()
                watch = OnMyWatch()
                watch.run()
                StartOpcService.startOPC()
                print("WatchDog Service Started at Origin")
            # Web Mode
            else:
                print("Cloud Consumer Started at Origin")
                StartOpcService.startKafkaWeb()
                StartOpcService.startConsumeDeviceApiRequest()

                thread = threading.Thread(target=web_device_status_monitor, args=())
                thread.start()


def wait_for_machine_id():
    machine_id = get_device_id()
    while machine_id == "":
        machine_id = get_device_id()
        time.sleep(1)

    if os.environ['ApplicationMode'] != "web":
        StartOpcService.startConsumeWebApiRequest()
