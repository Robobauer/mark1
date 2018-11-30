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


def findCont(roi):
	# find contours in the thresholded image
	cnts = cv2.findContours(roi, cv2.RETR_TREE,
		cv2.CHAIN_APPROX_SIMPLE)
	cnts =  cnts[1]
	return cnts

	
def drawCont(contours, frame, offset):
	cX = 0
	cY = 0
	if len(contours) > 0:
	# Find the biggest contour (if detected)
		c = max(contours, key=cv2.contourArea)
		M = cv2.moments(c)
		if M["m00"] != 0: 
			cX = int(M["m10"] / M["m00"]) + offset
			cY = int(M["m01"] / M["m00"]) + offset
			#cv2.drawContours(frame, [c], 0, (0, 255, 0), 3)
			cv2.circle(frame, (cX, cY), 7, (255, 255, 255), -1)
			cv2.putText(frame, str(360-cX), (cX - 20, cY - 20),
				cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
			
			contours =[]
			return frame, cY, cX
		
	contours =[]
	return frame, -1, -1


def motorVectorCalc(cX):
	if (639 > cX > 450):
		print("turn right hard")
		transmitlib.transmitDrivingVector(180,70)
	elif (450 >= cX > 370):
		print("turn right soft")
		transmitlib.transmitDrivingVector(120,70)
	elif (370 >= cX > 280):
		print("forward middle")
		transmitlib.transmitDrivingVector(90,70)
	elif (280 >= cX > 190):
		print("turn left soft")
		transmitlib.transmitDrivingVector(60,70)
	elif (190 >= cX > 1):
		print("turn left hard")
		transmitlib.transmitDrivingVector(0,70)


# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (640, 480)
camera.awb_mode='sunlight'
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

	# handle the frame from VideoCapture or VideoStream
	#frame = frame[1] if args.get("video", False) else frame
	frame = frameCapture.array


	# resize the frame, blur it, and convert it to the HSV
	# color space
	#frame = imutils.resize(frame, width=600)
	preprocessedFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	preprocessedFrame = cv2.GaussianBlur(preprocessedFrame, (5, 5), 0)
	preprocessedFrame = cv2.erode(preprocessedFrame, None, iterations=2)
	preprocessedFrame = cv2.dilate(preprocessedFrame, None, iterations=2)
	preprocessedFrame = cv2.threshold(preprocessedFrame, 50, 50, cv2.THRESH_BINARY_INV)[1]
	
	#get Image_size
	shape = preprocessedFrame.shape

	#split image
	c = 0
	x = 0
	offset = 0
	split = 4
	for c in range(0,split):
		offset = x
		x = x + int(shape[0]/(split))
		rio = preprocessedFrame[offset:x,offset:shape[1]]
		cnts = findCont(rio)
		frame, pointY, pointX = drawCont(cnts,frame,offset)

	#drive in direction of last Point
	#if pointX >= 0:
		#motorVectorCalc(pointX)

	#turn Image
	#(h, w) = frame.shape[:2]
	#center = (w / 2, h / 2)
	
	#M = cv2.getRotationMatrix2D(center, 180, 1)
	#frame = cv2.warpAffine(frame, M, (w,h))
	
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
