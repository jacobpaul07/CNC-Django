import threading
import time
from typing import List
from App.Json_Class.COMPort_dto import Comport
from App.Json_Class.IOTag_dto import IOTag
from App.Json_Class.Stations_dto import Stations
from App.Json_Class.TCPdevice_dto import TCPdevice
from App.Json_Class.index import read_setting
from App.Post_to_Nexeed import Nexeedpost
from App.GeneralUtilities import timestamp
from App.TCPReaders.modbusTcpReader import ReadTCPSingleTag
from App.RTUReaders.modbusRtuReader import ReadRTUSingleTag
import App.globalsettings as appsetting


data = read_setting()


def start_ppmp_post():
    TCP_Measurements = []
    RTU_Measurements = []
    Enable = data.edgedevice.DataService.PPMP.Properties.Enable

    if Enable == "True" or Enable == "true":
        for channel in data.edgedevice.DataService.PPMP.Station:
            if channel.Enable == "True" or channel.Enable == "true":
                for measurement in channel.MeasurementTag:
                    if measurement.DeviceType == "COM1" or measurement.DeviceType == "COM2":
                        newData = read_RTU_Measurements(measurement.to_dict())
                        RTU_Measurements.append(newData)
                    else:
                        newData = read_TCP_Measurements(measurement.to_dict())
                        TCP_Measurements.append(newData)

                thread = threading.Thread(target=read_ppmp_channels,
                                          args=[channel, TCP_Measurements, RTU_Measurements, completed_ppmp_post])
                thread.start()


def completed_ppmp_post(channel: Stations, TCP_Measurements, RTU_Measurements):
    time.sleep(int(channel.UpdateTime))
    if appsetting.startPpmpService:
        thread = threading.Thread(target=read_ppmp_channels,
                                  args=[channel, TCP_Measurements, RTU_Measurements, completed_ppmp_post])
        thread.start()


def read_ppmp_channels(channel: Stations, TCP_Measurements, RTU_Measurements, callback):
    threads: threading = []
    finalData = []
    for tcp_measure in TCP_Measurements:
        newData = {"tagName": tcp_measure["tagName"]}
        finalData.append(newData)

    for rtu_measure in RTU_Measurements:
        newData = {"tagName": rtu_measure["tagName"]}
        finalData.append(newData)

    for tcp_measure in TCP_Measurements:
        thread = threading.Thread(target=ReadTCPSingleTag, args=[tcp_measure, finalData])
        threads.append(thread)
        thread.start()

    for rtu_measure in RTU_Measurements:
        thread = threading.Thread(target=ReadRTUSingleTag, args=[rtu_measure, finalData])
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    # here we goes to final data sent to PPMP
    # print(finalData)

    complete_CallBack_Thread = threading.Thread(target=callback, args=[channel, TCP_Measurements, RTU_Measurements])
    complete_CallBack_Thread.start()

    post_Thread = threading.Thread(target=sent_Data_To_Nexeed, args=[finalData, channel])
    post_Thread.start()


def read_TCP_Measurements(TCPMes):
    deviceName = TCPMes["Device Name"]
    tagName = TCPMes["TagName"]

    device: List[TCPdevice] = [x for x in data.edgedevice.DataCenter.TCP.devices if x.properties.Name == deviceName]

    if len(device) > 0:
        TCPMes["Enabled"] = device[0].properties.Enable
        TCPMes["IP"] = device[0].properties.TCPIP.IPAdress
        TCPMes["PORT"] = device[0].properties.TCPIP.PortNumber
        TCPMes["TimeOutms"] = 1000

        ioTags: List[IOTag] = device[0].IOTags
        tags: List[IOTag] = [y for y in ioTags if y.Name == tagName]

        TCPMes["tagName"] = tags[0].Name
        TCPMes["tagAddress"] = tags[0].Address

    return TCPMes


def read_RTU_Measurements(RTUMes):
    deviceName = RTUMes["Device Name"]
    deviceType = RTUMes["Device-Type"]
    tagName = RTUMes["TagName"]

    port: Comport = data.edgedevice.DataCenter.__getattribute__(deviceType)
    RTUMes["Enabled"] = port.properties.Enable
    RTUMes["Method"] = port.properties.SerialPortSetting.Method
    RTUMes["Port"] = port.properties.SerialPortSetting.Port
    RTUMes["Baud Rate"] = port.properties.SerialPortSetting.BaudRate
    RTUMes["Data Bit"] = port.properties.SerialPortSetting.DataBit
    RTUMes["Stop Bit"] = port.properties.SerialPortSetting.StopBit
    RTUMes["Timeout"] = port.properties.SerialPortSetting.Timeout
    RTUMes["Parity"] = port.properties.SerialPortSetting.Parity
    RTUMes["RTS"] = port.properties.SerialPortSetting.RTS
    RTUMes["DTR"] = port.properties.SerialPortSetting.DTR

    device = [x for x in port.devices if x.properties.Name == deviceName]
    if device:
        tags: List[IOTag] = [x for x in device[0].IOTags if x.Name == tagName]
        RTUMes["tagName"] = tags[0].Name
        RTUMes["tagAddress"] = tags[0].Address

    return RTUMes


def sent_Data_To_Nexeed(finalData, station: Stations):
    # PPMP Format to be sent to API
    url: str = station.API
    updateTime: int = int(station.UpdateTime)

    Nexeed_data = {
        "content-spec": data.edgedevice.DataService.PPMP.Properties.contentspec,
        "device": {
            "id": str(station.StationID)
        },
        "measurements": [{
            "ts": timestamp(),
            "series": {
                "time": [0]
            }
        }]
    }

    for sd in finalData:
        if "value" in sd:
            tagName = sd["tagName"]
            tagValue = [sd["value"]]
            Nexeed_data["measurements"][0]["series"][tagName] = tagValue

    Nexeedpost(Nexeed_data, url, updateTime)
