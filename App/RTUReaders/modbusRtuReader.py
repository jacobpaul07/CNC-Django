import threading
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from App.GeneralUtilities import timestamp
from App.Json_Class.COMProperties_dto import COMPORTProperties
from App.Json_Class.COMDevices_dto import *
from App.Json_Class.SerialPortSetting_dto import SerialPortSettings
from datetime import datetime


def ReadRTUSingleTag(RTUMeasurementTags: object, finalData: []):
    result: object = {}
    # print(RTUMeasurementTags)
    rtuDeviceEnabled: bool = bool(str(RTUMeasurementTags["Enabled"]))
    tagName: str = RTUMeasurementTags["tagName"]
    method: str = RTUMeasurementTags["Method"]
    port: str = RTUMeasurementTags["Port"]
    timeout = int(RTUMeasurementTags["Timeout"])
    stopbits = int(RTUMeasurementTags["Stop Bit"])
    bytesize = int(RTUMeasurementTags["Data Bit"])
    parity = RTUMeasurementTags["Parity"]
    baudrate = int(RTUMeasurementTags["Baud Rate"])

    if rtuDeviceEnabled:
        c = ModbusClient(method=method, port=port, timeout=int(timeout),
                         stopbits=int(stopbits), bytesize=int(bytesize), parity=parity,
                         baudrate=int(baudrate))

        # open or reconnect TCP to server
        if not c.connect():
            print("unable to connect to", port)

        try:
            if c.connect():
                # read 8 registers at address 0, store result in regs list
                for tags in COMdevice.IOTags:
                    register_data = c.read_input_registers(address=int(tags.Address),
                                                           count=1,
                                                           unit=int(COMdevice.properties.UnitNumber))
                    registerValue = register_data.registers
                    result = {
                        "tagName": tagName,
                        "value": round(registerValue, 3)
                    }

            for idx, currentObject in enumerate(finalData):
                if currentObject["tagName"] == tagName:
                    finalData[idx] = result
                    break
        except Exception as exception:
            print("Device is not Connected, Error:", exception)

    return result


def ReadRTU(settings: SerialPortSettings, ComDevices: COMdevice, comProperties: COMPORTProperties, threadsCount,
            callback, com):
    success = True
    datasList = []

    if ComDevices.properties.Enable == "True":
        c = ModbusClient(method=settings.Method, port=settings.Port, timeout=int(settings.Timeout),
                         stopbits=int(settings.StopBit), bytesize=int(settings.DataBit), parity=settings.Parity,
                         baudrate=int(settings.BaudRate))

        # open or reconnect TCP to server
        if not c.connect():
            print("unable to connect to", settings.Port)
        # if open() is ok, read register
        try:
            if c.connect():
                # read 8 registers at address 0, store result in regs list

                for tags in ComDevices.IOTags:
                    register_data = c.read_input_registers(address=int(tags.Address),
                                                           count=1,
                                                           unit=int(ComDevices.properties.UnitNumber))
                    registerValue = register_data.registers
                    timeStamp = datetime.now().strftime("%Y-%m-%dT%I:%M:%S_%p")

                    data = {
                        "deviceID": ComDevices.properties.Name,
                        "channel": com,
                        "tagName": tags.Name,
                        "value": registerValue[0] / 10,
                        "timestamp": timeStamp
                    }

                    datasList.append(data)
                print(ComDevices.properties.Name + str(datasList))
                c.close()
        except Exception as exception:
            success = False
            print("Device is not Connected Error:", exception)

        thread = threading.Thread(
            target=callback,
            args=(settings, ComDevices, comProperties, threadsCount, datasList, success, com)
        )
        thread.start()

    return datasList
