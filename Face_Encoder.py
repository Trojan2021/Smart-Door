#File to Encode Faces

import tkinter as tk
from tkinter import filedialog
import numpy as np
import face_recognition

filename = 0
def Beans():
    global filename
    filename = filedialog.askopenfilename()
    source.delete(0,"end")
    source.insert(0,filename)

def CompArray():
    image = face_recognition.load_image_file(source.get())
    face_encoding = face_recognition.face_encodings(image)[0]
    np.savetxt(name.get(), face_encoding, delimiter = ", ")

window = tk.Tk()

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
    text="Please enter the name of the person in the picture\n(Must be appended with .txt)"
)
askforname.pack()

name = tk.Entry()
name.pack()

compile = tk.Button(
    text="Compile Array",
    command=CompArray
)
compile.pack()

close = tk.Button(
    text="Close",
    command=window.destroy
)
close.pack()

window.mainloop()
