import copy
from multipledispatch import dispatch
from dataproviderthread import CanDataSimulator
from time import sleep
from typing import Any
from can import Listener
from can.message import Message
from threading import Lock

class SingleMosfetData() :
    def __init__(self) -> None:
        self.id : int = 0
        self.isUpdated = 0
        self.cmos : int = 0
        self.dmos : int = 0
        self.topTemp : int = 0
        self.midTemp : int = 0
        self.botTemp : int = 0
        self.cmosTemp : int = 0
        self.dmosTemp : int = 0
        self.cnt : int = 0
        self.lastCnt : int = 0

    def updateCnt(self) :
        self.lastCnt = self.cnt

    def incCnt(self) :
        self.cnt += 1

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
        self.isUpdated : int = 0
        self.packVoltage : int = 0
        self.packCurrent : int = 0
        self.packSoc : int = 0
        self.cnt : int = 0
        self.lastCnt : int = 0

    def updateCnt(self) :
        self.lastCnt = self.cnt

    def incCnt(self) :
        self.cnt += 1

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
        self.firmwareVersion : int = 0
        self.relayState : int = 0
        self.current : list[Stm32Current] = []

    def insertData(self, data : Stm32Current) :
        """
        Insert data, overwrite existing element if it is already exist, if not it will add new element

        Args:
            data (Stm32Current) : Stm32Current object
        """
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
        """
        Find the existing number and delete the data

        Args:
            number (int) : number to search
        """
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
    """
    Collection of data, consist of SinglePackData, SingleMosfetData and SingleStm32Data
    """
    def __init__(self) -> None:
        self.packData : list[SinglePackData] = []
        self.mosfetData : list[SingleMosfetData] = []
        self.stm32Data = SingleStm32Data()
        self.totalBattery = 0
        self.averageVoltage : int = 0
        self.totalCurrent : int = 0
        self.averageSoc :int = 0
        self.activeBattery = 0
        self.inactiveBattery = 0
        self.lowVoltageVsat = 0
        self.reconnectVoltageVsat = 0
        self.lowVoltageOther = 0
        self.reconnectVoltageOther = 0
        self.lowVoltageBts = 0
        self.reconnectVoltageBts = 0
    
    @dispatch(SinglePackData)
    def insertData(self, data : SinglePackData) :
        """
        Insert data of SinglePackData, overwrite existing data if any or add new element

        Args:
            data (SinglePackData) : SinglePackData object to be insert into
        """
        store = copy.deepcopy(data)
        for index, element in enumerate(self.packData) :
            if element.id == store.id :
                self.packData[index].isUpdated = store.isUpdated
                self.packData[index].id = store.id
                self.packData[index].packVoltage = store.packVoltage
                self.packData[index].packCurrent = store.packCurrent
                self.packData[index].packSoc = store.packSoc
                self.packData[index].incCnt() #increment the counter to indicate that the data was updated
                return
        store.incCnt() #increment the counter to indicate that the data was updated
        self.packData.append(store)

    @dispatch(SingleMosfetData)
    def insertData(self, data : SingleMosfetData) :
        """
        Insert data of SingleMosfetData, overwrite existing data if any or add new element

        Args:
            data (SingleMosfetData) : SingleMosfetData object to be insert into
        """
        store = copy.deepcopy(data)
        for index, element in enumerate(self.mosfetData) :
            if element.id == store.id :
                self.mosfetData[index].isUpdated = store.isUpdated
                self.mosfetData[index].id = store.id
                self.mosfetData[index].cmos = store.cmos
                self.mosfetData[index].dmos = store.dmos
                self.mosfetData[index].topTemp = store.topTemp
                self.mosfetData[index].midTemp = store.midTemp
                self.mosfetData[index].botTemp = store.botTemp
                self.mosfetData[index].cmosTemp = store.cmosTemp
                self.mosfetData[index].dmosTemp = store.dmosTemp
                self.mosfetData[index].incCnt() #increment the counter to indicate that the data was updated
                return
        store.incCnt() #increment the counter to indicate that the data was updated
        self.mosfetData.append(store)

    @dispatch(SingleStm32Data)
    def insertData(self, data : SingleStm32Data) :
        """
        Insert data of SingleStm32Data, overwrite existing data if any or add new element

        Args:
            data (SingleStm32Data) : SingleStm32Data object to be insert into
        """
        store = copy.deepcopy(data)
        self.stm32Data.id = store.id
        self.stm32Data.firmwareVersion = store.firmwareVersion
        self.stm32Data.relayState = store.relayState
        self.stm32Data.current.clear() #clear the old data 
        self.stm32Data.current = store.current.copy() #replace with latest data

    def buildPackData(self) -> dict:
        """
        Build Pack Data into json format

        Return:
            dict data of pack data and mosfet data
        """
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
        output : dict = {
            "total_battery" : self.totalBattery,
            "active_battery" : self.activeBattery,
            "inactive_battery" : self.inactiveBattery,
            "voltage" : self.averageVoltage,
            "current" : self.totalCurrent,
            "soc" : self.averageSoc,
            "details" : dataList
        }
        # print(dataList)
        # print('\n')
        return output

    def deleteData(self, id : int) :
        """
        Delete the data of the existing id

        Args:
            id (int) : id to search
        """
        for index, element in enumerate(self.packData) :
            if element.id == id :
                self.packData.remove(index)
                break
        for index, element in enumerate(self.mosfetData) :
            if element.id == id :
                self.mosfetData.remove(index)
                break
    
    def buildStm32Data(self) -> list :
        """
        Build STM32 Data into json format

        Return:
            list data of STM32 Data
        """
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
            "firmware_version" : self.stm32Data.firmwareVersion,
            "stm32_current" : dataCurrentList,
            "stm32_relay" : self.stm32Data.relayState
        }
        dataList.append(stm32Dict)
        # print(dataList)
        return dataList

    def buildData(self) -> dict:
        """
        Build data into dict format

        Return:
            dict of pack data and stm32 data
        """
        result = {
            "battery_data" : self.buildPackData(),
            "stm32_data" : self.buildStm32Data()
        }
        return result

    def packCalculate(self) :
        """
        Calculate pack info such as average voltage, average soc, total current, total battery, total active battery
        & total inactive battery. This method has to be called before using value above to ensure that the values properly
        updated
        """
        totalVoltage = 0
        averageVoltage = 0
        totalCurrent = 0
        totalSoc = 0
        averageSoc = 0
        totalBattery = 0
        activeBattery = 0
        inactiveBattery = 0
        for pack in self.packData :
            for mosfet in self.mosfetData :
                if pack.id == mosfet.id : #find status of dmos
                    if (pack.isUpdated) and (mosfet.dmos) : #if dmos is active and data constanly updated, count the data
                        activeBattery += 1
                        totalVoltage += pack.packVoltage
                        totalCurrent += pack.packCurrent
                        totalSoc += pack.packSoc
                    break
        if(activeBattery != 0) :
            averageVoltage = totalVoltage / activeBattery
            averageSoc = totalSoc / activeBattery
        totalBattery = len(self.packData)
        inactiveBattery = totalBattery - activeBattery
        self.totalBattery = totalBattery
        self.inactiveBattery = inactiveBattery
        self.activeBattery = activeBattery
        self.averageVoltage = round(averageVoltage)
        self.averageSoc = round(averageSoc)
        self.totalCurrent = totalCurrent

    def clearAll(self) :
        """
        Clear all the data
        """
        self.packData.clear()
        self.mosfetData.clear()

    def cleanUp(self) :
        """
        Provide a cleanup method to automatically delete non updated data, this method will check on 
        value changed counter. When the counter value doesn't change for a certain amount of time, the data get
        deleted. Calling this method too fast will result in data get deleted too soon, use a reasonable timing.
        E.g the data get updated every 1s, don't call this method < 1s 
        """
        # print("Begin")
        for index, pack in enumerate(self.packData) :
            # print("Pack Info")
            # print("Id :", pack.id)
            # print("counter now :", pack.cnt)
            # print("prev counter :", pack.lastCnt)
            # print("voltage :", pack.packVoltage)
            # print("Pack index :", index)
            # print("pack stack size :", len(self.packData))
            for mosIndex, mosfet in enumerate(self.mosfetData) :
                if pack.id == mosfet.id :
                    # print("Id :", mosfet.id)
                    # print("counter :", mosfet.cnt)
                    # print("prev counter :", mosfet.lastCnt)
                    # print("dmos :", mosfet.dmos)
                    # print("cmos :", mosfet.cmos)
                    if (pack.lastCnt == pack.cnt) :
                        # print("Mosfet index :", mosIndex)
                        # print("mosfet stack size :", len(self.mosfetData))
                        self.mosfetData.pop(mosIndex)
                        self.packData.pop(index)
                        break
                    else :
                        self.mosfetData[index].updateCnt()
                        self.packData[index].updateCnt()
                        break
            

class DataProcess() :
    """
    Helper to convert can bus message into some value
    """
    def __init__(self) -> None:
        self._packVoltageMaxValue = 25700
        self._packCurrentMaxValue = 25700
        self._packSocMaxValue = 25700
    
    @dispatch(CanDataSimulator)
    def getPackVoltage(self, msg : CanDataSimulator) -> int :
        if len(msg.data) < 8 :
            return None
        lowByte = msg.data[2]
        highByte = msg.data[3]
        if (lowByte > 0x64) : # if the low byte higher than 100 (0x64)
            highByte -= 1
        
        result = abs(self._packVoltageMaxValue - ((highByte << 8) + lowByte))
        return result
    
    @dispatch(Message)
    def getPackVoltage(self, msg : Message) -> int :
        """
        Get the pack voltage from can bus message

        Args:
            msg (Message) : can bus message
        """
        if len(msg.data) < 8 :
            return None
        lowByte = msg.data[2]
        highByte = msg.data[3]
        if (lowByte > 0x64) : # if the low byte higher than 100 (0x64)
            highByte -= 1 #decrease highbyte by 1
        
        result = abs(self._packVoltageMaxValue - ((highByte << 8) + lowByte))
        return result
    
    @dispatch(CanDataSimulator)
    def getPackCurrent(self, msg : CanDataSimulator) -> int :
        if len(msg.data) < 8 :
            return None
        lowByte = msg.data[4]
        highByte = msg.data[5]
        if (lowByte > 0x64) : # if the low byte higher than 100 (0x64)
            highByte -= 1
        
        result = abs(self._packVoltageMaxValue - ((highByte << 8) + lowByte))
        return result
    
    @dispatch(Message)
    def getPackCurrent(self, msg : Message) -> int :
        """
        Get the pack current from can bus message

        Args:
            msg (Message) : can bus message
        """
        if len(msg.data) < 8 :
            return None
        lowByte = msg.data[4]
        highByte = msg.data[5]
        if (lowByte > 0x64) : # if the low byte higher than 100 (0x64)
            highByte -= 1
        
        result = abs(self._packVoltageMaxValue - ((highByte << 8) + lowByte))
        return result
    
    @dispatch(CanDataSimulator)
    def getPackSoc(self, msg : CanDataSimulator) -> int :
        if len(msg.data) < 8 :
            return None
        lowByte = msg.data[6]
        highByte = msg.data[7]
        if (lowByte > 0x64) : # if the low byte higher than 100 (0x64)
            highByte -= 1
        
        result = abs(self._packVoltageMaxValue - ((highByte << 8) + lowByte))
        return result
    
    @dispatch(Message)
    def getPackSoc(self, msg : Message) -> int :
        """
        Get the pack soc from can bus message

        Args:
            msg (Message) : can bus message
        """
        if len(msg.data) < 8 :
            return None
        lowByte = msg.data[6]
        highByte = msg.data[7]
        if (lowByte > 0x64) : # if the low byte higher than 100 (0x64)
            highByte -= 1
        result = abs(self._packVoltageMaxValue - ((highByte << 8) + lowByte))
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
        """
        Get the temperature from can bus message

        Args:
            msg (Message) : can bus message
            startIndex (int) : start index of can bus data frame
            length (int) : number of data to get
            maxValue (int) : max value as constant for calculation
        """
        result = 0
        raw = 0
        if (len(msg.data) < 8) :
            return result
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
        """
        Get the current of stm32 from can bus message

        Args:
            msg (Message) : can bus message
            startIndex (int) : start index of the can bus data frame
            length (int) : number of data to get
        """
        result = 0
        raw = 0
        if (len(msg.data) < 8) :
            return result
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
        """
        Get relay value from can bus data

        Args:
            msg (Message) : can bus message frame
        """
        return msg.data[1]

class CanCallBack(Listener) :
    """
    Listener for can bus
    """
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.pack_base_addr = 0x764C864
        self.mosf_temp_base_addr = 0x763C864
        self.packDataFrame = 0x764C840
        self.mosfTempFrame = 0x763C840
        self.stm32Frame = 0x1D40C8C0
        self.stm32CurrentFrame = 0x1D40C8E7
        self.stm32LowVoltageParamFrame = 0x1D40C8E8
        self.stm32ReconnectVoltageParamFrame = 0x1D40C8E9
        self.lock = Lock()
        self.dataCollection = DataCollection()

    def on_message_received(self, msg: Message) -> None:
        """
        Execute every time the can bus line receiving data
        """
        print(hex(msg.arbitration_id))
        self.handleMessage(msg)
    
    @dispatch(Message)
    def handleMessage(self, msg : Message) :
        """
        Handle and parse the can bus message

        Args:
            msg (Message) : can bus message
        """
        frame = msg.arbitration_id & 0xFFFFFFC0 #zero'ed the id byte
        if(len(msg.data) < 8) :
            return
        # print("hex and :", hex(frame))
        # self.lock.acquire()
        if (frame == self.packDataFrame) : #if the can message frame is pack data frame
            dataProcess = DataProcess()
            singleBatData = SinglePackData()
            singleBatData.id = self.pack_base_addr - msg.arbitration_id
            singleBatData.isUpdated = 1
            singleBatData.packVoltage = dataProcess.getPackVoltage(msg)
            singleBatData.packCurrent = dataProcess.getPackCurrent(msg)
            singleBatData.packSoc = dataProcess.getPackSoc(msg)
            self.dataCollection.insertData(singleBatData)
            print(f"pack data id {singleBatData.id} updated")
            # singleBatData.printAll()
        elif(frame == self.mosfTempFrame) : #if the can message frame is mosfet data frame
            dataProcess = DataProcess()
            singleMosfetData = SingleMosfetData()
            singleMosfetData.id = self.mosf_temp_base_addr - msg.arbitration_id
            singleMosfetData.isUpdated = 1
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
            print(f"mosfet data id {singleMosfetData.id} updated")
            # self.dataCollection.buildPackData()
            # singleMosfetData.printAll()
        elif(msg.arbitration_id == self.stm32CurrentFrame) : #if the can message frame is stm32 data frame
            dataProcess = DataProcess()
            stm32Current1 = Stm32Current()
            stm32SingleData = SingleStm32Data()
            stm32SingleData.firmwareVersion = msg.data[0]
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
            # self.dataCollection.buildStm32Data()
            print("stm32 current data updated")
        elif(msg.arbitration_id == self.stm32LowVoltageParamFrame) : #if the can message frame is low voltage param frame
            self.dataCollection.lowVoltageVsat = (msg.data[1] << 8) + msg.data[0]
            self.dataCollection.lowVoltageOther = (msg.data[3] << 8) + msg.data[2]
            self.dataCollection.lowVoltageBts = (msg.data[5] << 8) + msg.data[4]
            print("stm32 low voltage parameter updated")
        elif(msg.arbitration_id == self.stm32ReconnectVoltageParamFrame) : #if the can message frame is reconnect voltage param frame
            self.dataCollection.reconnectVoltageVsat = (msg.data[1] << 8) + msg.data[0]
            self.dataCollection.reconnectVoltageOther = (msg.data[3] << 8) + msg.data[2]
            self.dataCollection.reconnectVoltageBts = (msg.data[5] << 8) + msg.data[4]
            print("stm32 reconnect voltage parameter updated")
        # self.lock.release()
