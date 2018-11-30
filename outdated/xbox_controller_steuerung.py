# first try to combine a ball_recognition
# with raspi-robot movement - markus oct 2018
# import the necessary packages
import math
import cv2
import serial
import xbox

# import getch
# serial Port communication
ser = serial.Serial("/dev/ttyACM0", 9600)


def angleFromCoords(_x, _y):
	_angle = 0.0
	if _x == 0.0 and _y == 0.0:
		_angle = 90.0
	elif _x >= 0.0 and _y >= 0.0:
		# first quadrant
		_angle = math.degrees(math.atan(_y/_x)) if _x != 0.0 else 90.0
	elif _x < 0.0 and _y >= 0.0:
		# second quadrant
		_angle = math.degrees(math.atan(_y/_x))
		_angle += 180.0
	elif _x < 0.0 and _y < 0.0:
		# third quadrant
		_angle = math.degrees(math.atan(_y/_x))
		_angle += 180.0
	elif _x >= 0.0 and _y < 0.0:
		# third quadrant
		_angle = math.degrees(math.atan(_y/_x)) if _x != 0.0 else -90.0
		_angle += 360.0
	return _angle


def serialTransmit(c):
	ser.write(c)


# keep looping
while True:
	joy = xbox.Joystick()

	serialTransmit(x)

	while not joy.Back():

		x, y = joy.leftStick()
		angle = angleFromCoords(x, y)
		if (45 > angle > 0) or (360 > angle > 315):
			serialTransmit('r')
		elif 225 > angle > 135:
			serialTransmit('l')
		elif 135 > angle > 45:
			serialTransmit('f')
	joy.close()
	# if the 'q' key is pressed, stop the loop
	if joy.X():
		break

# close all windows
cv2.destroyAllWindows()
