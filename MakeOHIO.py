import time

import cv2
import face_recognition
import numpy as np
import pigpio
import RPi.GPIO as GPIO
from bluedot import BlueDot

# Servo setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
Deadbolt = 19
Handle = 26
pwm = pigpio.pi() 
pwm.set_mode(Deadbolt, pigpio.OUTPUT)
pwm.set_mode(Handle, pigpio.OUTPUT)
pwm.set_PWM_frequency( Deadbolt, 50 )
pwm.set_PWM_frequency( Handle, 50 )

#Deadbolt
DOpen = 2000
DClosed = 2500

def DeadOpen():
    pwm.set_servo_pulsewidth(Deadbolt, DOpen)

def DeadClosed():
    pwm.set_servo_pulsewidth(Deadbolt, DClosed)
    
#Handle
HOpen = 800
HClosed = 1500

def HandleOpen():
    pwm.set_servo_pulsewidth(Handle, HOpen)
    
def HandleClosed():
    pwm.set_servo_pulsewidth(Handle, HClosed)
    

#LED Setup
RED = 5
GREEN = 3
GPIO.setup(RED, GPIO.OUT)
GPIO.output(RED, True)
GPIO.setup(GREEN, GPIO.OUT) 
GPIO.output(GREEN, False)

def GreenOn():
    GPIO.setup(RED, GPIO.OUT)
    GPIO.output(RED, False)
    GPIO.setup(GREEN, GPIO.OUT)
    GPIO.output(GREEN, True)
    
def RedOn():
    GPIO.setup(RED, GPIO.OUT)
    GPIO.output(RED, True)
    GPIO.setup(GREEN, GPIO.OUT)
    GPIO.output(GREEN, False)
    
bd = BlueDot(cols=3, rows=1)
bd[2,0].color = "red" # RED SHOULD BE FOR HANDLE
HANDLE = 2,0
bd[0,0].color = "blue" # BLUE SHOULD BE FOR DEADBOLT
DEADBOLT = 0,0
bd[1,0].visible = False # "REMOVES" MIDDLE BUTTON TO MAKE DISPLAY LOOK NICE

# Video capture
video_capture = cv2.VideoCapture(0)

# Photo database
bret_face_encoding = np.loadtxt("Bret_Encoding.txt", dtype = float)

michael_face_encoding = np.loadtxt("Michael_Encoding.txt", dtype = float)

hayden_face_encoding = np.loadtxt("Hayden_Encoding.txt", dtype = float)


known_face_encodings = [
    bret_face_encoding,
    michael_face_encoding,
    hayden_face_encoding,
]
known_face_names = [
    "Bret",
    "Michael",
    "Hayden",
]

# Initializing arrays/variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

while True:
    
    #Bluetooth
    
    bd[DEADBOLT].when_pressed = DeadOpen
    bd[HANDLE].when_pressed = HandleOpen
    time.sleep(1)
        
    # Analyzing frame
    ret, frame = video_capture.read()

    # Scaling for performance
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25, interpolation = cv2.INTER_CUBIC)

    # Converting RGB to BRG
    rgb_small_frame = small_frame[:, :, ::-1]
    
    if process_this_frame:
        
        # Finds a face
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        DeadClosed()
        HandleClosed()
        
        # LED settings
        RedOn()
        
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
                
                # Servo makes door open
                DeadOpen()
                HandleOpen()
                time.sleep(1)
                
                # LED settings
                GreenOn()
                
                # Slight delay before servo closes
                time.sleep(1)
         
            face_names.append(name)

    process_this_frame = not process_this_frame
    
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # box
        cv2.rectangle(frame, (left, top), (right, bottom), (255, 0, 255), 2)

        # Dname
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (255, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    # Display
    cv2.imshow('Video', frame)

    # Hit 'q' on the keyboard to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()
