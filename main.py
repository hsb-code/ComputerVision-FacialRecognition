# cmake, dlib, face-recognition, cvzone, opencv-python
# importing libraries
import cv2
import os
import pickle
import face_recognition
import numpy as np
import cvzone
import firebase_admin
from firebase_admin import storage
from firebase_admin import db
from firebase_admin import credentials
from datetime import datetime

cred = credentials.Certificate(
    "add your database credentials")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'add your database url',
    'storageBucket': 'add your db storage bucket'})

bucket = storage.bucket()

# capturing the video
cap = cv2.VideoCapture(0)
cap.set(3, 640)  # 3 is the id for width
cap.set(4, 480)  # 4 is the id for height
# the part of background where our webcame will be shown in 640 by 480
# the complete background will be 1280 by 720

# background image
imbackground = cv2.imread(
    "add backgound image path")  # background image

# importing the mode images into a list
folderModePath = ("add mode images folder path")
modePathList = os.listdir(folderModePath)
imModeList = []

for path in modePathList:
    imModeList.append(cv2.imread(os.path.join(folderModePath, path)))

# print(len(imModeList))

# load the encoding file
print("Loading Encode File ...")
file = open('EncodeFile.p', 'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodeListKnownWithIds
print(studentIds)
print("Encode File Loaded")

# fetching the data from firebase
modeType = 0
counter = 0
id = -1
imgOwners = []

# video loop
while True:
    success, img = cap.read()  # img is the frame

    # resizing the image
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    # converting the image to RGB
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
    # finding the face locations
    faceCurFrame = face_recognition.face_locations(imgS)
    # finding the encodings
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    # img = cv2.flip(img, 1)
    imbackground[162:162+480, 55:55+640] = img  # rows and column
    imbackground[44:44+633, 808:808 +
                 414] = imModeList[modeType]  # rows and column

    # comparing the encodings
    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(
                encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(
                encodeListKnown, encodeFace)
            # print("matches", matches)
            # print("faceDis", faceDis)

            matchIndex = np.argmin(faceDis)
            # print("Match Index", matchIndex)
            if matches[matchIndex]:
                # print("Authorized Person Detected")
                # print(f'The Person ID is: {studentIds[matchIndex]}')
                y1, x2, y2, x1 = faceLoc  # extracting the coordinates
                # print(y1, x2, y2, x1)
                y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
                # drawing the rectangle around the face
                # top left x, top left y, width, height
                bbx = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                imbackground = cvzone.cornerRect(imbackground, bbx, rt=0)
                id = studentIds[matchIndex]

                if counter == 0:
                    cvzone.putTextRect(imbackground, "Loading", (275, 400))
                    cv2.imshow("Home Security", imbackground)
                    cv2.waitKey(1)
                    counter = 1
                    modeType = 1
            elif matches[matchIndex] == False:
                modeType = 4
                counter = 0
                imbackground[44:44+633, 808:808 + 414] = imModeList[modeType]

        if counter != 0:

            if counter == 1:
                # get the data
                ownerinfo = db.reference(f'Home Owners/{id}').get()
                print(ownerinfo)
                # get image from firebase storage
                blob = bucket.get_blob(
                    f'path{id}.jpg')
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imgOwners = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)

                # update datetime of verification
                datetimeobject = datetime.strptime(
                    ownerinfo['Last_Verification_Time'], '%Y-%m-%d %H:%M:%S')
                secondselapsed = (
                    datetime.now() - datetimeobject).total_seconds()
                print(secondselapsed)

                if secondselapsed > 30:
                    # update data of verification
                    ref = db.reference(f'Home Owners/{id}')
                    ownerinfo['Total_Verifications'] += 1
                    ref.child('Total_Verifications').set(
                        ownerinfo['Total_Verifications'])
                    ref.child('Last_Verification_Time').set(
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                else:
                    modeType = 3
                    counter = 0
                    imbackground[44:44+633, 808:808 +
                                 414] = imModeList[modeType]
            if modeType != 3:

                if 10 < counter < 20:
                    modeType = 2
                    imbackground[44:44+633, 808:808 +
                                 414] = imModeList[modeType]  # rows and column

                if counter <= 10:
                    # adding the data to the background image
                    cv2.putText(imbackground, str(ownerinfo['Total_Verifications']), (
                        861, 125), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
                    cv2.putText(imbackground, str(id), (1006, 493),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imbackground, str(ownerinfo['Authorization']), (
                                990, 550), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)

                    (w, h), _ = cv2.getTextSize(
                        ownerinfo['Name'], cv2.FONT_HERSHEY_PLAIN, 1, 1)
                    offset = (414 - w) // 2
                    cv2.putText(imbackground, str(
                        ownerinfo['Name']), (808+offset, 445), cv2.FONT_HERSHEY_PLAIN, 1, (50, 50, 50), 1)

                    imbackground[175:175+216, 909:909+216] = imgOwners
                counter += 1
                if counter >= 20:
                    counter = 0
                    modeType = 0
                    ownerinfo = []
                    imgOwners = []
                    imbackground[44:44+633, 808:808 +
                                 414] = imModeList[modeType]
    else:
        modeType = 0
        counter = 0
        # else:
        #     print("Unknown Person Detected")

    # showing the cam with background
    cv2.imshow("Home Security", imbackground)
    # cv2.imshow("Home Security", img) #showing simple camk
    cv2.waitKey(1)  # 1ms delay
