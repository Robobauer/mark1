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
ser = serial.Serial("/dev/ttyACM0",115200)



def findCont(roi):
	# find contours in the thresholded image
	cnts = cv2.findContours(roi, cv2.RETR_TREE,
		cv2.CHAIN_APPROX_SIMPLE)
	cnts =  cnts[1]
	return cnts

	
def drawCont(cnts, frame, a):
	cX = 0
	cY = 0
	if cnts != []:
		c = max(cnts, key=cv2.contourArea)
		M = cv2.moments(c)
		if M["m00"] != 0: 
			
			cX = int(M["m10"] / M["m00"]) + a
			cY = int(M["m01"] / M["m00"]) + a
			cv2.circle(frame, (cX, cY), 7, (255, 255, 255), -1)
			cv2.putText(frame, str(360-cX), (cX - 20, cY - 20),
				cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
			
	cnts =[]
	return frame, cY, cX
	


##CALCULATE MAG
def reg(coeff):
	coeff = coeff * 100000
	print(int(coeff))
	return 0

##CALCULATE ANGLE	
#			if not fail:
#				if (639 > cX > 450):
#					print("turn right hard")
#					setMotorlevel(180,100)
#				elif (450 >= cX > 370):
#					print("turn right soft")
#					setMotorlevel(120,100)
#				elif (370 >= cX > 280):
#					print("forward middle")
#					setMotorlevel(90,100)
#				elif (280 >= cX > 190):
#					print("turn left soft")
#					setMotorlevel(60,100)
#				elif (190 >= cX > 1):
#					print("turn left hard")
#					setMotorlevel(0,100)
	
##SERIAL STUFF
#def serialTransmit(c):
#   print('serial {!r}'.format(c))
#   ser.write(str.encode(c + '\n'))
#	
#def setMotorlevel(angle,mag):
#	serialTransmit('{};{}'.format(int(angle), int(mag)))
	
	
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
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	blurred = cv2.GaussianBlur(gray, (5, 5), 0)
	mask = cv2.erode(blurred, None, iterations=2)
	mask = cv2.dilate(mask, None, iterations=2)
	mask = cv2.threshold(mask, 30, 30, cv2.THRESH_BINARY_INV)[1]

	# construct a mask for the color "green", then perform
	# a series of dilations and erosions to remove any small
	# blobs left in the mask
	#mask = cv2.inRange(image, greenLower, greenUpper)
	#mask = cv2.erode(mask, None, iterations=2)
	#mask = cv2.dilate(mask, None, iterations=2)

	
	#get Image_size
	shape = mask.shape
	split = 4
	a=0
	x=0
	c=0
	regressionX = [0,0,0,0]
	regressionY = [0,0,0,0]
	
	for c in range(0,split):
		a= x
		x= x + int(shape[0]/(split))
		rio = mask[a:x,a:shape[1]]
		cnts = findCont(rio)
		frame, pointY, pointX = drawCont(cnts,frame,a)
		regressionX[c] = pointX
		regressionY[c] = pointY
		c = c+1
	
	if regressionX != [0,0,0,0]:
		x = np.array(regressionX)
		y = np.array(regressionY)
		z = np.polyfit(x, y, 2)
		reg(z[0])
	

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
