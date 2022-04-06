#!/usr/bin/env python

#Main v1.3
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

# Start the bluetooth server and get BlueDot ready to be used
bd = BlueDot(cols = 3, rows = 1)
bd[0,0].color = "blue"
bd[1,0].visible = False
bd[2,0].color = "red"

# Servos Setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
# Setting pins to variables
Deadbolt = 19
Handle = 26
# You can't use GPIO for servo because it causes jittering
pwm = pigpio.pi()
pwm.set_mode(Deadbolt, pigpio.OUTPUT)
pwm.set_mode(Handle, pigpio.OUTPUT)
pwm.set_PWM_frequency(Deadbolt, 50)
pwm.set_PWM_frequency(Handle, 50)

# Setting where the servos need to turn to for the deadbolt
DOpen = 1675
DClosed = 2500

def DeadOpen():
    pwm.set_servo_pulsewidth(Deadbolt, DOpen)

def DeadClosed():
    pwm.set_servo_pulsewidth(Deadbolt, DClosed)

# Setting where the servos need to turn to open the handle
HOpen = 1200
HClosed = 1750

def HandleOpen():
    pwm.set_servo_pulsewidth(Handle, HOpen)

def HandleClosed():
    pwm.set_servo_pulsewidth(Handle, HClosed)

# Motor Setup
# Setting pins for relay

# H-Bridge Relays
RELAYONE = 17
RELAYTWO = 27

# Relays to allow for manual operation of door (Turning servos off)
DEADRELAY = 22
HANDLERELAY = 23

GPIO.setup(RELAYONE, GPIO.OUT)
GPIO.setup(RELAYTWO, GPIO.OUT)
GPIO.setup(DEADRELAY, GPIO.OUT)
GPIO.setup(HANDLERELAY, GPIO.OUT)
GPIO.output(RELAYONE, GPIO.HIGH)
GPIO.output(RELAYTWO, GPIO.HIGH)
GPIO.output(DEADRELAY, GPIO.HIGH)
GPIO.output(HANDLERELAY, GPIO.HIGH)

def MotorOpen():
    GPIO.output(RELAYTWO, GPIO.LOW)

def MotorClose():
    GPIO.output(RELAYONE, GPIO.LOW)

def MotorStop():
    GPIO.output(RELAYTWO, GPIO.HIGH)
    GPIO.output(RELAYONE, GPIO.HIGH)

def DeadOn():
    GPIO.output(DEADRELAY, GPIO.LOW)

def DeadOff():
    GPIO.output(DEADRELAY, GPIO.HIGH)

def HandleOn():
    GPIO.output(HANDLERELAY, GPIO.LOW)

def HandleOff():
    GPIO.output(HANDLERELAY, GPIO.HIGH)

# LED Setup
# Pins for LEDs
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
        # Telling which folder to search in for encodings
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
        perfCount = 0

        # Run while Main is toggled on
        while not overall:

            # Bluetooth
            # Checking to see if bluetooth is toggled on
            if btOn:

                # If the red button on the app is being pressed then continue
                if (bd[2,0].is_pressed == True):
                    bd[2,0].when_released = Dead()
                    # Open/Closes the Deadbolt
                    #Dead()

                # If the blue button on the app is being pressed then continue
                if (bd[0,0].is_pressed == True):

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

                # If the performance counter is 0 then check the frame for faces
                if perfCount == 0:

                    # Set performance counter back up so it waits through 5 frames
                    perfCount = 5

                    # Finds the location of a face in the frame if there is one
                    face_locations = face_recognition.face_locations(rgb_small_frame)

                    # Makes an encoding of a face if it finds one
                    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

                    # Initialize a list for the names of the faces it found if any
                    face_names = []

                    # Test each encoded face against the person in the frame
                    for face_encoding in face_encodings:

                        # Compare encoded faces with the new encodings that were made from the frame
                        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                        name = "Unknown"

                        # Use a tolerance check on the faces found
                        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                        best_match_index = np.argmin(face_distances)

                        if matches[best_match_index]:

                            # Set the name of the known face to the name that will be used in the frame
                            name = known_face_names[best_match_index]

                            #Door Control
                            if cool == False:
                                timestart = time.time()
                                cool = True

                        # Set this name to the list to used in the final frame
                        face_names.append(name)

                # Decrement perfCount so that it counts back down to 0
                perfCount -= 1

                for (top, right, bottom, left), name in zip(face_locations, face_names):

                    # Aligning the location of face to the unscaled frame
                    top *= 4
                    right *= 4
                    bottom *= 4
                    left *= 4

                    # Drawing a box around the face dound
                    cv2.rectangle(frame, (left, top), (right, bottom), (255, 0, 255), 2)

                    # Drawing the name box
                    cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (255, 0, 255), cv2.FILLED)

                    # Font used
                    font = cv2.FONT_HERSHEY_DUPLEX

                    # Drawing the name in the name box
                    cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

                # Display
                # Rearrange the array from BGR to RGB
                blue,green,red = cv2.split(frame)
                c = cv2.merge((red,green,blue))
                co = Image.fromarray(c)

                # Configure the image for Tkinter
                coo = ImageTk.PhotoImage(image=co)

                # Update picture in Tkinter to use the read in frame
                picture.configure(image=coo)
            elif letGo:

                # Set letGo to False so it is ready to be toggled again
                letGo = False

                # Update picture to hold our logo
                picture.configure(image=img)

            # Control of Door

            # If the controls are told to turn on (cool) or the controls are told to stay on past DeadBolt
            if (cool == True and not DeadBolt) or Beans:

                # Variable to ensure this loop continues to run if DeadBolt is toggled
                Beans = True

                # Set LEDs to green to say door is open
                GreenOn()

                # Check the current time
                timenow = time.time()

                # Take the time from the system that toggled the controls and subtract from the current time to run a timer
                dtime = timenow - timestart

                # Prints the amount of time that has passed (uncomment for use)
                print(dtime)

                # dtime is the timer so open, stop, close, stop
                if dtime < 2:
                    DeadOn()
                    HandleOn()
                    DeadOpen()
                    HandleOpen()
                if dtime > 2 and dtime < 3.5:
                    MotorOpen()
                if dtime > 3.5 and dtime < 6.25:
                    HandleClosed()
                    MotorStop()
                if dtime > 6.25 and dtime < 10.25:
                    MotorClose()
                if dtime > 10.25:
                    MotorStop()
                    RedOn()

                    cool = False
                    Beans = False

            # If the DeadBolt is Flase then allow for the door to be opened manually with the handle
            elif not DeadBolt:
                DeadOpen()
                GreenOn()
                HandleClosed()
                DeadOff()
                HandleOff()

            # If nothing above is true keep the door handle and deadbolt closed
            else:
                HandleClosed()
                DeadClosed()
                RedOn()
                DeadOff()
                HandleOff()

                # Prep the timer to be used again
                cool = False

            # this try statement is here because when the GUI is closed sometimes it closes before this statement is done
            try:

                # Updates the GUI with all changed that have been made
                window.update()

            # This is to make the try work
            except:
                cool_beans = False

    # If Main has been called before go here
    else:

        # Prep main to be run again
        overall = True

        # Toggle everything off and update the GUI
        btOn = False
        bluetooth['text'] = "Start Bluetooth"
        faceOn = False
        fr['text'] = "Start Facial Recognition"
        main['text'] = "Start Program"
        DeadBolt = True
        dead['text'] = "Open Deadbolt"

        # Update the image displayed to be the logo
        picture.configure(image=img)

        # Updates the GUI with the changes
        window.update()


# Toggle Bluetooth
def btToggle():
    global btOn
    if btOn:
        btOn = False
        bluetooth['text'] = "Start Bluetooth"
    elif not btOn:
        btOn = True
        bluetooth['text'] = "Stop Bluetooth"
    window.update()

# Toggle Facial Reecognition
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

# Toggle the deadbolt
def Dead():
    DeadOn()
    global DeadBolt
    if DeadBolt:
        DeadBolt = False
        DeadOpen()
        dead['text'] = "Close Deadbolt"
    elif not DeadBolt:
        DeadBolt = True
        DeadClosed()
        dead['text'] = "Open Deadbolt"
    time.sleep(0.5)
    DeadOff()

# Close the program
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


# Define the Tkinter GUI as window
window = tk.Tk()

#Setting the window size for the pi
window.geometry('1024x600')

# If on the Pi go fullscreen
if platform == "linux":
    window.attributes('-fullscreen', True)

# Setting up the logo to be used
global img
img = ImageTk.PhotoImage(Image.open('Media/logo_with_text.jpg'))

# The display of the program
picture = tk.Label(
    image=img
)
picture.place(x=30, y = 20)

# Display the deadbolt warning
warning = tk.Label(
    text="In order for the door to open the deadbolt must be open"
)
warning.place(x=130, y=505)

# The button that toggles the program
main = tk.Button(
    text="Start Program",
    command=Main,
    height=3,
    font=30
)
main.place(x=690, y=50)

# The button that toggles the deadbolt
dead = tk.Button(
    text="Open Deadbolt",
    command=Dead,
    height=3,
    font=30
)
dead.place(x=690, y=150)

# The button that toggles Bluetooth
bluetooth = tk.Button(
    text="Start Bluetooth",
    command=btToggle,
    height=3,
    font=30
)
bluetooth.place(x=690, y=250)

# The button that toggles facial recognition
fr = tk.Button(
    text="Start Facial Recognition",
    command=faceToggle,
    height=3,
    font=30
)
fr.place(x=690, y=350)

# The button that closes the program
close = tk.Button(
    text="Close",
    command=Close,
    height=3,
    font=30
)
close.place(x=690, y=450)

# Setting the title of the GUI that displpays
window.title("Smart Door Control")

# Starting the GUI
window.mainloop()
