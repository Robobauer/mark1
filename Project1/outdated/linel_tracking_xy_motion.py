#first try to combine a ball_recogintion 
#with raspi-robot movement - markus oct 2018
# import the necessary packages
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
#import getch
# serial Port communication
ser = serial.Serial("/dev/ttyACM0",9600)


def findCont(roi):
	# find contours in the thresholded image
	cnts = cv2.findContours(roi, cv2.RETR_TREE,
		cv2.CHAIN_APPROX_SIMPLE)
	cnts =  cnts[1]
	return cnts

	
def drawCont(cnts, frame):
	if cnts != []:
		# loop over the contours
		for c in cnts:
			M = cv2.moments(c)
			if M["m00"] != 0: 
				cX = int(M["m10"] / M["m00"])
				cY = int(M["m01"] / M["m00"])
				fail = False
			else:
				fail = True
				break
	
	
			cv2.drawContours(frame, [c], 0, (0, 255, 0), 3)
			cv2.circle(frame, (cX, cY), 7, (255, 255, 255), -1)
			cv2.putText(frame, str(360-cX), (cX - 20, cY - 20),
		        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

			print("before serial transmit")

#			if not fail:
#				if (639 > cX > 450):
#					print("turn right hard")
#					ser.write(str.encode('s'))
#				elif (450 >= cX > 370):
#					print("turn right soft")
#					ser.write(str.encode('r'))
#				elif (370 >= cX > 280):
#					print("forward middle")
#					ser.write(str.encode('f'))
#				elif (280 >= cX > 190):
#					print("turn left soft")
#					ser.write(str.encode('1'))
#				elif (190 >= cX > 1):
#					print("turn left hard")
#					ser.write(str.encode('m'))

	cnts =[]
	return frame


def serialTransmit(c) :
	ser.write(c)


# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (640, 480)
print(camera.awb_mode)
camera.awb_mode='sunlight'
#camera.exposure_mode="sunlight"
print(camera.exposure_mode)
camera.rotation=180
camera.framerate = 10
rawCapture = PiRGBArray(camera, size=(640, 480))

# define the lower and upper boundaries of the "green"
# ball in the HSV color space, then initialize the
# list of tracked points
greenLower = (0, 0, 0)
greenUpper = (0, 0, 13)

# allow the camera to warm up
time.sleep(0.1)

#serial Port communication
#ser = serial.Serial('/dev/ttyACM0',9600)


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
	blurred = cv2.GaussianBlur(frame, (11, 11), 0)
	image = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

	# construct a mask for the color "green", then perform
	# a series of dilations and erosions to remove any small
	# blobs left in the mask
	mask = cv2.inRange(image, greenLower, greenUpper)
	mask = cv2.erode(mask, None, iterations=2)
	mask = cv2.dilate(mask, None, iterations=2)

	
	#get Image_size
	shape = mask.shape
	
	#split image into region of interests
	cnts = findCont(mask)
	frame = drawCont(cnts,frame)

	# show the frame to our screen
	cv2.imshow("Image", frame)
	key = cv2.waitKey(1) & 0xFF

	# clear the stream in preparation for the next frame
	rawCapture.truncate(0)

	# if the 'q' key is pressed, stop the loop
	if key == ord("q"):
		break

# close all windows
cv2.destroyAllWindows()
