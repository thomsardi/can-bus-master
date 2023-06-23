import sys
import threading
import queue
import os
# import keyboard
import can
from cancallback import CanCallBack
from dataproviderthread import DataProvider
from cancallback import DataCollection
# from datareaderthread import DataReader, DataCollection
from time import sleep
from httpserver import Server
from can.bus import BusABC

def get_platform():
    platforms = {
        'linux1' : 'Linux',
        'linux2' : 'Linux',
        'linux' : "Linux",
        'darwin' : 'OS X',
        'win32' : 'Windows'
    }
    if sys.platform not in platforms:
        return sys.platform
    
    return platforms[sys.platform]

if __name__ == "__main__":
        
    if(get_platform() == "Linux") :
        print("Initialize CAN bus")
        try :
            os.system('sudo ip link set can0 type can bitrate 250000')
            os.system('sudo ifconfig can0 up')
        except :
            print("Failed")
            pass
    else :
        print("Operating system is not Linux")
        print("Failed to setup CAN")
        print("Exit")
        exit()

    syncFlag = threading.Condition()
    data = DataCollection()   
    buffer = queue.Queue()
    canFilter = [
        {"can_id": 0x540C840, "can_mask": 0x5D8FF40, "extended": True}
    ]
    bus = can.ThreadSafeBus(interface='socketcan', channel='can0', receive_own_messages=False)
    bus.set_filters(filters=canFilter)
    listCallback = []
    canCallBack = CanCallBack()
    listCallback.append(canCallBack)
    # reader = DataReader(name="datareader", stopEvent=readerStopEvent, syncFlag=syncFlag, buffer=buffer)
    provider = DataProvider(name="dataprovider", syncFlag=syncFlag, buffer=buffer)
    provider.initBus(bus)
    provider.setListener(listCallback)
    data = canCallBack.dataCollection
    server = Server(name="httpserver", data=data)    
    server.link(provider.writeQueue)
    # reader.start()
    provider.start()
    server.start()
    inc = 0
    while True :
        # if keyboard.is_pressed("q") :
        #     print("you pressed q")
        #     break
        if(inc > 50) :
            print("cleanup routine")
            # canCallBack.lock.acquire()
            data.cleanUp()
            # canCallBack.lock.release()
            inc = 0
        inc += 1
        sleep(0.1)
    # readerStopEvent.set()
    provider.stop()
    print("Quit")
    # stopEvent.set()

