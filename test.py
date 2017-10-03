# coding: utf-8
import FaBo9Axis_MPU9250
import time
import sys
import json
import numpy
import math

mpu9250 = FaBo9Axis_MPU9250.MPU9250()
calibration={}
with open('calibration.json', 'r') as f:
    calibration=json.load(f)

try:
    while True:

        mag = mpu9250.readMagnet()
        print(mag['x'], mag['y'])
        x=(mag['x']+calibration['xoffset'])/calibration['a']
        y=(mag['y']+calibration['yoffset'])/calibration['b']
        z=(mag['z']+calibration['zoffset'])/calibration['c']
        print(x, y)
        print(math.atan2(y, x)/math.pi*180)

        time.sleep(0.01)

except KeyboardInterrupt:
	sys.exit()
