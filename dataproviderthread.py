import threading
import queue
import can
from can import Listener
from time import sleep
from can.message import Message
from multipledispatch import dispatch
from can.broadcastmanager import ModifiableCyclicTaskABC, CyclicSendTaskABC
from can.interfaces.socketcan.socketcan import CyclicSendTask

class CanDataSimulator() :
    """
    Can data simulator, this simulate the frame of the can data
    """

    def __init__(self) -> None:
        self.arbitration_id : int
        self.dlc : int
        self.data : list[int] = []

class CanBatteryPackSimulatorData() :
    """
    Can battery pack data generator, this simulate the data of the battery pack and to be passed
    into provider thread to be read
    """
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
    """
    This class derived from thread class, this is used as reader and writer of the can bus line 
    """
    def __init__(self, name : str, syncFlag : threading.Condition, buffer : queue.Queue) :
        """
        Class constructor and init

        Args:
            name (str) : the name of the thread
            syncFlag (threading.Condition) : the flag to synchronize with lock
            buffer (queue.Queue) : the write buffer to be sent into can bus line 
        """
        threading.Thread.__init__(self, name=name)
        self.stopEvent = threading.Event()
        self.syncFlag = syncFlag
        self.buffer : queue.Queue = buffer
        self.daemon = True  # set the thread into daemon thread
        self.batteryPack : list[CanBatteryPackSimulatorData] = []
        self.writeQueue = queue.Queue()
        self.override : int = 0
        self.keepAliveId = 0x1D41C8E8
        self.bus : can.ThreadSafeBus = None
        self.periodicKeepAlive : ModifiableCyclicTaskABC = None
        self.periodicWake : list[CyclicSendTaskABC] = []
        self.listenerList : list[Listener] = []
        
        self.canFilter = [
            {"can_id": 0x540C840, "can_mask": 0x5D8FF40, "extended": True}
        ]

        for i in range(1,17,1) :
            sim = CanBatteryPackSimulatorData(i)
            self.batteryPack.append(sim)

    def initBus(self, bus : can.ThreadSafeBus) :
        """
        Init bus and pass the can.ThreadSafeBus object into this class bus

        Args:
            bus (can.ThreadSafeBus) : can bus object, this bus will be used as send and receive bus
        """
        self.bus = bus

    def setListener(self, listener : list[Listener]) :
        """
        Register the listener / callback on can.Notifier. the listener will be called everytime can bus line
        received data

        Args:
            listener (list[Listener]) : list of 'Listener' object
        """
        self.listenerList = listener
        can.Notifier(self.bus, listener)
        # pass

    def link(self, queue : queue.Queue) :
        """
        Link / register the outside queue into this class queue, this queue will be used as write queue for can bus line
        everytime this queue is not empty, the queue data will be sent into can bus line in FIFO manner

        Args:
            queue (queue.Queue) : the queue for write queue
        """
        self.writeQueue = queue

    def insertQueue(self, msg : CanDataSimulator) :
        """
        Insert CanDataSimulator into this class write queue

        Args:
            msg (CanDataSimulator) : CAN data simulator message
        """
        self.writeQueue.put(msg)

    def keep_alive_periodic_send(self, bus : can.Bus):
        """
        Periodically send keep alive message + override into can bus line. this message is important for 
        taking control of stm32. To control stm32, keep alive and override message need to be sent periodically

        Args:
            bus (can.Bus) : bus object
        """
        print("Starting to send a keep alive message every 600ms")
        # msg = can.Message(
        #     arbitration_id=0x1D41C8E8, data=[160, self.override, 0, 0, 0, 0, 0, 0], is_extended_id=True
        # )
        uniqueId = 160
        msg = can.Message(
            arbitration_id=0x1D41C8E8,
            data=[(uniqueId & 0xFF), (uniqueId >> 8), self.override, 0, 0, 0, 0, 0],
            is_extended_id=True
        )
        self.periodicKeepAlive = bus.send_periodic(msg, 0.6) #send message every 0.6s (600ms)
        if not isinstance(self.periodicKeepAlive, can.ModifiableCyclicTaskABC):
            print("This interface doesn't seem to support modification")
            self.periodicKeepAlive.stop()
            return
        
    def wake_periodic_send(self, bus : can.Bus):
        """
        Periodically send wake up message into can bus line. This message is used to keep the battery pack awake
        and prevent the battery pack going into sleep. for now the wake up message is for id 1 - 32

        Args:
            bus (can.Bus) : bus object

        """
        #TODO : add flexible device id, not fixed into 1 - 32 id
        print("Starting to send wake message every 500ms")
        msgList : list[Message] = []
        for i in range(1,33,1) :
            msg = can.Message(
                arbitration_id=0x12640066 + (i<<8),
                data=[0x33, 0x63, 0x60, 0x64, 0x64, 0x64, 0x53, 0x64],
                is_extended_id=True
            )
            msgList.append(msg)    
        
        for index, element in enumerate(msgList) :
            task = bus.send_periodic(element, 0.50 + (index*0.01), store_task=False)
            assert isinstance(task, can.CyclicSendTaskABC)
            self.periodicWake.append(task) #store the tasklist to track the task, for later can be used to stop the task

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
        """
        get data from write queue and send them into can bus line

        Args:
            flag (Message) : flag used to overload the function

        """
        if self.stopEvent.is_set() :
            return
        while not self.writeQueue.empty() :
            print("Data from http")
            canData : Message = self.writeQueue.get()
            self.writeQueue.task_done()
            if canData.arbitration_id == 0x1D41C8E8 : #when the frame id is keep alive frame id
                print("overwrite override")
                # self.periodicTask.stop()
                self.override = canData.data[2] #update this class override flag
                self.periodicKeepAlive.modify_data(canData) #modify the override data
            else :
                self.bus.send(canData)
            sleep(0.1) #sleep for 100ms to lighten the cpu

    def run(self) :
        self.stopEvent.clear()
        print("Start can")
        if self.bus is None :
            print("Bus is not yet initialized, call the initBus method, and set the listener / callback")
            print("exiting the thread")
            for listener in self.listenerList :
                can.Notifier.remove_listener(listener=listener)
            self.stopEvent.set()
            return
        msg = Message(
            arbitration_id=0x12640066,
            data=[1, 2, 3, 4, 5, 6, 7, 8],
            is_extended_id=True
        )
        self.keep_alive_periodic_send(self.bus)
        self.wake_periodic_send(self.bus)
        while not self.stopEvent.is_set() :
            self.provide(msg)
            sleep(0.1)
        for task in self.periodicWake :
            task.stop()
        self.periodicWake.clear()
        self.periodicKeepAlive.stop()        

    def stop(self) :
        self.stopEvent.set()