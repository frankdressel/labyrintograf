# coding: utf-8
## @package faboMPU9250
#  This is a library for the FaBo 9AXIS I2C Brick.
#
#  http://fabo.io/202.html
#
#  Released under APACHE LICENSE, VERSION 2.0
#
#  http://www.apache.org/licenses/
#
#  FaBo <info@fabo.io>

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
#        accel = mpu9250.readAccel()
#        print(" ax = " , ( accel['x'] ))
#        print(" ay = " , ( accel['y'] ))
#        print(" az = " , ( accel['z'] ))
#
#        gyro = mpu9250.readGyro()
#        print(" gx = " , ( gyro['x'] ))
#        print(" gy = " , ( gyro['y'] ))
#        print(" gz = " , ( gyro['z'] ))

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
