# File to Encode Faces
# Do not run when the PI is attached to the touchscreen

import os
import tkinter as tk
from sys import platform
from tkinter import filedialog

import cv2
import face_recognition
import numpy as np
from PIL import Image, ImageTk

global cameraOn
cameraOn = False

filename = 0
def Beans():
    global filename
    filename = filedialog.askopenfilename(
        title="Open a JPG",
        filetypes=(("JPG Files", "*.jpg"), ("All Files", "*.*"))
    )
    source.delete(0,"end")
    source.insert(0,filename)

def CompArray():
    if source.get() == "From Picture":
        image = face_recognition.load_image_file("Media/tempfile.jpg")
        face_encoding = face_recognition.face_encodings(image)[0]
        np.savetxt(("Encodings/" + name.get()), face_encoding, delimiter = ", ")
    else:
        image = face_recognition.load_image_file(source.get())
        face_encoding = face_recognition.face_encodings(image)[0]
        np.savetxt(("Encodings/" + name.get()), face_encoding, delimiter = ", ")
    if os.path.exists("Media/tempfile.jpg"):
      os.remove("Media/tempfile.jpg")

def takePicture():

    global cameraOn
    global co

    if not cameraOn:

        cameraOn = True
        camera['text'] = "Take Picture"

        # Video capture
        if platform == "linux":
            video_capture = cv2.VideoCapture(0)
        elif platform == "win32":
            video_capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)

        while cameraOn:

            # Reading in the video
            ret, frame = video_capture.read()

            # Displaying the camera
            blue,green,red = cv2.split(frame)
            c = cv2.merge((red,green,blue))
            co = Image.fromarray(c)
            coo = ImageTk.PhotoImage(image=co)
            picture.configure(image=coo)
            window.update()


        cv2.imwrite("Media/tempfile.jpg", frame)

        video_capture.release()

        picture.configure(image=img)
        camera['text'] = "Open Camera"
        window.update()


    else:
        cameraOn = False
        source.delete(0,"end")
        source.insert(0,"From Picture")






window = tk.Tk()

global img
img = ImageTk.PhotoImage(Image.open('Media/logo_with_text.jpg'))

picture = tk.Label(
    image=img
)
picture.pack()

camera = tk.Button(
    text="Open Camera",
    command=takePicture
)
camera.pack()

bean = tk.Label(text="Please seclect the picture with a\n face that you would like to encode\n(*.jpg only)")
bean.pack()

source = tk.Entry()
source.pack()

button = tk.Button(
    text="Select Source",
    command=Beans
)
button.pack()

askforname = tk.Label(
    text="Please enter the name of the person in the picture\n(Must append name with .txt)"
)
askforname.pack()

name = tk.Entry()
name.pack()

compile = tk.Button(
    text="Compile Array",
    command=CompArray
)
compile.pack()

infostatement = tk.Label(
    text="Once you press the compile button it will stay down\nuntil the compiling is done"
)
infostatement.pack()

close = tk.Button(
    text="Close",
    command=window.destroy
)
close.pack()

window.title("Face Encoder")

window.mainloop()
