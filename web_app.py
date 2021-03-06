import cv2
import numpy as np
import pandas as pd
import streamlit as st
import face_recognition
import os
import io
from PIL import Image
from datetime import datetime
import warnings
from dataset_maker import enroll_new_entry

warnings.filterwarnings("ignore")


path = 'images'
images = []
personNames = []
myList = os.listdir(path)

for cu_img in myList:
    current_Img = cv2.imread(f'{path}/{cu_img}')
    images.append(current_Img)
    personNames.append(os.path.splitext(cu_img)[0])



def faceEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

def attendance(name):
    with open('Attendance.csv','r+') as f:

    	#read file line by line
        myDataList = f.readlines()
        nameList = [[],[]]
        dateList = []

        #iterate over each line
        for line in myDataList:

            #split with comma
            entry = line.split(',')

            #after splitting extarct name for each line and append it to list of names
            nameList.append(entry[0])
            
        now = datetime.now()
        tStr = now.strftime('%H:%M:%S')
        dtString = now.strftime('%d:%m:%Y')
        f.writelines(f'\n{name},{tStr},{dtString}')
        
        
encodeListKnown = faceEncodings(images)

def main():
    """Smart Attendance System"""

    st.title("Streamlit")

    html_temp = """
    <body style="background-color:#F2FDFC;">
    <div style="background-color:#54095A ;padding:4px">
    <h1 style="font-family:'sans-serif';color:white;font-size: 38px;text-align:center;">Attendance using Face Recognition</h2>
    </div>
    <br>
    </body>
    """
    st.markdown(html_temp, unsafe_allow_html=True)
    st.set_option('deprecation.showfileUploaderEncoding', False)

    if st.button("New Registration"):
        enroll_new_entry()



    if st.button("Check your Attendance here !!"):
        attendancefile = pd.read_csv("Attendance.csv")
        st.write(attendancefile)

    if st.button('Mark your attendance'):
        cap = cv2.VideoCapture(0)
        count =1
        while (count<2):
            #read from video and return success status and image
            ret, frame = cap.read()
            count=count+1
            faces = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
            faces = cv2.cvtColor(faces, cv2.COLOR_BGR2RGB)

            facesCurrentFrame = face_recognition.face_locations(faces)
            encodesCurrentFrame = face_recognition.face_encodings(faces, facesCurrentFrame)

            for encodeFace, faceLoc in zip(encodesCurrentFrame, facesCurrentFrame):
                matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
                faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
                matchIndex = np.argmin(faceDis)

                if matches[matchIndex]:
                    name = personNames[matchIndex].upper()

                    y1,x2,y2,x1 = faceLoc
                    y1,x2,y2,x1 = y1*4,x2*4,y2*4,x1*4
                    cv2.rectangle(frame,(x1,y1),(x2,y2),(255,167,59),2)
                    cv2.rectangle(frame,(x1,y2-35),(x2,y2),(255,167,59),cv2.FILLED)
                    cv2.putText(frame,name,(x1+6,y2-6),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),2)
                    attendance(name)

            cv2.imshow('Webcam', frame)
            k = cv2.waitKey(1)
 
            
                
            
        #release camera object
        cap.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()

