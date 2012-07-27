#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
calibrate.py - Guides user through FreeIMU calibration

Copyright (C) 2012 Fabio Varesano <fvaresano@yahoo.it>

Development of this code has been supported by the Department of Computer Science,
Universita' degli Studi di Torino, Italy within the Piemonte Project
http://www.piemonte.di.unito.it/


This program is free software: you can redistribute it and/or modify
it under the terms of the version 3 GNU General Public License as
published by the Free Software Foundation.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

import time, serial
from struct import unpack
from binascii import unhexlify
from subprocess import call


print "\n\nWelcome to the FreeIMU library calibration routine!\nCopyright © Fabio Varesano 2012.\nReleased under GPL v3 - See http://www.gnu.org/copyleft/gpl.html\n\n"

print "Please load the FreeIMU_serial program from the FreeIMU library examples on your Arduino. Once you correctly installed the FreeIMU library, the examples are available from File->Examples->FreeIMU in the Arduino IDE.\nWhen done, close the Arduino IDE and its serial monitor."
raw_input('Hit Enter to continue.')

arduino_port = raw_input('Insert the serial port which connects to the Arduino (See in the Arduino IDE Tools->Serial Port if in doubt): ')


# instantiate a serial port object. port gets opened by default, no need to explicitly open it.
ser = serial.Serial(
	port= arduino_port,
	baudrate=115200,
	parity=serial.PARITY_NONE,
	stopbits=serial.STOPBITS_ONE,
	bytesize=serial.EIGHTBITS
)

if ser.isOpen():
  print "Arduino serial port opened correctly"
# we rely on the unhandled serial exception which will stop the program in case of problems during serial opening

ser.write('v') # ask version
print "\nFreeIMU library version informations:", 
print ser.readline()

print "\nThe program will now start to sample magnetometers readings. You have to rotate the device in 3D so that your rotations define a complete sphere.\n"
raw_input('Hit Enter to continue.')


count = 30
buff = [0.0 for i in range(9)]
filename = 'magn.txt'

tot_readings = 0

try:
  print "Sampling from magnetometer and logging to %s.\nHit CTRL+C to interrupt." % (filename)
  f = open(filename, 'w')
  while True:
    ser.write('b')
    ser.write(chr(count))
    for j in range(count):
      for i in range(9):
        buff[i] = unpack('h', ser.read(2))[0]
      ser.read(2) # consumes remaining '\r\n'
      
      #print buff
      readings_line = "%d %d %d\r\n" % (buff[6], buff[7], buff[8])
      f.write(readings_line) 
      
      tot_readings = tot_readings + 1
      if(tot_readings % 200 == 0):
        print "%d readings logged. Hit CTRL+C to interrupt." % (tot_readings)
      
      
except KeyboardInterrupt:
  ser.close()
  f.close()
  print "\n%d values logged to %s" % (tot_readings, filename)



call(["octave", "CompassCalib.m"]) #execute octave script

print "Calibration procedure completed. The calibration values have been saved to calibration.h and will be compiled in the next compilations of your FreeIMU library code."
  