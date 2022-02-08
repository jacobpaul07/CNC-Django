from typing import List
from App.OPCUA.Output import UnplannedDownHour_Data, downTimeGraphData
from App.GeneralUtils.JsonClass import DowntimeGraph, DowntimeDatum, Downtime, LiveData


def GetUpdatedLiveData(orginalData: LiveData,
                       Calculation_Data,
                       currentTime,
                       availabilityJson,
                       reasonCodeList,
                       OutputArgs,
                       recycleHour):

    # DownTime
    machineDownData = UnplannedDownHour_Data(Calculation_Data=Calculation_Data)
    myDownTime: List[DowntimeDatum] = []
    for downObj in machineDownData:
        myDownTime.append(DowntimeDatum.from_dict(downObj))

    downtimeActiveHours = OutputArgs["DownTimeDurationFormatted"]
    downtime: Downtime = Downtime(
        active_hours=downtimeActiveHours, data=myDownTime)

    # Down Time Production
    newDownTimeGraph: List[DowntimeGraph] = downTimeGraphData(currentTime=currentTime,
                                                              availabilityJson=availabilityJson,
                                                              reasonCodeList=reasonCodeList)

    # Final Output
    OutputLiveData: LiveData = LiveData(machine_id=orginalData.machine_id,
                                        job_id=orginalData.job_id,
                                        operator_id=orginalData.operator_id,
                                        shift_id=orginalData.shift_id,
                                        powerOnStatus=orginalData.powerOnStatus,
                                        machineStatus=orginalData.machineStatus,
                                        running=orginalData.running,
                                        downtime=downtime,
                                        total_produced=orginalData.total_produced,
                                        oee=orginalData.oee,
                                        current_production_graph=orginalData.current_production_graph,
                                        oee_graph=orginalData.oee_graph,
                                        RecycleHour=recycleHour,
                                        Timestamp=currentTime,
                                        downtime_graph=newDownTimeGraph)

    dumpedOutput = OutputLiveData.to_dict()
    return dumpedOutput
