from dataproviderthread import DataProvider, CanDataSimulator
from datareaderthread import DataReader
import queue
import threading
import keyboard
from time import sleep

if __name__ == "__main__":
    readerStopEvent = threading.Event()
    providerStopEvent = threading.Event()
    syncFlag = threading.Condition()
    buffer = queue.Queue()
    reader = DataReader(stopEvent=readerStopEvent, syncFlag=syncFlag, buffer=buffer)
    provider = DataProvider(stopEvent=providerStopEvent, syncFlag=syncFlag, buffer=buffer)
    reader.start()
    provider.start()
    while True :
        if keyboard.is_pressed("q") :
            print("you pressed q")
            break
        sleep(0.1)
    readerStopEvent.set()
    providerStopEvent.set()
    print("Quit")
        