import threading
import time
import DoorControl
import tkinter as tk
from bluedot import BlueDot
from PIL import Image, ImageTk
import cv2
import face_recognition
import numpy as np
import Jetson.GPIO as GPIO

# AFAICS only pins 32 and 33 are PWM capable on the Jetson Nano.
# And you need to run /opt/nvidia/jetson-io/jetson-io.py to enable PWM on those pins.

bean = DoorControl.Door("Beans")

GPIO.setmode(GPIO.BOARD)

# Start the bluetooth server and get BlueDot ready to be used
bd = BlueDot(cols=3, rows=1)
bd[0, 0].color = "blue"
bd[1, 0].visible = False
bd[2, 0].color = "red"


def doorTimer():
    while True:
        dtime = 0
        timestart = time.time()
        if not bean.doorState:
            if dtime < 2:
                bean.deadOpen()
                bean.handOpen()
                bean.deadOpen()

            if dtime > 2 and dtime < 3.5:
                bean.open()
            if dtime > 3.5 and dtime < 6.25:
                bean.handClose()
            if dtime > 6.25 and dtime < 10.25:
                bean.close()
            if dtime > 10.25:
                bean.doorState = not bean.doorState

def logic():
    while True:
        # Bluetooth
        # Checking to see if bluetooth is toggled on
        if bean.BTState:

            # If the red button on the app is being pressed then continue
            if bd[2, 0].is_pressed == True:
                bd[2, 0].when_released = Dead()
                # Open/Closes the Deadbolt
                # Dead()

            # If the blue button on the app is being pressed then continue
            if bd[0, 0].is_pressed == True:

                # Checking to see if the timer is not already running
                if cool == False:

                    # Setting a variable to the time the button was pressed
                    timestart = time.time()

                    # Ensuring the timer can't be run again until it is finished
                    cool = True


t = threading.Thread(target=doorTimer)
t.daemon = True
t.start()

window = tk.Tk()

img = ImageTk.PhotoImage(Image.open("Media/logo_with_text.jpg"))
picture = tk.Label(image=img)
picture.place(x=30, y=20)

warning = tk.Label(text="In order for the door to open the deadbolt must be open")
warning.place(x=130, y=505)

main = tk.Button(text="Start Face Recognition", height=3, font=30)
main.place(x=690, y=50)

window.mainloop()
