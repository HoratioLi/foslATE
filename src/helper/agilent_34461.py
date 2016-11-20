#!/usr/bin/env python
'''
Created on 2014-07-07

@author: Rachel Kalmar
'''

import usbtmc
import ast

class A34461():

	# Initialize the instrument
	def __init__(self, num1, num2):
		try:
			self.instr = usbtmc.Instrument(num1, num2)
		except Exception as e:
			print "Agilent not connected."
			self.instr = None 

	# Set the mode to measure voltage
	def setModeToVoltage(self):
		self.instr.write("CONF:VOLT:DC")

	# Set the mode to measure current
	def setModeToCurrent(self):
		self.instr.write("CONF:CURR:DC")

	# Set the mode to measure resistance
	def setModeToResistance(self):
		self.instr.write("CONF:RES")

	# Set measurement range
	def setRange(self, measurementRange):
		self.instr.write("CURR:DC:RANG %s" % measurementRange)

	# Default NPLC is 10. Change to other values here.
	def setNPLC(self, targetNPLC):
		self.instr.write("CURR:DC:NPLC %s" % targetNPLC)

	# Turn off auto zero
	def disableAutoZero(self):
		# self.instr.write("CURR:DC:ZERO:AUTO OFF")
		self.instr.write("CURR:DC:ZERO:AUTO ONCE")		

	# Take reading
	def getReading(self):
		self.instr.write("SAMP:COUN 1")		
		reading = self.instr.ask("READ?")
		return float(reading)

	# Take multiple readings
	def getMultipleReadings(self, numReadings):
		readingList = []
		self.instr.write("SAMP:COUN %s" % numReadings)
		readings = self.instr.ask("READ?")
		self.instr.write("SAMP:COUN 1")
		# Note: using eval is potentially unsafe, should use ast.literal_eval instead
		# for x in ast.literal_eval(readings):	# This is safer but doesn't always work
		if numReadings == 1:
			readingList.append(float(readings))
		else:
			for x in eval(readings):
				readingList.append(x)
		return readingList

	# Disconnect device
	def reset(self):
		print "\nResetting Agilent\n"
		self.instr.write("*RST")
