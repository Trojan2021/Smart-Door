#Main File To Run Door

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

cool = False
timestart = 0


# Bluetooth Setup
bd = BlueDot()

# Video capture
video_capture = cv2.VideoCapture(0)

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

        # Bluetooth
        if (bd.is_pressed == True):
            if cool == False:
                timestart = time.time()
                cool = True

        # Analyzing frame
        ret, frame = video_capture.read()

        # Scaling for performance
        small_frame = cv2.resize(
            frame, (0, 0), fx=0.25, fy=0.25, interpolation=cv2.INTER_CUBIC)

        # Converting RGB to BRG
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        if process_this_frame:

            # Finds a face
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            # LED settings

            face_names = []

            for face_encoding in face_encodings:

                # Matches a face
                matches = face_recognition.compare_faces(
                    known_face_encodings, face_encoding)
                name = "Unknown"

                # Or instead, use the known face with the smallest distance to the new face
                face_distances = face_recognition.face_distance(
                    known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)

                if matches[best_match_index]:
                    name = known_face_names[best_match_index]

                    # LED settings
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

            # box
            cv2.rectangle(frame, (left, top),
                          (right, bottom), (255, 0, 255), 2)

            # Dname
            cv2.rectangle(frame, (left, bottom - 35),
                          (right, bottom), (255, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6),
                        font, 1.0, (255, 255, 255), 1)

        # Display
        cv2.imshow('Video', frame)


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

        # Hit 'q' on the keyboard to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()
