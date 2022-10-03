import threading
import time
import DoorControl

bean = DoorControl.Door("Beans")


def worker():
    while True:
        dtime = 0
        timestart = time.time()
        if not bean.state:
            print(1)
            while dtime < 5:
                timenow = time.time()
                dtime = timenow - timestart
            bean.close()
            print(0)


t = threading.Thread(target=worker)
t.daemon = True
t.start()

while True:
    cool = input("Open or close?")
    if cool == "open":
        bean.open()
    elif cool == "close":
        bean.close()
