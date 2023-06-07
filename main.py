import threading
import queue
import keyboard
from dataproviderthread import DataProvider
from datareaderthread import DataReader, DataCollection
from time import sleep
from httpserver import Server

if __name__ == "__main__":
    readerStopEvent = threading.Event()
    providerStopEvent = threading.Event()
    syncFlag = threading.Condition()
    data = DataCollection()   
    buffer = queue.Queue()
    reader = DataReader(name="datareader", stopEvent=readerStopEvent, syncFlag=syncFlag, buffer=buffer)
    data = reader.dataCollection
    provider = DataProvider(name="dataprovider", stopEvent=providerStopEvent, syncFlag=syncFlag, buffer=buffer)
    server = Server(name="httpserver", data=data)    
    server.link(provider.writeQueue)
    reader.start()
    provider.start()
    server.start()
    # stopEvent = threading.Event()
    # buffer = queue.Queue()
    # canBus = CanBus("canbus", stopEvent)
    # canBus.configureBus(interface="socketcan", channel="can0", bitrate=250000)
    # canBus.setBuffer(queue=buffer)
    # canBus.daemon = True
    # canBus.start()
    while True :
        if keyboard.is_pressed("q") :
            print("you pressed q")
            break
        sleep(0.1)
    readerStopEvent.set()
    providerStopEvent.set()
    print("Quit")
    # stopEvent.set()

