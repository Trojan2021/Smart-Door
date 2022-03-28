#Facial Recogntion w/o Door

import os
import tkinter as tk

import cv2
import face_recognition
import numpy as np
from PIL import Image, ImageTk
from sys import platform

global Bean
Bean = True
global letgo
letgo = False
global beenRun
beenRun = False

def Face():

    global Bean
    global letgo
    global beenRun
    beenRun = True

    if Bean:

        startFace['text'] = "Stop Recognition"

        Bean = False

        # Video capture
        if platform == "linux":
            video_capture = cv2.VideoCapture(0)
        elif platform == "win32":
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
        perfCount = 0

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

            if perfCount == 0:

                perfCount = 5

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

                    face_names.append(name)

            perfCount -= 1


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

def CloseProgram():
    global beenRun
    global letgo
    if beenRun:
        letgo = True
        Face()
    window.destroy()


window = tk.Tk()

window.geometry('1024x600')

# If on the Pi go fullscreen
if platform == "linux":
    window.attributes('-fullscreen', True)


global img
img = ImageTk.PhotoImage(Image.open('Media/logo_with_text.jpg'))

picture = tk.Label(
    image=img
)
picture.place(x=30, y = 20)

bean = tk.Label(
    text="Facial Recogntion Tester\n(This program only does facial recongiton and does not control the door)"
)
bean.place(x=150, y=505)

startFace = tk.Button(
    text="Start Recognition",
    command=Face,
    height=10,
    width=25,
    font=30
)
startFace.place(x=690, y=20)

close = tk.Button(
    text="Close",
    command=CloseProgram,
    height=10,
    width=25,
    font=30
)
close.place(x=690, y=320)

window.title("Facial Detection")

window.mainloop()
