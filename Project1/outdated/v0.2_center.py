# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import imutils


resy = 640
resx = 480

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
#camera.resolution = (resy, resx)
rawCapture = PiRGBArray(camera)

# allow the camera to warmup
time.sleep(0.1)

# grab an image from the camera
camera.capture(rawCapture, format="bgr")
image = rawCapture.array



#convert to grayscale, blur slightly and threshold
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY_INV)[1]

# find contours in the thresholded image
cnts = cv2.findContours(thresh, cv2.RETR_TREE,
	cv2.CHAIN_APPROX_SIMPLE)
cnts =  cnts[1]


# loop over the contours
for c in cnts:
	M = cv2.moments(c)
	if M["m00"] != 0: 
		cX = int(M["m10"] / M["m00"])
		cY = int(M["m01"] / M["m00"])

	print(cX)

	cv2.drawContours(image, [c], 0, (0, 255, 0), 3)
	cv2.circle(image, (cX, cY), 7, (255, 255, 255), -1)
	
	cv2.circle(image, (360, 240), 7, (255, 255, 255), -1)
	cv2.putText(image, str(360-cX), (cX - 20, cY - 20),
		cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)



# display the image on screen and wait for a keypress
cv2.imshow("Image", image)
cv2.waitKey(0)

