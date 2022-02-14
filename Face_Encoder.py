import face_recognition
import numpy as np

image = face_recognition.load_image_file("Hayden.jpg")
face_encoding = face_recognition.face_encodings(image)[0]

np.savetxt("Hayden_Encoding.txt", face_encoding, delimiter = ", ")