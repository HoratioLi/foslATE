#!/usr/bin/env python
'''
Created on 2014-07-16

@author: Rachel Kalmar
'''

from constants import *
from helper.utils import *

ledTestList = []
for ledIndex in range(1, NUM_LED_TESTS+1):
	ledTestList.append("LED Test %s" % ledIndex)

testList = []
bleTestList = []

if STATION_ID == 1:
	if DEVICE_TYPE == 'Venus':
		testList = [
			"Electrical Current Test",
			"Get Mac Address Test",
			"Idle Mode Test", 
			ledTestList,
			"Load Test",
			"BT DTM Test",
			"Accelerometer Self Test",
			"Accelerometer Orientation Test",
			"Accelerometer Current Test",
			"Deep Sleep Test",
		]

		bleTestList = [
			"Get RSSI Test",
		]

	elif DEVICE_TYPE == 'Apollo':
		testList = [
			"Electrical Current Test",
			"Dummy Test",
			"Idle Mode Test",
			ledTestList,
			"Load Test",
			"BT DTM Test",
			"Accelerometer Self Test",
			"Accelerometer Current Test",
			"Get Mac Address Test",
			"Accelerometer Orientation Test",
		]

		bleTestList = [
			"Get RSSI Test",
		]

		# Add in special setup for CES testing
		if STATION_INDEX == -2:
			bleTestList.append("Write Serial Number Test")
			bleTestList.append("Read Serial Number Test")

if STATION_ID == 2:
	if DEVICE_TYPE == 'Venus':
		testList = [
			"Duplicate Serial Number Test",
		]

		bleTestList = [
			"Get RSSI Test",
			"Write Serial Number Test",
			"Read Serial Number Test",
			"Accelerometer BT Self Test",
			"Battery BT Test",
			"Reset via BT",			
		]

	elif DEVICE_TYPE == 'Apollo':
		testList = [
			"Duplicate Serial Number Test",
			"Operating Current Test",
		]	

		bleTestList = [
			"Get RSSI Test",
			"Write Serial Number Test",
			"Read Serial Number Test",
			"Accelerometer Streaming Test",
		]
		
if STATION_ID == 3:
	if DEVICE_TYPE == 'Venus':
		testList = [
			"Operating Current Test",
			"Duplicate Serial Number Test",
			"Recent Sync Test",
			"Battery Plot Test",
		]

		bleTestList = [
			"Get RSSI Test",
			"Read Serial Number Test",
		]

	elif DEVICE_TYPE == 'Apollo':
		testList = [
			"Operating Current Test",
			"Duplicate Serial Number Test",
			"Recent Sync Test",
			"Battery Plot Test",
		]	

		bleTestList = [
			"Get RSSI Test",
			"Read Serial Number Test",
		]

testList = flattenList(testList)
testOrder = createTestOrder(testList)

bleTestList = flattenList(bleTestList)
testOrderBLE = createTestOrder(bleTestList)


	
	
