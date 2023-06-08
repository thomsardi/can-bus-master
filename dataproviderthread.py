import threading
import queue
import can
from can import Listener
from time import sleep
from can.message import Message
from multipledispatch import dispatch
from can.broadcastmanager import ModifiableCyclicTaskABC

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
            0x0764c864 - id,
            0x0763c864 - id,
            0x0762c864 - id,
            0x0761c864 - id,
            0x0760c864 - id,
            0x075fc864 - id,
            0x075ec864 - id,
            0x075dc864 - id,
            0x075cc864 - id,
            0x075bc864 - id,
            0x075ac864 - id,
            0x1D40C8E7,
        ]
        self.dataList = [
            [0x56, 0x61, 0x64, 0x65, 0x02, 0x64, 0x01, 0x64],
            [0x31, 0x31, 0x49, 0x49, 0x49, 0x4b, 0x47, 0x45],
            [0x15, 0x56, 0x15, 0x56, 0x15, 0x56, 0x15, 0x56],
            [0x17, 0x56, 0x16, 0x56, 0x15, 0x56, 0x16, 0x56],
            [0x17, 0x56, 0x17, 0x56, 0x16, 0x56, 0x16, 0x56],
            [0x17, 0x56, 0x17, 0x56, 0x64, 0x64, 0x64, 0x5e],
            [0x15, 0x56, 0x17, 0x56, 0x49, 0x4b, 0x42, 0xfc],
            [0x64, 0x63, 0x64, 0x64, 0x64, 0x64, 0x64, 0x64],
            [0x27, 0x5a, 0x64, 0x64, 0xe1, 0x6f, 0x61, 0x64],
            [0x0e, 0x57, 0x64, 0x64, 0xf4, 0x59, 0x64, 0x64],
            [0x52, 0x64, 0x59, 0x5f, 0x5a, 0x29, 0x64, 0x00],
            [1, 7, 25, 15, 30, 20, 40, 25]
        ]

        for index, id in enumerate(self.idList) :
            dataPair = {
                "id" : self.idList[index],
                "data" : self.dataList[index]
            }
            self.data.append(dataPair)

class DataProvider(threading.Thread) :
    def __init__(self, name : str, stopEvent : threading.Event, syncFlag : threading.Condition, buffer : queue.Queue) :
        threading.Thread.__init__(self, name=name)
        self.stopEvent : threading.Event = stopEvent
        self.syncFlag = syncFlag
        self.buffer : queue.Queue = buffer
        self.daemon = True
        self.batteryPack : list[CanBatteryPackSimulatorData] = []
        self.writeQueue = queue.Queue()
        self.override : int = 0
        self.keepAliveId = 0x1D41C8E8
        self.canInterface = "socketcan"
        self.canChannel = "can0"
        self.canBitrate = 250000
        self.bus : can.ThreadSafeBus
        self.periodicTask : ModifiableCyclicTaskABC
        self.canFilter = [
            {"can_id": 0x540C840, "can_mask": 0x5D8FF40, "extended": True}
        ]

        for i in range(1,17,1) :
            sim = CanBatteryPackSimulatorData(i)
            self.batteryPack.append(sim)

    def initBus(self, bus : can.ThreadSafeBus) :
        self.bus = bus

    def setListener(self, listener : list[Listener]) :
        can.Notifier(self.bus, listener)
        # pass

    def link(self, queue : queue.Queue) :
        self.writeQueue = queue

    def insertQueue(self, msg : CanDataSimulator) :
        self.writeQueue.put(msg)

    def simple_periodic_send(self, bus : can.Bus):
        print("Starting to send a message every 200ms for 2s")
        # msg = can.Message(
        #     arbitration_id=0x1D41C8E8, data=[160, self.override, 0, 0, 0, 0, 0, 0], is_extended_id=True
        # )
        msg = can.Message(
            arbitration_id=0x1D41C8E8,
            data=[160, self.override, 0, 0, 0, 0, 0, 0],
            is_extended_id=True
        )
        self.periodicTask = bus.send_periodic(msg, 0.20)
        if not isinstance(self.periodicTask, can.ModifiableCyclicTaskABC):
            print("This interface doesn't seem to support modification")
            self.periodicTask.stop()
            return

    @dispatch(CanDataSimulator)
    def provide(self, flag : CanDataSimulator) :
        if self.stopEvent.is_set() :
            return
        while not self.writeQueue.empty() :
            store : CanDataSimulator = self.writeQueue.get()
            print("Id :", hex(store.arbitration_id))
            print("Dlc :", store.dlc)
            print("Data :")
            for data in store.data :
                print(" ", hex(data))
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

    @dispatch(Message)
    def provide(self, flag : Message) :
        if self.stopEvent.is_set() :
            return
        while not self.writeQueue.empty() :
            print("Data from http")
            canData : Message = self.writeQueue.get()
            if canData.arbitration_id == 0x1D41C8E8 :
                print("overwrite override")
                # self.periodicTask.stop()
                self.override = canData.data[2]
                self.periodicTask.modify_data(canData)
            else :
                self.bus.send(canData)
            sleep(0.1)

    def run(self) :
        msg = Message(
            arbitration_id=0x1D41C8E8,
            data=[160, self.override, 0, 0, 0, 0, 0, 0],
            is_extended_id=True
        )
        self.simple_periodic_send(self.bus)
        while not self.stopEvent.is_set() :
            self.provide(msg)
            sleep(0.1)