import face_recognition
import numpy as np

bret_image = face_recognition.load_image_file("Hayden.jpg")
bret_face_encoding = face_recognition.face_encodings(bret_image)[0]

np.savetxt("Hayden_Encoding.txt", bret_face_encoding, delimiter = ", ")