from django.apps import AppConfig
from App.CNC_Calculation.ReadFromExcel import OnMyWatch
from Webapp.views import StartOpcService


class MyAppConfig(AppConfig):
    name = "BoschMCM_API"

    def ready(self):
        # StartOpcService.startOPC()
        watch = OnMyWatch()
        watch.run()
        print("WatchDog & OPC Service Started")
