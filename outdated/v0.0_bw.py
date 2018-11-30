# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
 
# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
rawCapture = PiRGBArray(camera)
 
# allow the camera to warmup
time.sleep(0.1)
 
# grab an image from the camera
camera.capture(rawCapture, format="bgr")
image = rawCapture.array


# display the image on screen and wait for a keypress
cv2.imshow("Image", image)
cv2.waitKey(0)



#convert to grayscale, blur slightly and threshold
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]


 
# display the image on screen and wait for a keypress
cv2.imshow("Image", thresh)
cv2.waitKey(0)
