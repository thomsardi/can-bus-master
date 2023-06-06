import threading
import queue
from dataproviderthread import CanDataSimulator
from time import sleep

class DataReader(threading.Thread) :
    def __init__(self, stopEvent : threading.Event, syncFlag : threading.Condition, buffer : queue.Queue) :
        threading.Thread.__init__(self)
        self.stopEvent : threading.Event = stopEvent
        self.syncFlag = syncFlag
        self.buffer : queue.Queue = buffer
        self.daemon = True

    def read(self) :
        if self.stopEvent.is_set() : 
            return
        with self.syncFlag :
            self.syncFlag.wait()
            print("available")
        while not self.buffer.empty() :
            try :
                canData : CanDataSimulator = self.buffer.get()
                print("Frame Id :", hex(canData.arbitration_id))
                print("Length :", canData.dlc)
                toPrint : str = ""
                for x in canData.data:
                    toPrint += hex(x)
                    toPrint += " "
                print("Data :", toPrint)
            except :
                print("timeout")
                pass
        # else :
        #     print("buffer empty")
        #     sleep(0.1)
        #     pass

    def run(self) :
        while not self.stopEvent.is_set() :
            self.read()
            