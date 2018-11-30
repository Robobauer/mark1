# Third tutorial code for line detection
# additionally to the gray-scaling and bluring we will
# and finding the contours in the image, we will now 
# draw a line through the found contor and calculate
# its angle and x position
# markus 10.2018
 
# import the necessary packages
from collections import deque
from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
import argparse
import cv2
import imutils
import time
import math
import TransmitLib

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (640, 480)
print(camera.awb_mode)
#camera.awb_mode='sunlight'
camera.exposure_mode="backlight"
print(camera.exposure_mode)
camera.rotation=180
#camera.framerate = 10
rawCapture = PiRGBArray(camera, size=(640, 480))


# allow the camera to warm up
time.sleep(2.0)

# keep looping
for frameCapture in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # grab the raw NumPy array representing the image, then initialize the timestamp
    startTime = time.time()
    frame = frameCapture.array
    #change to gray colors
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Gaussian blur
    blur = cv2.GaussianBlur(gray,(5,5),0)
    # Color thresholding - what is black what is white?
    ret,thresh = cv2.threshold(blur,100,200,cv2.THRESH_BINARY_INV)
    # Find the contours of the frame - method has three return arguments
    # only the list of contours is needed by us
    _,contours,hierarchy = cv2.findContours(thresh.copy(), 1, cv2.CHAIN_APPROX_NONE)

    # there could be multible contours - lets focus on the biggest
    print("len(contours)=",len(contours))
    if len(contours) > 0:
        # Find the biggest contour (if detected)
        c = max(contours, key=cv2.contourArea)
	# draw the contours on the frame
        #cv2.drawContours(frame, c, -1, (0,255,0), 1)
        #now try to fit a line through the contour
        [vx,vy,x0,y0] = cv2.fitLine(c, cv2.DIST_L2,0,0.01,0.01)
        #found x y position and a normalized unit vektor
        #achtung! origin is to the top left! so vx to the right 
        # is positiv and vy down is positiv
        print("vx={}, vy={}, x0={}, y0={}".format(vx,vy,x0,y0))
        alpha = math.asin(vy)
        alpha = int(math.degrees(alpha))
        if (alpha < 0):
            alpha = alpha + 180
        print("alpha=",alpha)

        #the formular for the line going through the contour is
        # (x,y) = (x0,y0) + t*(vx,vy)
        #lets calculate to points and draw a line through it for
        # better visualisation of the found contour
        x1 = x0 + int(150*vx)
        y1 = y0 + int(150*vy)
        x2 = x0 + int(-150*vx)
        y2 = y0 + int(-150*vy)
        cv2.line(frame,(x1,y1),(x2,y2),(0,255,0),2)

    else:
        print("could not find the line")

    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)
    #Display the resulting frames
    cv2.imshow('thres',thresh)
    cv2.imshow('blur',frame)
    endTime = time.time()
    fps = 1//(endTime - startTime)
    print("fps=",fps)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()





