#!/usr/bin/python

import smbus
import math
import websockets
import asyncio

import RPi.GPIO as GPIO
import time
import FaBo9Axis_MPU9250
GPIO.setmode(GPIO.BCM)
import sys
import json
import numpy


class DirectionMeasurement():
    def __init__(self):
        self.__mpu9250 = FaBo9Axis_MPU9250.MPU9250()
        self.__calibration={}
        with open('calibration.json', 'r') as f:
            self.__calibration=json.load(f)

    def direction(self):
        mag=self.__mpu9250.readMagnet()
        x=(mag['x']+self.__calibration['xoffset'])/self.__calibration['a']
        y=(mag['y']+self.__calibration['yoffset'])/self.__calibration['b']
        z=(mag['z']+self.__calibration['zoffset'])/self.__calibration['c']

        return math.atan2(y, x)

class DistanceMeasurement():
	def __init__(self, GPIO_TRIGGER, GPIO_ECHO):
		self.GPIO_TRIGGER=GPIO_TRIGGER
		self.GPIO_ECHO=GPIO_ECHO
		GPIO.setup(self.GPIO_TRIGGER,GPIO.OUT)
		GPIO.setup(self.GPIO_ECHO,GPIO.IN)

	def entfernung(self):
		GPIO.output(self.GPIO_TRIGGER, False)
		time.sleep(0.00002)

		# Trig High setzen
		GPIO.output(self.GPIO_TRIGGER, True)

		# Trig Low setzen (nach 0.01ms)
		time.sleep(0.00005)
		GPIO.output(self.GPIO_TRIGGER, False)

		Startzeit = time.time()
		Endzeit = time.time()

		# Start/Stop Zeit ermitteln
		while GPIO.input(self.GPIO_ECHO) == 0:
			Startzeit = time.time()

		while GPIO.input(self.GPIO_ECHO) == 1:
			Endzeit = time.time()

		# Vergangene Zeit
		Zeitdifferenz = Endzeit - Startzeit

		# Schallgeschwindigkeit (34300 cm/s) einbeziehen
		entfernung = (Zeitdifferenz * 34300) / 2

		return entfernung

class GyroMeasurement():
	def __init__(self):
		# Power management registers
		power_mgmt_1 = 0x6b
		power_mgmt_2 = 0x6c

		self.bus = smbus.SMBus(1) # or bus = smbus.SMBus(1) for Revision 2 boards
		self.address = 0x68       # This is the address value read via the i2cdetect command

		# Now wake the 6050 up as it starts in sleep mode
		self.bus.write_byte_data(self.address, power_mgmt_1, 0)

	def read_byte(self, adr):
		return self.bus.read_byte_data(self.address, adr)

	def read_word(self, adr):
		high = self.bus.read_byte_data(self.address, adr)
		low = self.bus.read_byte_data(self.address, adr+1)
		val = (high << 8) + low
		return val

	def read_word_2c(self, adr):
		val = self.read_word(adr)
		if (val >= 0x8000):
			return -((65535 - val) + 1)
		else:
			return val

	def dist(self, a,b):
		return math.sqrt((a*a)+(b*b))

	def get_y_rotation(self, x,y,z):
		radians = math.atan2(x, dist(y,z))
		return -math.degrees(radians)

	def get_x_rotation(self, x,y,z):
		radians = math.atan2(y, dist(x,z))
		return math.degrees(radians)

	def gyro(self):
		gyro_xout = self.read_word_2c(0x43)
		gyro_yout = self.read_word_2c(0x45)
		gyro_zout = self.read_word_2c(0x47)

		return {'x': gyro_xout / 131, 'y': gyro_yout / 131, 'z': gyro_zout / 131}

	def accel(self):
		accel_xout = self.read_word_2c(0x3b)
		accel_yout = self.read_word_2c(0x3d)
		accel_zout = self.read_word_2c(0x3f)

		return {'x': accel_xout / 16384.0, 'y': accel_yout / 16384.0, 'z': accel_zout / 16384.0}

distanceMeasurement=DistanceMeasurement(23, 24)
gyroMeasurement=GyroMeasurement()
directionMeasurement=DirectionMeasurement()

if __name__ == '__main__':
	try:
		async def data(websocket, path):
			while True:
				await websocket.send('{"direction":'+str(directionMeasurement.direction())+', "distance": '+str(distanceMeasurement.entfernung())+'}')
				await asyncio.sleep(0.1)

		start_server = websockets.serve(data, '', 5678)

		asyncio.get_event_loop().run_until_complete(start_server)
		asyncio.get_event_loop().run_forever()

	# Programm beenden
	except KeyboardInterrupt:
		print("Programm abgebrochen")
		GPIO.cleanup()
