import copy
from multipledispatch import dispatch
from dataproviderthread import CanDataSimulator
from time import sleep
from typing import Any
from can import Listener
from can.message import Message

class SingleMosfetData() :
    def __init__(self) -> None:
        self.id : int = 0
        self.cmos : int = 0
        self.dmos : int = 0
        self.topTemp : int = 0
        self.midTemp : int = 0
        self.botTemp : int = 0
        self.cmosTemp : int = 0
        self.dmosTemp : int = 0

    def printAll(self) :
        print("Id :", self.id)
        print("Cmos :", self.cmos)
        print("Dmos :", self.dmos)
        print("Top Temp :", self.topTemp)
        print("Mid Temp :", self.midTemp)
        print("Bot Temp :", self.botTemp)
        print("Cmos Temp :", self.cmosTemp)
        print("Dmos Temp :", self.dmosTemp)

class SinglePackData() :
    def __init__(self) -> None:
        self.id : int = 0
        self.packVoltage : int = 0
        self.packCurrent : int = 0
        self.packSoc : int = 0

    def printAll(self) :
        print("Id :", self.id)
        print("Pack Voltage :", self.packVoltage)
        print("Pack Current :", self.packCurrent)
        print("Pack SoC :", self.packSoc)

class Stm32Current() :
    def __init__(self) -> None:
        self.number : int = 0
        self.current : int = 0

class SingleStm32Data() :
    def __init__(self) -> None:
        self.id : int = 0
        self.relayState : int = 0
        self.current : list[Stm32Current] = []

    def insertData(self, data : Stm32Current) :
        store = copy.deepcopy(data)
        for index, element in enumerate(self.current) :
            if element.number == store.number :
                # print("Found, overwrite existing data")
                self.current[index].number = store.number
                self.current[index].current = store.current
                return
        # print("Not Found, insert new data")
        self.current.append(store)
        # for i in self.current :
        #     print(i.current)
        #     pass
        
    def deleteData(self, number : int) :
        for index, element in enumerate(self.current) :
            if element.number == number :
                self.current.remove(index)
                break

    def printAll(self) :
        print("id :", self.id)
        print("relay state :", self.relayState)
        for element in self.current :
            print("Number :", element.number)
            print("Current :", element.current)

class DataCollection() :
    def __init__(self) -> None:
        self.packData : list[SinglePackData] = []
        self.mosfetData : list[SingleMosfetData] = []
        self.stm32Data = SingleStm32Data()
    
    @dispatch(SinglePackData)
    def insertData(self, data : SinglePackData) :
        store = copy.deepcopy(data)
        for index, element in enumerate(self.packData) :
            if element.id == store.id :
                self.packData[index].id = store.id
                self.packData[index].packVoltage = store.packVoltage
                self.packData[index].packCurrent = store.packCurrent
                self.packData[index].packSoc = store.packSoc
                return
        self.packData.append(store)

    @dispatch(SingleMosfetData)
    def insertData(self, data : SingleMosfetData) :
        store = copy.deepcopy(data)
        for index, element in enumerate(self.mosfetData) :
            if element.id == store.id :
                self.mosfetData[index].id = store.id
                self.mosfetData[index].cmos = store.cmos
                self.mosfetData[index].dmos = store.dmos
                self.mosfetData[index].topTemp = store.topTemp
                self.mosfetData[index].midTemp = store.midTemp
                self.mosfetData[index].botTemp = store.botTemp
                self.mosfetData[index].cmosTemp = store.cmosTemp
                self.mosfetData[index].dmosTemp = store.dmosTemp
                return
        self.mosfetData.append(store)

    @dispatch(SingleStm32Data)
    def insertData(self, data : SingleStm32Data) :
        store = copy.deepcopy(data)
        self.stm32Data.id = store.id
        self.stm32Data.relayState = store.relayState
        self.stm32Data.current.clear()
        self.stm32Data.current = store.current.copy()

    def buildPackData(self) -> list:
        dataList : list[dict] = []
        for packData in self.packData :
            for mosfetData in self.mosfetData :
                if packData.id == mosfetData.id :
                    output = {
                        "id" : packData.id,
                        "pack_voltage" : packData.packVoltage,
                        "pack_current" : packData.packCurrent,
                        "soc" : packData.packSoc,
                        "cmos" : mosfetData.cmos,
                        "dmos" : mosfetData.dmos,
                        "top_temp" : mosfetData.topTemp,
                        "mid_temp" : mosfetData.midTemp,
                        "bot_temp" : mosfetData.botTemp,
                        "cmos_temp" : mosfetData.cmosTemp,
                        "dmos_temp" : mosfetData.dmosTemp
                    }
                    dataList.append(output)
        # print(dataList)
        # print('\n')
        return dataList

    def deleteData(self, id : int) :
        for index, element in enumerate(self.packData) :
            if element.id == id :
                self.packData.remove(index)
                break
        for index, element in enumerate(self.mosfetData) :
            if element.id == id :
                self.mosfetData.remove(index)
                break
    
    def buildStm32Data(self) -> list :
        dataList = []
        
        dataCurrentList : list[dict] = []
        for dataCurrent in self.stm32Data.current :
            temp_dict = {
                "number" : dataCurrent.number,
                "current" : dataCurrent.current
            }
            dataCurrentList.append(temp_dict)

        stm32Dict = {
            "id" : self.stm32Data.id,
            "stm32_current" : dataCurrentList,
            "stm32_relay" : self.stm32Data.relayState
        }
        dataList.append(stm32Dict)
        # print(dataList)
        return dataList

    def buildData(self) -> dict:
        result = {
            "battery_data" : self.buildPackData(),
            "stm32_data" : self.buildStm32Data()
        }
        return result

    def clearAll(self) :
        self.packData.clear()
        self.mosfetData.clear()

class DataProcess() :
    def __init__(self) -> None:
        self._packVoltageMaxValue = 25700
        self._packCurrentMaxValue = 25700
        self._packSocMaxValue = 25700
    
    @dispatch(CanDataSimulator)
    def getPackVoltage(self, msg : CanDataSimulator) -> int :
        result = abs(self._packVoltageMaxValue - (msg.data[2] + (msg.data[3] << 8))) * 2
        return result
    
    @dispatch(Message)
    def getPackVoltage(self, msg : Message) -> int :
        result = abs(self._packVoltageMaxValue - (msg.data[2] + (msg.data[3] << 8))) * 2
        return result
    
    @dispatch(CanDataSimulator)
    def getPackCurrent(self, msg : CanDataSimulator) -> int :
        result = abs(self._packCurrentMaxValue - (msg.data[4] + (msg.data[5] << 8)))
        return result
    
    @dispatch(Message)
    def getPackCurrent(self, msg : Message) -> int :
        result = abs(self._packCurrentMaxValue - (msg.data[4] + (msg.data[5] << 8)))
        return result
    
    @dispatch(CanDataSimulator)
    def getPackSoc(self, msg : CanDataSimulator) -> int :
        result = abs(self._packSocMaxValue - (msg.data[6] + (msg.data[7] << 8)))
        return result
    
    @dispatch(Message)
    def getPackSoc(self, msg : Message) -> int :
        result = abs(self._packSocMaxValue - (msg.data[6] + (msg.data[7] << 8)))
        return result
    
    @dispatch(CanDataSimulator, int, int, int)
    def getTemperature(self, msg : CanDataSimulator, startIndex : int, length : int, maxValue : int = 100) -> int :
        result = 0
        raw = 0
        for i in range(0, length, 1) :
            val = 0
            val = (msg.data[startIndex + i] << (i*8))
            raw += val
        result = abs(maxValue - raw)
        return result
    
    @dispatch(Message, int, int, int)
    def getTemperature(self, msg : Message, startIndex : int, length : int, maxValue : int = 100) -> int :
        result = 0
        raw = 0
        for i in range(0, length, 1) :
            val = 0
            val = (msg.data[startIndex + i] << (i*8))
            raw += val
        result = abs(maxValue - raw)
        return result
    
    @dispatch(CanDataSimulator, int, int)
    def getCurrent(self, msg : CanDataSimulator, startIndex : int, length : int) -> int :
        result = 0
        raw = 0
        for i in range(0, length, 1) :
            val = 0
            val = (msg.data[startIndex + i] * pow(10, length - (i*2)))
            raw += val
        result = raw
        return result
    
    @dispatch(Message, int, int)
    def getCurrent(self, msg : Message, startIndex : int, length : int) -> int :
        result = 0
        raw = 0
        for i in range(0, length, 1) :
            val = 0
            val = (msg.data[startIndex + i] * pow(10, length - (i*2)))
            raw += val
        result = raw
        return result
    
    @dispatch(CanDataSimulator)
    def getRelay(self, msg : CanDataSimulator) -> int :
        return msg.data[1]
    
    @dispatch(Message)
    def getRelay(self, msg : Message) -> int :
        return msg.data[1]

class CanCallBack(Listener) :
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.pack_base_addr = 0x764C864
        self.mosf_temp_base_addr = 0x763C864
        self.packDataFrame = 0x764C840
        self.mosfTempFrame = 0x763C840
        self.stm32Frame = 0x1D40C8C0
        self.dataCollection = DataCollection()

    def on_message_received(self, msg: Message) -> None:
        print(hex(msg.arbitration_id))
        self.handleMessage(msg)
    
    @dispatch(Message)
    def handleMessage(self, msg : Message) :
        frame = msg.arbitration_id & 0xFFFFFFC0
        if (frame == self.packDataFrame) :
            dataProcess = DataProcess()
            singleBatData = SinglePackData()
            singleBatData.id = self.pack_base_addr - msg.arbitration_id
            singleBatData.packVoltage = dataProcess.getPackVoltage(msg)
            singleBatData.packCurrent = dataProcess.getPackCurrent(msg)
            singleBatData.packSoc = dataProcess.getPackSoc(msg)
            self.dataCollection.insertData(singleBatData)
            # singleBatData.printAll()
        elif(frame == self.mosfTempFrame) :
            dataProcess = DataProcess()
            singleMosfetData = SingleMosfetData()
            singleMosfetData.id = self.mosf_temp_base_addr - msg.arbitration_id
            singleMosfetData.topTemp = dataProcess.getTemperature(msg, 3, 1, 100)
            singleMosfetData.midTemp = dataProcess.getTemperature(msg, 4, 1, 100)
            singleMosfetData.botTemp = dataProcess.getTemperature(msg, 5, 1, 100)
            singleMosfetData.cmosTemp = dataProcess.getTemperature(msg, 6, 1, 100)
            singleMosfetData.dmosTemp = dataProcess.getTemperature(msg, 7, 1, 100)
            if (msg.data[0] == 0x53) :
                singleMosfetData.cmos = 1
                singleMosfetData.dmos = 0
            elif (msg.data[0] == 0x42) :
                singleMosfetData.cmos = 0
                singleMosfetData.dmos = 1
            elif (msg.data[0] == 0x31) :
                singleMosfetData.cmos = 1
                singleMosfetData.dmos = 1
            elif (msg.data[0] == 0x65) :
                singleMosfetData.cmos = 0
                singleMosfetData.dmos = 0
            self.dataCollection.insertData(singleMosfetData)
            self.dataCollection.buildPackData()
            # singleMosfetData.printAll()
        elif(frame == self.stm32Frame) :
            dataProcess = DataProcess()
            stm32Current1 = Stm32Current()
            stm32SingleData = SingleStm32Data()
            stm32Current1.number = 1
            stm32Current1.current = dataProcess.getCurrent(msg, 2, 2)
            stm32SingleData.insertData(stm32Current1)
            stm32Current1.number = 2
            stm32Current1.current = dataProcess.getCurrent(msg, 4, 2)
            stm32SingleData.insertData(stm32Current1)
            stm32Current1.number = 3
            stm32Current1.current = dataProcess.getCurrent(msg, 6, 2)
            stm32SingleData.insertData(stm32Current1)
            stm32SingleData.id = 1
            stm32SingleData.relayState = dataProcess.getRelay(msg)
            self.dataCollection.insertData(stm32SingleData)
            self.dataCollection.buildStm32Data()
