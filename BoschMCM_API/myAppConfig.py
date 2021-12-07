from django.apps import AppConfig
from App.CNC_Calculation.ReadFromExcel import OnMyWatch
from Webapp.views import StartOpcService


class MyAppConfig(AppConfig):
    name = "BoschMCM_API"
    started = False

    def ready(self):
        if not self.started:
            self.started = True
            watch = OnMyWatch()
            watch.run()
            StartOpcService.startOPC()
            print("WatchDog Service Started at Origin")
