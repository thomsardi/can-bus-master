import threading
import queue
from time import sleep

class CanDataSimulator() :
    def __init__(self) -> None:
        self.arbitration_id : int
        self.dlc : int
        self.data : list[int] = []

class CanBatteryPackSimulatorData() :
    def __init__(self, id : int) -> None:
        self.packVoltageBaseAddr = 0x764c864
        self.packMosfetAddr = 0x763c864
        self.data = []
        self.idList = [
            self.packVoltageBaseAddr - id,
            self.packMosfetAddr - id
        ]
        self.dataList = [
            [0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07],
            [0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F],
            [0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17],
            [0x18, 0x19, 0x1A, 0x1B, 0x1C, 0x1D, 0x1E, 0x1F]
        ]

        for index, id in enumerate(self.idList) :
            dataPair = {
                "id" : self.idList[index],
                "data" : self.dataList[index]
            }
            self.data.append(dataPair)

class DataProvider(threading.Thread) :
    def __init__(self, stopEvent : threading.Event, syncFlag : threading.Condition, buffer : queue.Queue) :
        threading.Thread.__init__(self)
        self.stopEvent : threading.Event = stopEvent
        self.syncFlag = syncFlag
        self.buffer : queue.Queue = buffer
        self.daemon = True
        self.batteryPack : list[CanBatteryPackSimulatorData] = []

        for i in range(0,16,1) :
            sim = CanBatteryPackSimulatorData(i)
            self.batteryPack.append(sim)

    def provide(self) :
        if self.stopEvent.is_set() :
            return
        for batteryPack in self.batteryPack :
            for data in batteryPack.data :
                storage : list = data['data']
                canData = CanDataSimulator()
                canData.arbitration_id = data['id']
                canData.dlc = 8
                canData.data = storage.copy()
                self.buffer.put(canData)
                with self.syncFlag :
                    self.syncFlag.notify_all()
                sleep(0.1)

    def run(self) :
        while not self.stopEvent.is_set() :
            self.provide()