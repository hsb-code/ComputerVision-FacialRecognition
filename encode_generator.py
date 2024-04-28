import cv2
import pickle
import face_recognition
import os
import firebase_admin
from firebase_admin import storage
from firebase_admin import db
from firebase_admin import credentials

cred = credentials.Certificate(
    "add your database credentials")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'add your database url',
    'storageBucket': 'add your db storage bucket'})

# importing the images of house owners
folderPath = ("path to images")
PathList = os.listdir(folderPath)
imgList = []
ownerIds = []  # list of ids of owners

for path in PathList:
    imgList.append(cv2.imread(os.path.join(folderPath, path)))
    os.path.splitext(path)[0]
    # this will give the name of the image without extension
    ownerIds.append(os.path.splitext(path)[0])

    # uploading the images to firebase storage
    fileName = f'{folderPath}/{path}'
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)

print(ownerIds)
print(len(imgList))

# generate encodings


def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)

    return encodeList


print("Encoding Started ...")
encodeListKnown = findEncodings(imgList)
encodeListKnownWithIds = [encodeListKnown, ownerIds]
print(encodeListKnown)
print("Encoding Complete")

# Serialization is the process of converting a data structure or object into
# a format that can be easily stored, transmitted, or reconstructed later.
file = open("EncodeFile.p", 'wb')  # opening file in binary mode
# dumping/serializing the data into the file
pickle.dump(encodeListKnownWithIds, file)
file.close()
print("File Saved")
