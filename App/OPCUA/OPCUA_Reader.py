import threading
from datetime import datetime
from opcua import Client

from App.Json_Class.OPCUAParameters import OPCParameters
from App.Json_Class.OPCUAProperties import OPCProperties


def ReadOPCUA(Properties: OPCProperties, OPCTags: OPCParameters, threadsCount, callback):
    success = True
    datasList = []
    if Properties.Enable == "true" or Properties.Enable == "True":
        url: str = Properties.url
        client = Client(url)
        try:
            client.connect()
            # read 8 registers at address 0, store result in regs list
            for tags in OPCTags.MeasurementTag:
                nameSpace = tags.NameSpace
                identifier = tags.Identifier
                DisplayName = tags.DisplayName
                register = client.get_node("ns={0};i={1}".format(nameSpace, identifier))
                registerValue = register.get_value()
                print(registerValue)
                timeStamp = datetime.now().strftime("%Y-%m-%dT%I:%M:%S_%p")

                data = {
                    "DisplayName": DisplayName,
                    "value": registerValue,
                    "timestamp": timeStamp
                }
                datasList.append(data)

            # if success display registers
            if datasList:
                print(str(datasList))
        except Exception as exception:
            success = False
            print("Device is not Connected Error:", exception)

        thread = threading.Thread(
            target=callback,
            args=(Properties, OPCTags, threadsCount, datasList, success)
        )
        thread.start()
    return datasList
