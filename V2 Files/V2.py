import threading
import time
import DoorControl
import tkinter as tk
from PIL import Image, ImageTk

bean = DoorControl.Door("Beans")


def doorTimer():
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


t = threading.Thread(target=doorTimer)
t.daemon = True
t.start()

img = ImageTk.PhotoImage(Image.open("Media/logo_with_text.jpg"))
picture = tk.Label(image=img)
picture.place(x=30, y=20)

warning = tk.Label(text="In order for the door to open the deadbolt must be open")
warning.place(x=130, y=505)

main = tk.Button(text="Start Face Recognition", command=, height=3, font=30)
main.place(x=690, y=50)

window = tk.Tk()
