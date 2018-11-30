import serial
import argparse

ser = serial.Serial("/dev/ttyACM0",115200)
	

def serialTransmit(c):
    print('serial {!r}'.format(c))
    ser.write(str.encode(c + '\n'))
	

def transmitDrivingVector(angle,mag):
	serialTransmit('{};{}'.format(int(angle), int(mag)))