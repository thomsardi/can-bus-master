import threading
import can
import queue
from time import sleep
from can.bus import BusABC
from can.message import Message

class SingleBatteryData() :
    def __init__(self) -> None:
        self.id : int
        self.packVoltage : int
        self.packCurrent : int
        self.packSoc : int
        self.cmos : int
        self.dmos : int
        self.topTemp : int
        self.midTemp : int
        self.botTemp : int
        self.cmosTemp : int
        self.dmosTemp : int

class Stm32CurrentData() :
    def __init__(self) -> None:
        self.id : int
        self.current1 : int
        self.current2 : int

class SingleStm32Data() :
    def __init__(self) -> None:
        self.stm32CurrentData : list[Stm32CurrentData]
        self.id : int
        self.stm32RelayState : int

class Stm32DataCollection() :
    def __init__(self) -> None:
        self.stm32Data : list[SingleStm32Data]

    def insertData(self, data : SingleStm32Data) :
        for index, item in enumerate(self.stm32Data):
            if item.id == data.id :
                self.stm32Data[index].id = data.id
                self.stm32Data[index].stm32RelayState = data.stm32RelayState
                for idx, element in enumerate(data.stm32CurrentData) :
                    self.stm32Data[index].stm32CurrentData[idx] = element[idx]
                return
        self.stm32Data.append(data)

    def deleteData(self, id : int) :
        for index, item in enumerate(self.stm32Data) :
            if item.id == id :
                self.stm32Data.remove(index)
                return
    
class BatteryDataCollection() :
    def __init__(self) -> None:
        self.data : list[SingleBatteryData]
        pass
    
    def insertData(self, data : SingleBatteryData) :
        for index, item in enumerate(self.data):
            if item.id == data.id :
                self.data[index].id = data.id
                self.data[index].packVoltage = data.packVoltage
                self.data[index].packCurrent = data.packCurrent
                self.data[index].packSoc = data.packSoc
                self.data[index].cmos = data.cmos
                self.data[index].cmos = data.dmos
                self.data[index].topTemp = data.topTemp
                self.data[index].midTemp = data.midTemp
                self.data[index].botTemp = data.botTemp
                return
        self.data.append(data)
    
    def deleteData(self, id : int) :
        for index, item in enumerate(self.data) :
            if item.id == id :
                self.data.remove(index)
                return

    def getCollectionData(self) -> list :
        return self.data 

class Data() :
    def __init__(self) -> None:
        pass
    
    def toDict(self, batteryData : SingleBatteryData) -> dict :
        list_dict = {
            "id" : batteryData.id,
            "pack_voltage" : batteryData.packVoltage,
            "pack_current" : batteryData.packCurrent,
            "soc" : batteryData.packSoc,
            "cmos" : batteryData.cmos,
            "dmos" : batteryData.dmos,
            "top_temp" : batteryData.topTemp,
            "mid_temp" : batteryData.midTemp,
            "bot_temp" : batteryData.botTemp,
            "cmos_temp" : batteryData.cmosTemp,
            "dmos_temp" : batteryData.dmosTemp
        }
        result = {
            "battery_data" : list_dict
        }
        return result

    def buildData(self, batteryData : list[SingleBatteryData], stm32Data : list[SingleStm32Data]) -> dict:
        batData = list[dict]
        stmData = list[dict]

        for item in batteryData :
            list_dict = {
                "id" : item.id,
                "pack_voltage" : item.packVoltage,
                "pack_current" : item.packCurrent,
                "soc" : item.packSoc,
                "cmos" : item.cmos,
                "dmos" : item.dmos
            }
            batData.append(list_dict)

        for item in stm32Data :
            list_dict = {
                "id" : item.id,
                "stm32_current" : item.stm32CurrentData,
                "stm32_relay" : item.stm32RelayState
            }
            stmData.append(list_dict)
        data = {
            "battery_data" : batData,
            "stm32_data" : stmData
        }
        return data

class DataHandler() :
    def __init__(self) -> None:
        self._packVoltageMaxValue = 25700
        self._packCurrentMaxValue = 25700
        self._packSocMaxValue = 25700

    def getPackVoltage(self, msg : Message) -> int :
        result = abs(self._packVoltageMaxValue - (msg.data[2] + (msg.data[3] << 8))) * 2
        return result
    
    def getPackCurrent(self, msg : Message) -> int :
        result = abs(self._packCurrentMaxValue - (msg.data[4] + (msg.data[5] << 8)))
        return result
    
    def getPackSoc(self, msg : Message) -> int :
        result = abs(self._packSocMaxValue - (msg.data[6] + (msg.data[7] << 8)))
        return result
    
    def getTemperature(self, msg : Message, startIndex : int, length : int, maxValue : int = 100) -> int :
        result = 0
        raw = 0
        for i in range(0, length, 1) :
            val = 0
            val = (msg.data[startIndex + i] << (i*8))
            raw += val
        result = abs(maxValue - raw)
        return result

class CanBus(threading.Thread) :
    def __init__(self, name : str, stopEvent : threading.Event):
        threading.Thread.__init__(self, name = name)
        self._batteryDataCollection = BatteryDataCollection()
        self._stm32DataCollection = Stm32DataCollection()
        self._Data = Data()
        self._interface = "socketcan"
        self._channel = "can0"
        self._bitrate = 125000
        self._increment = 0
        self._stopEvent : threading.Event = stopEvent
        self._queue : queue.Queue = None
        self._packDataType = 0x764C840
        self._mosfTempType = 0x763C840
        self._pack_addr = 0x764C864
        self._mosf_temp_addr = 0x763C864
    
    def configureBus(self, interface : str, channel : str, bitrate : int) :
        self._interface = interface
        self._channel = channel
        self._bitrate = bitrate

    def setBuffer(self, queue : queue.Queue) :
        self._queue = queue

    def handleCase(self, msg : Message) :
        value = msg.arbitration_id & 0xFFFFFFC0
        dataHandler = DataHandler()
        if (value == self._packDataType) :
            proc = Data()
            singleBatData = SingleBatteryData()
            singleBatData.id = self._pack_addr - msg.arbitration_id
            singleBatData.packVoltage = dataHandler.getPackVoltage(msg)
            singleBatData.packCurrent = dataHandler.getPackCurrent(msg)
            singleBatData.packSoc = dataHandler.getPackSoc(msg)
            # self._batteryDataCollection.insertData(singleBatData)
            # self._queue.put(proc.toDict(singleBatData))
            print(proc.toDict(singleBatData))

        elif(value == self._mosfTempType) :
            proc = Data()
            singleBatData = SingleBatteryData()
            singleBatData.id = self._mosf_temp_addr - msg.arbitration_id
            singleBatData.topTemp = dataHandler.getTemperature(msg, 3, 1)
            singleBatData.midTemp = dataHandler.getTemperature(msg, 4, 1)
            singleBatData.botTemp = dataHandler.getTemperature(msg, 5, 1)
            singleBatData.cmosTemp = dataHandler.getTemperature(msg, 6, 1)
            singleBatData.dmosTemp = dataHandler.getTemperature(msg, 7, 1)
            if (msg.data[0] == 0x53) :
                singleBatData.cmos = 1
                singleBatData.dmos = 0
            elif (msg.data[0] == 0x42) :
                singleBatData.cmos = 0
                singleBatData.dmos = 1
            elif (msg.data[0] == 0x31) :
                singleBatData.cmos = 1
                singleBatData.dmos = 1
            elif (msg.data[0] == 0x65) :
                singleBatData.cmos = 0
                singleBatData.dmos = 0
            # self._batteryDataCollection.insertData(singleBatData)
            # self._queue.put(proc.toDict(singleBatData))
            print(proc.toDict(singleBatData))
        
    def read(self) :
        filters = [
            {"can_id": 0x540C840, "can_mask": 0x5D8FF40, "extended": True}
        ]
        with can.interface.Bus(interface=self._interface, channel=self._channel, bitrate=self._bitrate) as bus :
            bus.set_filters(filters=filters)
            for msg in bus :
                if self._stopEvent.is_set() :
                    return
                # print("frame Id :", hex(msg.arbitration_id))
                # print("frame Id :", format(msg.arbitration_id, '02x'))
                # print("data length :", msg.dlc)
                # res = ' '.join(format(x, '02x') for x in msg.data)
                # print("data :", res)
                # self._queue.put(msg)
                self.handleCase(msg)

    def run(self) -> None:
        while not self._stopEvent.is_set() :
            # print(self._increment)
            # self._queue.put(self._increment)
            # self._increment += 1
            # sleep(0.1)
            self.read()

        print("CanBus thread stopped")