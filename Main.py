#Main v1.1.1 Beta
import os
import time
import tkinter as tk
from sys import platform

import cv2
import face_recognition
import numpy as np
import pigpio
import RPi.GPIO as GPIO
from bluedot import BlueDot
from PIL import Image, ImageTk

#Variable Initialization

global overall
overall = True
global btOn
btOn = False
global faceOn
faceOn = False
global letGo
letGo = False
global Deadbolt
DeadBolt = True

bd = BlueDot()

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

# Main function
# This is in a function because of Tkinter. With Tkinter it is able to be called while it is still running
# so with that the main is turned into a toggle for itself so it may be called again to turn itself off.

def Main():

    #Variable initialization for states and toggles
    global overall
    global btOn
    global faceOn
    global letGo
    global img
    global DeadBolt

    # Check to see if it has been run yet
    # If run then start prepping for door functions
    if overall:

        # Set overall to False so its ready to be called again for the toggle
        overall = False

        # Set cool to false to prep the timer in control so it can be turned on
        cool = False

        # Update GUI
        main['text'] = "Stop Program"

        # Ensure that the controls/counter continues to run to make sure the door is not stuck in an in between state
        Beans = False

        # Video capture
        # Check to see if the user is on linux or windows to capture video correctly
        if platform == "linux":
            video_capture = cv2.VideoCapture(0)
        elif platform == "win32":
            video_capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)

        # Initializing lists for facial recognition later
        known_face_encodings = []
        known_face_names = []

        # Adding people's names and faces to lists
        #Telling which folder to search in for encodings
        dir_path = 'Encodings'

        # The amount of files and folders in the directory
        for path in os.listdir(dir_path):

            # If the item is a file then read it in
            if os.path.isfile(os.path.join(dir_path, path)):

                # Load the file in and save to a variable
                face_encoding = np.loadtxt((dir_path + "/" + path), dtype = float)

                # Place the variable into a list
                known_face_encodings.append(face_encoding)

                # Take the name of the file and take off the .txt and use that as the name for the encoding
                known_face_names.append(path[0:-4])

        # Initializing arrays/variables
        face_locations = []
        face_encodings = []
        face_names = []
        process_this_frame = True

        # Run while Main is toggled on
        while not overall:

            # Bluetooth
            # Checking to see if bluetooth is toggled on
            if btOn:
                # If the button on the app is being pressed then continue
                if (bd.is_pressed == True):

                    # Checking to see if the timer is not already running
                    if cool == False:

                        # Setting a variable to the time the button was pressed
                        timestart = time.time()

                        # Ensuring the timer can't be run again until it is finished
                        cool = True

            # Face Recogntion
            # If Face is toggled on and not being told to let go of video stream then continue
            if faceOn and not letGo:
                # Taking in a frame from the video to checked for faces
                ret, frame = video_capture.read()

                # Resizing the frame to be a quarter of normal size for performance
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25, interpolation = cv2.INTER_CUBIC)

                # Converting BGR array to RGB array
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
                            if cool == False:
                                timestart = time.time()
                                cool = True

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
            elif letGo:
                letGo = False
                picture.configure(image=img)

            #Control of Door
            if (cool == True and not DeadBolt) or Beans:
                Beans = True
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
                    MotorStop()
                    RedOn()
                    cool = False
                    Beans = False
            elif not DeadBolt:
                DeadOpen()
            else:
                HandleClosed()
                DeadClosed()
                RedOn()
                cool = False
            try:
                window.update()
            except:
                cool_beans = False
    else:
        overall = True

        btOn = False
        bluetooth['text'] = "Start Bluetooth"
        faceOn = False
        fr['text'] = "Start Facial Recognition"
        main['text'] = "Start Program"
        DeadBolt = True
        dead['text'] = "Open Deadbolt"
        picture.configure(image=img)

        window.update()


def btToggle():
    global btOn
    if btOn:
        btOn = False
        bluetooth['text'] = "Start Bluetooth"
    elif not btOn:
        btOn = True
        bluetooth['text'] = "Stop Bluetooth"
    window.update()

def faceToggle():
    global faceOn
    global letGo
    if faceOn:
        faceOn = False
        letGo = True
        fr['text'] = "Start Facial Recognition"
    elif not faceOn:
        faceOn = True
        fr['text'] = "Stop Facial Recognition"
    window.update()

def Dead():
    global DeadBolt
    if DeadBolt:
        DeadBolt = False
        dead['text'] = "Close Deadbolt"
    elif not DeadBolt:
        DeadBolt = True
        dead['text'] = "Open Deadbolt"

def Close():
    global btOn
    global faceOn
    global overall
    global letGo
    letGo = True
    btOn = False
    faceOn = False
    overall = True
    window.destroy()


window = tk.Tk()

global img
img = ImageTk.PhotoImage(Image.open('Media\logo_with_text.jpg'))

picture = tk.Label(
    image=img
)
picture.pack()

warning = tk.Label(
    text="In order for the door to open the deadbolt must be open"
)
warning.pack()

main = tk.Button(
    text="Start Program",
    command=Main
)
main.pack()

dead = tk.Button(
    text="Open Deadbolt",
    command=Dead
)
dead.pack()

bluetooth = tk.Button(
    text="Start Bluetooth",
    command=btToggle
)
bluetooth.pack()

fr = tk.Button(
    text="Start Facial Recognition",
    command=faceToggle
)
fr.pack()

close = tk.Button(
    text="Close",
    command=Close
)
close.pack()

window.title("Smart Door Control")

window.mainloop()
