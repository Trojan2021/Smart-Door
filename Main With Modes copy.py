#Facial Recogntion with Door

import os
import time
import tkinter as tk

import cv2
import face_recognition
import numpy as np
import pigpio
import RPi.GPIO as GPIO
from bluedot import BlueDot
from PIL import Image, ImageTk

#Variable Initialization
#All global variable are used to control the states the of different modes independently
global Bean
Bean = True
global letgo
letgo = False
global beenRun
beenRun = False
global cool
cool = False
global timestart
timestart = 0
global btPressed
btPressed = False
global cPressed
cPressed = False

# Servos Setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
Deadbolt = 19
Handle = 26
pwm = pigpio.pi()
pwm.set_mode(Deadbolt, pigpio.OUTPUT)
pwm.set_mode(Handle, pigpio.OUTPUT)
pwm.set_PWM_frequency(Deadbolt, 50)
pwm.set_PWM_frequency(Handle, 50)

# Deadbolt Servo Setup
DOpen = 1750
DClosed = 2500

def DeadOpen():
    pwm.set_servo_pulsewidth(Deadbolt, DOpen)

def DeadClosed():
    pwm.set_servo_pulsewidth(Deadbolt, DClosed)

# Handle Servo Setup
HOpen = 800
HClosed = 1500

def HandleOpen():
    pwm.set_servo_pulsewidth(Handle, HOpen)

def HandleClosed():
    pwm.set_servo_pulsewidth(Handle, HClosed)

# Motor Setup

RELAYONE = 17
RELAYTWO = 27

GPIO.setup(RELAYONE, GPIO.OUT)
GPIO.setup(RELAYTWO, GPIO.OUT)
GPIO.output(RELAYONE, GPIO.HIGH)
GPIO.output(RELAYTWO, GPIO.HIGH)

def MotorOpen():
    GPIO.output(RELAYTWO, GPIO.LOW)

def MotorClose():
    GPIO.output(RELAYONE, GPIO.LOW)

def MotorStop():
    GPIO.output(RELAYTWO, GPIO.HIGH)
    GPIO.output(RELAYONE, GPIO.HIGH)

# LED Setup

RED = 5
GREEN = 6
GPIO.setup(RED, GPIO.OUT)
GPIO.output(RED, True)
GPIO.setup(GREEN, GPIO.OUT)
GPIO.output(GREEN, False)


def GreenOn():
    GPIO.setup(RED, GPIO.OUT)
    GPIO.output(RED, True)
    GPIO.setup(GREEN, GPIO.OUT)
    GPIO.output(GREEN, False)


def RedOn():
    GPIO.setup(RED, GPIO.OUT)
    GPIO.output(RED, False)
    GPIO.setup(GREEN, GPIO.OUT)
    GPIO.output(GREEN, True)

def actuateDoor():
    global cool
    global timestart
    if cool == False:
        timestart = time.time()
        cool = True


def Face():
    global Bean
    global letgo
    global beenRun
    beenRun = True

    if Bean:

        startFace['text'] = "Stop Recognition"

        Bean = False

        # Video capture
        video_capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)

        known_face_encodings = []
        known_face_names = []

        # Adding people's names and faces to lists
        dir_path = 'Encodings'
        count = 0
        # Iterate directory
        for path in os.listdir(dir_path):

            if os.path.isfile(os.path.join(dir_path, path)):
                count += 1
                face_encoding = np.loadtxt((dir_path + "/" + path), dtype = float)
                known_face_encodings.append(face_encoding)
                known_face_names.append(path[0:-4])

        # Initializing arrays/variables
        face_locations = []
        face_encodings = []
        face_names = []
        process_this_frame = True

        while True:

            # Release handle to the webcam
            if letgo:
                video_capture.release()
                letgo = False
                break

            # Analyzing frame
            ret, frame = video_capture.read()

            # Scaling for performance
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25, interpolation = cv2.INTER_CUBIC)

            # Converting BRG to RGB
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

            if process_this_frame:

                # Finds a face
                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

                face_names = []

                for face_encoding in face_encodings:

                    # Matches a face
                    matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                    name = "Unknown"

                    # Or instead, use the known face with the smallest distance to the new face
                    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)

                    if matches[best_match_index]:
                        name = known_face_names[best_match_index]

                        #Door Control
                        actuateDoor()

                    face_names.append(name)

            process_this_frame = not process_this_frame

            for (top, right, bottom, left), name in zip(face_locations, face_names):
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                # Box
                cv2.rectangle(frame, (left, top), (right, bottom), (255, 0, 255), 2)

                # Dname
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (255, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

            # Display
            blue,green,red = cv2.split(frame)
            c = cv2.merge((red,green,blue))
            co = Image.fromarray(c)
            coo = ImageTk.PhotoImage(image=co)
            picture.configure(image=coo)
            window.update()
    else:
        letgo = True
        Bean = True
        startFace['text'] = "Start Recognition"
        picture.configure(image=img)
        window.update()

def btToggle():
    global cool
    global timestart
    global btPressed

    if not btPressed:

        btPressed = True
        bt['text'] = "Stop Bluetooth"
        window.update()
        bd = BlueDot()
        BlueDot.start()
        while True:

            if (bd.is_pressed == True):
                actuateDoor()
            if not btPressed:
                break
    else:
        btPressed = False
        BlueDot.stop()
        bt['text'] = "Start Bluetooth"
        window.update()

def CloseProgram():
    global beenRun
    global letgo
    global cPressed
    global btPressed
    cPressed = True
    control()
    btPressed = True
    btToggle()
    if beenRun:
        letgo = True
        Face()
    window.destroy()

def control():
    global cool
    global timestart
    global cPressed

    if not cPressed:
        cPressed = True
        cb['text'] = "Stop Controls"
        while True:

            if cool == True:
                GreenOn()
                timenow = time.time()
                dtime = timenow - timestart
                print(dtime)
                if dtime < 2:
                    DeadOpen()
                    HandleOpen()
                if dtime > 2 and dtime < 4.25:
                    MotorOpen()
                if dtime > 4.25 and dtime < 6.25:
                    HandleClosed()
                    MotorStop()
                if dtime > 6.25 and dtime < 10.25:
                    MotorClose()
                if dtime > 10.25:
                    DeadClosed()
                    MotorStop()
                    RedOn()
                    cool = False
            else:
                HandleClosed()
                DeadClosed()
                RedOn()
            if not cPressed:
                break
    else:
        cPressed = False
        cb['text'] = "Start Controls"
        window.update()





window = tk.Tk()

global img
img = ImageTk.PhotoImage(Image.open('Media/Notyet.jpg'))

picture = tk.Label(
    image=img
)
picture.pack()

bean = tk.Label(
    text="Facial Recogntion Tester\n(This program only does facial recongiton\nand does not control the door)"
)
bean.pack()

warning = tk.Label(
    text="Facial Detection, Bluetooth, and the\ndoor toggle below will not work unless\nthe controls have been turned on"
)
warning.pack()

doorToggle = tk.Button(
    text="Toggle Door Actuation",
    command=actuateDoor
)
doorToggle.pack()

toggle = tk.Label(
    text="This will tell the door to open at any point"
)
toggle.pack()

startFace = tk.Button(
    text="Start Recognition",
    command=Face
)
startFace.pack()

sf = tk.Label(
    text="This will toggle facial recognition"
)
sf.pack()

bt = tk.Button(
    text="Start Bluetooth",
    command=btToggle
)
bt.pack()

bl = tk.Label(
    text="This will toggle the bluetooth"
)
bl.pack()

cb = tk.Button(
    text="Start Controls",
    command=control
)
cb.pack()

cl = tk.Label(
    text="This will toggle the controls"
)
cl.pack()

close = tk.Button(
    text="Close",
    command=CloseProgram
)
close.pack()

window.title("Facial Detection")

window.mainloop()
