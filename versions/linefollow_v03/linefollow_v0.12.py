#import Packages
from collections import deque
from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
import argparse
import cv2
import imutils
import time
from time import sleep
import serial
import transmitlib

blackLower = (0, 0, 0)
blackUpper = (255, 255, 15)

def findCont(roi):
    # find contours in the thresholded image
    cnts = cv2.findContours(roi, cv2.RETR_TREE,
        cv2.CHAIN_APPROX_SIMPLE)
    cnts =  cnts[1]
    return cnts

    
def drawCont(contours, frame):
    if len(contours) > 0:
    # Find the biggest contour (if detected)
        c = max(contours, key=cv2.contourArea)
        M = cv2.moments(c)
        if M["m00"] != 0: 
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            cv2.drawContours(frame, [c], 0, (0, 255, 0), 3)
            cv2.circle(frame, (cX, cY), 7, (255, 255, 255), -1)
            cv2.rectangle(frame, (0,0), (size[1],int(size[0]/4)), (0,255,0),2)
            cv2.putText(frame, str(360-cX), (cX - 20, cY - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            
            contours =[]
            return frame, cX
        
    contours =[]
    return frame, -1


def motorVectorCalc(cX):
    if (639 > cX > 450):
        print("turn right hard")
        transmitlib.transmitDrivingVector(180,100)
    elif (450 >= cX > 370):
        print("turn right soft")
        transmitlib.transmitDrivingVector(120,100)
    elif (370 >= cX > 280):
        print("forward middle")
        transmitlib.transmitDrivingVector(90,100)
    elif (280 >= cX > 190):
        print("turn left soft")
        transmitlib.transmitDrivingVector(60,100)
    elif (190 >= cX > 1):
        print("turn left hard")
        transmitlib.transmitDrivingVector(0,100)


# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (640, 480)
camera.awb_mode='auto'
camera.exposure_mode="backlight"
print(camera.awb_mode)
print(camera.exposure_mode)
#camera.rotation=180
camera.framerate = 60
rawCapture = PiRGBArray(camera, size=(640, 480))

# allow the camera to warm up
time.sleep(0.2)

# initialize stopped variable
stopped = False

# keep looping
for frameCapture in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text

    # handle the frame from VideoCapture or VideoStream
    #frame = frame[1] if args.get("video", False) else frame
    frame = frameCapture.array


    # resize the frame, blur it, and convert it to the HSV
    # color space
    #frame = imutils.resize(frame, width=600)
    preprocessedFrame = cv2.GaussianBlur(frame, (5, 5), 0)
    preprocessedFrame = cv2.cvtColor(preprocessedFrame, cv2.COLOR_BGR2HSV)
    preprocessedFrame = cv2.inRange(preprocessedFrame, blackLower, blackUpper)
    preprocessedFrame = cv2.erode(preprocessedFrame, None, iterations=2)
    preprocessedFrame = cv2.dilate(preprocessedFrame, None, iterations=2)
    
    #calculate height of whole line for 90° curve detection
    im2,contours,hierarchy = cv2.findContours(preprocessedFrame, 1, 2)
    if contours != []:
        cnt = contours[0]
        x,y,w,h = cv2.boundingRect(cnt)
        cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
        cnts =[]
    
    
    #get Image_size
    size = preprocessedFrame.shape
    
    preprocessedFrame = preprocessedFrame[0:int(size[0]/4),0:size[1]]
    
    #split image into region of interests
    cnts = findCont(preprocessedFrame)
    frame,cX = drawCont(cnts,frame)
    if cX >= 0:
        motorVectorCalc(cX)

    #turn Image
    (h, w) = frame.shape[:2]
    center = (w / 2, h / 2)
    
    M = cv2.getRotationMatrix2D(center, 180, 1)
    frame = cv2.warpAffine(frame, M, (w,h))
    
    # show the frame to our screen
    cv2.imshow("Image", frame)
    key = cv2.waitKey(1) & 0xFF
    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)

    # if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        transmitlib.transmitDrivingVector(0,0)
        break

# close all windows
cv2.destroyAllWindows()
