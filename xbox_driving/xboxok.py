# first try to combine a ball_recognition
# with raspi-robot movement - markus oct 2018
# import the necessary packages
import math
import cv2
import serial
import xbox
import time

# import getch
# serial Port communication
ser = serial.Serial("/dev/ttyACM0", 115200)
angleThres = 1.0
magThres = 0.001


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
    print('serial {!r}'.format(c))
    ser.write(str.encode(c + '\n'))


# keep looping
while True:
    joy = xbox.Joystick()

    oldMag = 0
    oldAngle = 0

    while not joy.Back():

        x, y = joy.leftStick()

        newMag = math.sqrt(x**2 + y**2)
        if newMag < 0.1:
            newMag = 0

        newAngle = angleFromCoords(x, y)

        if (oldMag + magThres) <= newMag or newMag <= (oldMag - magThres) or (oldAngle + angleThres) <= newAngle or newAngle <= (oldAngle - angleThres):
            serialTransmit('{};{}'.format(int(newAngle), int(newMag * 100)))
            oldMag = newMag
            oldAngle = newAngle
        time.sleep(0.1)

    joy.close()
    # if the 'q' key is pressed, stop the loop
    if joy.X():
        break

# close all windows
cv2.destroyAllWindows()
