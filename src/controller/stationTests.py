#!/usr/bin/env python
'''
Created on 2014-07-07

@author: Rachel Kalmar
'''

from model.device import *
from helper.gpio_no_sudo import *
from constants import *
from array import array

import numpy
import usbtmc
import binascii
import serial
import time
from ble_commands import *
from model.bleDevice import BLEdevice 
from helper.agilent_34461 import A34461
from helper.utils import *
from pprint import pprint
import helper.posgresDB_extractor as pgdb
from raspberryPi_commands import *

from helper.plotOperatingCurrent import *
import subprocess

import numpy as np
import operator

import pyaudio
import math
import struct
import wave
import sys
from matplotlib.mlab import find

###########################################
# Helper functions
###########################################

def readCurrent(instr, num_readings, params):
    readings = instr.getMultipleReadings(num_readings)
    meanReading = numpy.mean(readings)
    if INVERT_AGILENT_READINGS:
        for reading in readings:
            reading = reading * -1
        meanReading = meanReading * -1
    if params['debug_mode']:
        print "\n%d readings: %s" % (num_readings, readings)    
        print "Mean of %d readings: %s" % (num_readings, meanReading)
    testResult = MultipleCurrentTest(currents=readings, 
                                 average=meanReading)
    return testResult

def readSingleCurrent(instr, params):
    reading = instr.getReading()
    if INVERT_AGILENT_READINGS:
        reading = reading * -1    
    if params['debug_mode']:
        print "\nReading: %s" % reading
    testResult = SingleCurrentTest(current=reading)
    return testResult    

def readSingleVoltage(instr, params):
    pinState = gpio_ns_write(VOLTAGE_TEST_PIN, GPIO_LO) 
    read_pin_state = gpio_ns_read(VOLTAGE_TEST_PIN)  
    print "read_pin_state: %s, intended pin_state: %s" % (read_pin_state, GPIO_LO)               
    reading = instr.getReading()
    if INVERT_AGILENT_READINGS:
        reading = reading * -1        
    #choice = raw_input("Hit 'Enter' to continue: ")        
    pinState = gpio_ns_write(VOLTAGE_TEST_PIN, GPIO_HI) 
    read_pin_state = gpio_ns_read(VOLTAGE_TEST_PIN)  
    print "read_pin_state: %s, intended pin_state: %s" % (read_pin_state, GPIO_HI)      
    if params['debug_mode']:
        print "\nReading: %s" % reading
    testResult = SingleVoltageTest(voltage=reading)
    return testResult   

def setResults(testResult, name, isPassed, params):
    testResult.name = name
    testResult.is_passed = isPassed
    if params['verbose_mode']:
        pprint (vars(testResult))
        print ""
    return testResult    

def setTimeoutResults(name, timeout, params):
    print "Warning: timeout in %s. Exiting." % name
    testResult = TimeoutTest()
    testResult.timeout = timeout
    testResult.is_passed = False
    testResult.name = name
    if params['verbose_mode']:
        pprint (vars(testResult))
        print ""
    return testResult    

###########################################
# Tests
###########################################
def electricalCurrentTest(instr, params):
    # Measuring the current consumption on the DUT
    print "================================="
    print "Performing Electrical Current Test (test %s/%s)" % (params['testIndex'], params['numTests'])
    print "================================="    
    testName = "Electrical Current Test"
    testResult = readCurrent(instr, params['num_readings'], params)

    rangeLo = params['mcu_current_lower']
    rangeHi = params['mcu_current_upper']

    # Compare result against upper/lower bounds and make a pass/fail decision
    if testResult.average >= rangeLo and testResult.average <= rangeHi:
        isPassed = True
        print "\n%s: passed\n" % testName
    else:
        isPassed = False
        print "\n%s: failed: current out of range.  Measured: %s, Range: [%s, %s] \n" % (testName, testResult.average, rangeLo, rangeHi)

    testResult = setResults(testResult, testName, isPassed, params)
    return testResult

def voltageMeasurementTest(instr, params):
    print "================================="
    print "Performing Voltage Measurement Test"
    print "================================="    
    testName = "Voltage Measurement Test"
    instr.setModeToVoltage()
    testResult = readSingleVoltage(instr, params)
    instr.setModeToCurrent()

    rangeLo = params['pi_voltage_lower']
    rangeHi = params['pi_voltage_upper']

    # Compare result against upper/lower bounds and make a pass/fail decision
    if testResult.voltage >= rangeLo and testResult.voltage <= rangeHi:
        isPassed = True
        print "\n%s: passed\n" % testName
    else:
        isPassed = False
        print "\n%s: failed: voltage out of range.  Measured: %s, Range: [%s, %s] \n" % (testName, testResult.voltage, rangeLo, rangeHi)

    testResult = setResults(testResult, testName, isPassed, params)
    return testResult

def idleModeTest(instr, params):
    print "================================="
    print "Performing Idle Mode Test (test %s/%s)" % (params['testIndex'], params['numTests'])
    print "================================="     
    testName = "Idle Mode Test"     

    rangeLo = params['idle_current_lower']
    rangeHi = params['idle_current_upper']

    instr.setRange(0.01)#0001) # 100 uA    # Set current range to microamps   
    instr.setNPLC(100)   
    time.sleep(2)
    testResult = readCurrent(instr, params['num_readings'], params)
    instr.setNPLC(1)
    instr.setRange(params['default_current_range']) # Set current range back to default

    # Compare result against upper/lower bounds and make a pass/fail decision
    if testResult.average > rangeLo and testResult.average < rangeHi:
        isPassed = True
        print "\n%s: passed\n" % testName
    else:
        isPassed = False
        print "\n%s: failed: current out of range.  Measured: %s, Range: [%s, %s] \n" % (testName, testResult.average, rangeLo, rangeHi)

    testResult = setResults(testResult, testName, isPassed, params)
    return testResult

def hibernationModeTest(instr, params):
    print "================================="
    print "Performing Hibernation Mode Test" # (test %s/%s)" % (params['testIndex'], params['numTests'])
    print "================================="     
    testName = "Hibernation Mode Test"     

    rangeLo = params['hibernation_current_lower']
    rangeHi = params['hibernation_current_upper']

    instr.setRange(0.0001) # 100 uA    # Set current range to microamps   
    instr.setNPLC(100)   
    time.sleep(2)
    testResult = readCurrent(instr, params['num_readings'], params)
    instr.setNPLC(1)
    instr.setRange(params['default_current_range']) # Set current range back to default

    # Compare result against upper/lower bounds and make a pass/fail decision
    if testResult.average >= rangeLo and testResult.average <= rangeHi:
        isPassed = True
        print "\n%s: passed\n" % testName
    else:
        isPassed = False
        print "\n%s: failed: current out of range.  Measured: %s, Range: [%s, %s] \n" % (testName, testResult.average, rangeLo, rangeHi)

    testResult = setResults(testResult, testName, isPassed, params)
    return testResult

def dummyTest(instr, params):
    print "================================="
    print "Place Holder Test (test %s/%s)" % (params['testIndex'], params['numTests'])
    print "================================="       
    print ""

    port = params['port']
    port.flushInput()
    
    return None

def LEDtest(instr, params):
    print "================================="
    print "Performing LED Test %s (test %s/%s)" % (params['ledIndex'], params['testIndex'], params['numTests'])
    print "================================="       
    testName = "LED Test %s" % params['ledIndex']
    testResult = readSingleCurrent(instr, params)
    
    if DEVICE_TYPE == "Pluto":
        if params['ledIndex'] == 1:
            rangeLo = params['led_low_current_lower']
            rangeHi = params['led_low_current_upper'] 
        if params['ledIndex'] == 2: 
            rangeLo = params['led_high_current_lower']
            rangeHi = params['led_high_current_upper']
    else:
        rangeLo = params['led_current_lower']
        rangeHi = params['led_current_upper']

    # Compare result against upper/lower bounds and make a pass/fail decision
    if testResult.current >= rangeLo and testResult.current <= rangeHi:
        isPassed = True
        print "\n%s: passed\n" % testName
    else:
        isPassed = False
        print "\n%s: failed: current out of range.  Measured: %s, Range: [%s, %s] \n" % (testName, testResult.current, rangeLo, rangeHi)

    testResult = setResults(testResult, testName, isPassed, params)
    return testResult

def loadTest(instr, params):
    print "================================="
    print "Performing Load Test (test %s/%s)" % (params['testIndex'], params['numTests'])
    print "================================="       
    testName = "Load Test"      
    testResult = readSingleCurrent(instr, params)
    
    rangeLo = params['load_current_lower']
    rangeHi = params['load_current_upper']

    # Compare result against upper/lower bounds and make a pass/fail decision
    if testResult.current >= rangeLo and testResult.current <= rangeHi:
        isPassed = True
        print "\n%s: passed\n" % testName
    else:
        isPassed = False
        print "\n%s: failed: current out of range.  Measured: %s, Range: [%s, %s] \n" % (testName, testResult.current, rangeLo, rangeHi)

    testResult = setResults(testResult, testName, isPassed, params)
    return testResult

def btDTMtest(instr, params):
    print "================================="
    print "Performing BT DTM Test (test %s/%s)" % (params['testIndex'], params['numTests'])
    print "================================="       
    print "\n(Skipping for now...)\n"
    return None

def accelSelfTest(instr, params):
    print "================================="
    print "Performing Accelerometer Self Test (test %s/%s)" % (params['testIndex'], params['numTests'])
    print "================================="    
    # Check accel self test, if this fails then IO_4 will be asserted. 
    testName = "Accelerometer Self Test"

    # If operating with a limited pin set, get the pin state from the UART read in the orientation test instead
    if not LIMITED_PIN_SET:
        pinState = gpio_ns_read(MFG_INFO_PIN)
    else:
        pinState = params['pinState']

    if pinState == 1:
        isPassed = False
        print "\n%s: failed\n" % testName
    elif pinState == 0:
        isPassed = True
        print "\n%s: passed\n" % testName

    testResult = AccelSelfTest(isPassed=isPassed)
    testResult = setResults(testResult, testName, isPassed, params)
    return testResult  

def accelBTSelfTest(bleController, params):
    print "================================="
    print "Performing Accelerometer BT Self Test" 
    print "=================================" 
    print ""   
    testName = "Accelerometer BT Self Test"

    time.sleep(BLE_DELAY)
    testResult = AccelSelfTest()
    results = getAccelerometerValue(bleController)
    accel_value = results[1]
    timeout = results[0]

    if timeout:
        testResult = setTimeoutResults(testName, timeout, params)
    else:
        if accel_value == '0':
            isPassed = True
            print "\n%s: passed\n" % testName
        else:
            isPassed = False
            print "\n%s: failed\n" % testName

        testResult = AccelSelfTest(isPassed=isPassed)
        testResult = setResults(testResult, testName, isPassed, params)
    return testResult

def accelStreamingTest(bleController, params):
    print "================================="
    print "Performing Accelerometer Streaming Data Test" 
    print "=================================" 
    print ""   
    testName = "Accelerometer Streaming Test"

    startTime = resetTimer()

    testResult = AccelZDataTest()
    results = getAccelerometerStreaming(bleController)
    timeout = results[0]
    zData1 = results[1]
    zData2 = results[2]
    zData3 = results[3] 
    xData1 = results[4] 
    xData2 = results[5]
    xData3 = results[6] 
    yData1 = results[7] 
    yData2 = results[8]
    yData3 = results[9] 
    isPassed = True 

    axis = ["x", "y", "z"]

    print "Test time: %s\n" % getTimePassed(startTime)

    if timeout:
        testResult = setTimeoutResults(testName, timeout, params)
    else:
        zData = [zData1, zData2, zData3] 
        xData = [xData1, xData2, xData3]
        yData = [yData1, yData2, yData3]   

        axis_data = [xData, yData, zData]
        # Check each axis to see if it is in range
        count = 0
        for a in axis:
            if max(axis_data[count]) >= params['accel_streamed_data_upper'][count] or min(axis_data[count]) <= params['accel_streamed_data_lower'][count]:
                isPassed = False
                print "%s %s-data: failed" % (testName, axis[count])            
            else:
                print "%s %s-data: passed" % (testName, axis[count])            

            count += 1

        print ""
        print "xdata: " + str(xData).strip("[]")
        print "ydata: " + str(yData).strip("[]")
        print "zdata: " + str(zData).strip("[]")
        print ""
        
        testResult.x_data = xData
        testResult.y_data = yData
        testResult.z_data = zData
        testResult = setResults(testResult, testName, isPassed, params)
    return testResult

def accelOrientationTest(instr, params):
    print "================================="
    print "Performing Accelerometer Orientation Test (test %s/%s)" % (params['testIndex'], params['numTests'])
    print "================================="        
    print ""
    # Check for orientation, if this fails then IO_4 will be asserted. 
    testName = "Accelerometer Orientation Test"

    zData = ''
    zData1 = ''
    zData2 = ''
    zData3 = ''
    pinState = 1
    isPassed = True
    zData = None
    testResult = AccelZDataTest()

    port = params['port']

    result = ''
    raw = ''

    time.sleep(0.5)
    
    (result, raw) = findHeaderFromPortRead("!Z", params)

    print "Result: %s \n" % result

    if result == '':
        print "Error: no data read from serial port.\n"
        isPassed = False
    else:
        try:
            if LIMITED_PIN_SET:
                prefix, zStr, pinResult = result.split(':')
                if pinResult[0] == 'P':
                    pinState = 0
            else:
                prefix, zStr = result.split(':')
        except ValueError:
            print "Error: no ':' read from serial port.\n"
            isPassed = False

        if isPassed:
            try:
                zDataList = zStr.split(',')
            except ValueError:
                print "Error: no ',' read from serial port.\n"
                isPassed = False

        if isPassed:
            if len(zDataList) != 3:
                print "Error: incorrect number of data points read from serial port (%s read, should be 3).\n" % len(zDataList)
                isPassed = False
            else:
                zData1 = int(zDataList[0][0:8],16)
                zData2 = int(zDataList[1][0:8],16)
                zData3 = int(zDataList[2][0:8],16)       
                zData = [zData1, zData2, zData3]     

                counter = 0
                for z in zData:
                    if z > 2 ** 31:
                        z = z - 2 ** 32
                        zData[counter] = z
                        counter += 1

                if max(zData) >= params['z_data_threshold_upper'] or min(zData) <= params['z_data_threshold_lower']:
                    isPassed = False
                    print "\n%s: failed\n" % testName            
                else:
                    print "\n%s: passed\n" % testName                  

                print "zdata: %s %s %s\n" % (zData[0], zData[1], zData[2])

    testResult.z_data = zData
    testResult.pin_state = pinState
    testResult.raw = raw
    testResult = setResults(testResult, testName, isPassed, params)
    return testResult

def accelCurrentTest(instr, params):
    print "================================="
    print "Performing Accelerometer Current Test (test %s/%s)" % (params['testIndex'], params['numTests'])
    print "================================="    
    testName = "Accelerometer Current Test"      

    instr.setRange(0.0001) # 100 uA    # Set current range to microamps   
    instr.setNPLC(100)   
    time.sleep(2)
    testResult = readCurrent(instr, params['num_readings'], params)
    instr.setNPLC(1)
    instr.setRange(params['default_current_range']) # Set current range back to default


    rangeLo = params['accel_current_lower']
    rangeHi = params['accel_current_upper']

    # Compare result against upper/lower bounds and make a pass/fail decision
    if testResult.average >= params['accel_current_lower'] and testResult.average <= params['accel_current_upper']:
        isPassed = True
        print "\n%s: passed\n" % testName
    else:
        isPassed = False
        print "\n%s: Failed: current out of range.  Measured: %s, Range: [%s, %s] \n" % (testName, testResult.average, rangeLo, rangeHi)

    testResult = setResults(testResult, testName, isPassed, params)
    return testResult

def deepSleepTest(instr, params):
    print "================================="
    print "Performing Deep Sleep Test (test %s/%s)" % (params['testIndex'], params['numTests'])
    print "================================="       
    testName = "Deep Sleep Test"      

    time.sleep(1)
    instr.setRange(0.0001) # 100 uA    # Set current range to microamps
    testResult = readCurrent(instr, params['num_readings'], params)
    instr.setRange(params['default_current_range']) # Set current range back to default
    
    rangeLo = params['deep_sleep_current_lower']
    rangeHi = params['deep_sleep_current_upper']

    # Compare result against upper/lower bounds and make a pass/fail decision
    if testResult.average >= rangeLo and testResult.average <= rangeHi:
        isPassed = True
        print "\n%s: passed\n" % testName
    else:
        isPassed = False
        print "\n%s: failed: current out of range.  Measured: %s, Range: [%s, %s] \n" % (testName, testResult.average, rangeLo, rangeHi)

    testResult = setResults(testResult, testName, isPassed, params)
    return testResult

def operatingCurrentTest(instr, params):
    print "================================="
    print "Performing Operating Current Test" 
    print "================================="       
    testName = "Operating Current Test"  

    avgOperatingCurrent = 0

    # Set PLC to 1
    instr.setNPLC(1)
    # instr.setRange(0.0001) # 100 uA    # Set current range to microamps        

    # Wait a moment for Agilent to register change
    time.sleep(2)

    if DEVICE_TYPE == "Silvretta" or DEVICE_TYPE == "BMW":
        #  Need to wait until start up animations finish to get an accurate current reading.
        time.sleep(7)

    # Read current
    testResult = readCurrent(instr, params['num_readings_baseline'], params)

    # Set PLC back to 10
    instr.setRange(params['default_current_range']) # Set current range back to default    
    instr.setNPLC(10)

    operatingCurrents = testResult.currents
    print "\nOperating currents: "
    print operatingCurrents
    print ""

    filetimestamp = datetime.datetime.utcnow().strftime("%Y_%m_%d_%H%M")  
    labels = {}
    labels['x_label'] = 'Reading index'
    labels['y_label'] = 'Current'
    labels['title'] = 'Operating current measurements'

    name_base = 'opCurrent'
    if SAVE_OP_CURRENT_CSV:
        exportData(testResult.currents, ["sample_index","current"],name_base,filetimestamp)
    if SAVE_OP_CURRENT_PNG:
        exportFigure(testResult.currents,name_base,filetimestamp, labels)

    # This function finds the lowest average current in a sliding window
    slidingAvg = []
    localAvg = 0
    for i in range(0, len(operatingCurrents)-params['baseline_window_size']):
        localAvg = np.mean(operatingCurrents[i:i+params['baseline_window_size']])
        slidingAvg.append(localAvg)

    labels['x_label'] = 'Window index'
    labels['y_label'] = 'Mean current in window'
    labels['title'] = 'Operating current window measurements'

    name_base = 'opCurrentWinAvg'
    if SAVE_OP_CURRENT_CSV:    
        exportData(slidingAvg, ["window_index","avg_current"],name_base,filetimestamp)
    if SAVE_OP_CURRENT_PNG:    
        exportFigure(slidingAvg,name_base,filetimestamp, labels)

    slidingAvgSorted = np.sort(slidingAvg)
    avgOperatingCurrent = np.mean(slidingAvgSorted[0:5])

    testResult.average = avgOperatingCurrent
    print "Average operating current: %s" % avgOperatingCurrent

    rangeLo = params['oper_curr_thresh_lower']
    rangeHi = params['oper_curr_thresh_upper']

    # TODO: We want an expanded threshold for fw 28, this is a quick & dirty fix. Need to make more robust.
    if DEVICE_TYPE == 'Apollo' and params['fw_rev'] is not None:
        fw_rev = params['fw_rev']
        if fw_rev.find('28') > 1:
            rangeHi = APOLLO_OPER_CURR_THRESH_UPPER_28R

    # Compare result against upper/lower bounds and make a pass/fail decision
    if testResult.average >= rangeLo and testResult.average <= rangeHi:
        isPassed = True
        print "\n%s: passed\n" % testName
    else:
        isPassed = False
        print "\n%s: failed: current out of range.  Measured: %s, Range: [%s, %s] \n" % (testName, testResult.average, rangeLo, rangeHi)

    testResult = setResults(testResult, testName, isPassed, params) 
    return testResult

def findHeaderFromPortRead(header, params):
    port = params['port']
    counter = 0
    line = ""
    raw = ""

    while counter < 5:

    # Read line on serial port
        line = port.readline()
        raw = " ".join(hex(ord(n)) for n in line)
        line = parseUartData(line)

        if line.find(header) != -1:
            break

        counter += 1

    if counter >= 5:
        line = ""
        raw = ""

    return (line, raw)

def getMACTest(instr, params):
    print "================================="
    print "Performing Get Mac Address Test (test %s/%s)" % (params['testIndex'], params['numTests'])
    print "================================="       
    testName = "Get Mac Address Test"      

    raw = ""
    result = ""
    isPassed = False

    if DEVICE_TYPE == 'SAM':
        header = "!M"
    elif MCU == "Ambiq":
        header = "!MAC"
    else:
        header = "!MA"

    (result, raw) = findHeaderFromPortRead(header, params)

    print "Result: " 
    print result
    print ""
    if raw == '':
        isPassed = False
        print "\nMac address not received!\n"   
    else:
        try:
            prefix = ""
            macStr = ""
            if DEVICE_TYPE == "BMW" or DEVICE_TYPE == "Silvretta":
                macStr = result[-12:]
                prefix = result[-21:-17]
            else:
                prefix, macStr = result.split(':')
                
            if len(macStr) < 12:
                print "\nError: MAC address too short."
                isPassed = False
            elif prefix[-4:] == header:
                result = macStr[-12:]
                isPassed = True
            else:
                print "\nIncorrect header.  Expecting " + header + " and read back " + prefix
                isPassed = False
        except ValueError:
            print "Error: Mac address not received!\n"
            isPassed = False   

    print "Final ieee address: %s \n" % result

    if not isPassed:
        result = "0"

    testResult = MacAddressTest(macRaw=raw,
                                macMasked=result)
    testResult = setResults(testResult, testName, isPassed, params)

    return testResult

def getRSSITest(bleController, params):
    print "================================="
    print "Performing RSSI Test" 
    print "================================="       
    testName = "RSSI Test"     
    print ""

    # Send command to read RSSI
    testResult = RSSIValueTest()
    results = readRSSI(bleController)
    rssi = results[1]
    timeout = results[0]

    bleController.device.rssi = rssi
    testResult.average_rssi = rssi
    testResult.rssi_values = rssi

    if rssi >= params['rssi_lower'] and rssi <= params['rssi_upper']:
        isPassed = True
        print "\n%s: passed\n" % testName
    else:
        isPassed = False
        print "\n%s: failed.  RSSI out of range.\n" % testName 

    if timeout:
        testResult = setTimeoutResults(testName, timeout, params)
    else:
        testResult = setResults(testResult, testName, isPassed, params)
    return testResult

def getAverageRssiTest(bleController, params):
    print "================================="
    print "Performing Average RSSI Test" 
    print "================================="       
    testName = "Average RSSI Test"     
    print ""

    # Send command to read RSSI
    testResult = AverageRssiTest()
    results = getAverageRSSI(bleController)
    average_rssi = results[1]
    timeout = results[0]

    bleController.device.rssi = average_rssi
    bleController.device.average_rssi = average_rssi
    testResult.average_rssi = average_rssi

    if average_rssi >= params['rssi_average_lower'] and average_rssi <= params['rssi_average_upper']:
        isPassed = True
        print "\n%s: passed\n" % testName
    else:
        isPassed = False
        print "\n%s: failed.  Average RSSI out of range.\n" % testName 

    if timeout:
        testResult = setTimeoutResults(testName, timeout, params)
    else:
        testResult = setResults(testResult, testName, isPassed, params)
    return testResult

def perTest(bleController, params):
    print "================================="
    print "Performing Packet Error Rate Test" 
    print "================================="       
    testName = "Packet Error Rate Test"     
    print ""

    # Send command to read RSSI
    testResult = AverageRssiTest()
    results = getAverageRSSI(bleController)
    average_rssi = results[1]
    timeout = results[0]

    bleController.device.rssi = average_rssi
    bleController.device.average_rssi = average_rssi
    testResult.average_rssi = average_rssi

    if average_rssi >= params['rssi_lower'] and average_rssi <= params['rssi_upper']:
        isPassed = True
        print "\n%s: passed\n" % testName
    else:
        isPassed = False
        print "\n%s: failed.  Average RSSI out of range.\n" % testName 

    if timeout:
        testResult = setTimeoutResults(testName, timeout, params)
    else:
        testResult = setResults(testResult, testName, isPassed, params)
    return testResult

def writeSNTest(bleController, params):
    print "================================="
    print "Performing Write SN Test" 
    print "================================="       
    testName = "Write Serial Number Test"    
    serial_number = params['serial_number']

    testResult = WriteSerialTest()
    testResult.serial_number = serial_number
    bleController.serial_done = False

    print "\nWritten SN: %s\n" % serial_number
    snResults = writeSN(bleController, serial_number)
    timeout = snResults[0]
    writeFailed = snResults[1]

    if not writeFailed:
        print "\n%s: passed\n" % testName
    else:
        print "\n%s: may have passed, check Read Serial Number Test." % testName
        # print "\n%s: failed\n" % testName

    # Pass the test if we don't timeout and if the write succeeds
    # isPassed = not writeFailed and not timeout 

    # Always pass unless there's a timeout -- use Read Serial Number Test to check if write succeeded
    isPassed = not timeout 

    if timeout:
        testResult = setTimeoutResults(testName, timeout, params)
    else:
        testResult = setResults(testResult, testName, isPassed, params)
    return testResult

def getSNTest(bleController, params):
    print "================================="
    print "Performing Read SN Test" 
    print "================================="       
    testName = "Read Serial Number Test"    
    serial_to_check = params['serial_number']

    print "\nSerial number to check: %s" % serial_to_check

    print ""
    testResult = ReadSerialTest()
    testResult.serial_to_check = serial_to_check
    results = readSN(bleController)
    serial_number = results[1]
    timeout = results[0]

    print ""
    if timeout:
        testResult = setTimeoutResults(testName, timeout, params)
    else:
        testResult.serial_from_device = serial_number
        
        if serial_number == serial_to_check:
            isPassed = True
            print "Serial Number read: " + serial_number
        else:
            isPassed = False
            print "Serial numbers do not match: %s (to check), %s (from device)" % (serial_to_check, serial_number)

        testResult = setResults(testResult, testName, isPassed, params)
    return testResult

def batteryBTTest(bleController, params):
    print "================================="
    print "Performing Battery Base and Load Voltage Difference BT Test" 
    print "=================================\n"    
    testName = "Battery Base and Load Voltage Difference BT Test"

    #stopLedAnimation(bleController)

    #time.sleep(1) # delay 1 second to ensure boost is turned off

    results = getBatteryValue(bleController)
    battery_base_voltage = results[1]
    battery_load_voltage = results[2]    
    timeout = results[0]

    base_load_voltage_difference = battery_base_voltage - battery_load_voltage

    rangeLo_base = params['batt_base_voltage_lower']
    rangeHi_base = params['batt_base_voltage_upper']

    rangeLo_load = params['batt_load_voltage_lower']
    rangeHi_load = params['batt_load_voltage_upper']

    base_load_voltage_difference_limit = params['batt_base_load_voltage_difference_limit']

    print ""
    if timeout:
        testResult = setTimeoutResults(testName, timeout, params)
    else:
        # Compare result against upper/lower bounds and make a pass/fail decision
        #if battery_base_voltage >= rangeLo_base and battery_load_voltage >= rangeLo_load and battery_base_voltage <= rangeHi_base and battery_load_voltage <= rangeHi_load:
        # If the battery base voltage is greater than or equal to 2.75V and the difference of the base and load voltages is less than or equal to 100 mV, pass.
        if battery_base_voltage >= rangeLo_base and base_load_voltage_difference <= base_load_voltage_difference_limit:
            isPassed = True
            print "\n%s: passed\n" % testName
        else:
            isPassed = False
            #print "\n%s: failed: battery voltage out of range.  Measured: %s (base) / %s (load), Range: [%s, %s] (base) / [%s, %s] (load) \n" % (testName, battery_base_voltage, battery_load_voltage, rangeLo_base, rangeHi_base, rangeLo_load, rangeHi_load)
            print "\n%s: failed: Base battery voltage.  Measured: %s (base) / %s (base and load voltage difference), [%s] (base min limit) / [%s] (base and load voltage difference max limit) \n" % (testName, battery_base_voltage, base_load_voltage_difference, rangeLo_base, base_load_voltage_difference_limit)
        testResult = BatteryTest(isPassed=isPassed,
                                baseLoadDifference=base_load_voltage_difference, 
                                baseVoltage=battery_base_voltage,
                                loadVoltage=battery_load_voltage)
        testResult = setResults(testResult, testName, isPassed, params)
    return testResult

def captouchBTTest(bleController, params):
    print "================================="
    print "Performing Captouch BT Test" 
    print "=================================\n"    
    testName = "Captouch BT Test"

    results = getCaptouchValue(bleController)
    captouch_value = results[1]  
    timeout = results[0]

    rangeLo = params['captouch_bt_capacitance_lower']
    rangeHi = params['captouch_bt_capacitance_upper']

    print ""
    if timeout:
        testResult = setTimeoutResults(testName, timeout, params)
    else:
        # Compare result against upper/lower bounds and make a pass/fail decision
        if captouch_value >= rangeLo and captouch_value <= rangeHi:
            isPassed = True
            print "\n%s: passed\n" % testName
        else:
            isPassed = False
            print "\n%s: failed: captouch value out of range.  Measured: %s , Range: [%s, %s]\n" % (testName, captouch_value, rangeLo, rangeHi)

        testResult = CaptouchTest(isPassed=isPassed, 
                                captouchValue=captouch_value)
        testResult = setResults(testResult, testName, isPassed, params)
    return testResult

def vibeBTTest(bleController, params):
    print "================================="
    print "Performing Vibe BT Test" 
    print "=================================\n"    
    testName = "Vibe BT Test"

    print "Performing vibe calibration"
    performVibeCalibration(bleController)

    time.sleep(10) #delay 10 seconds to allow vibe calibration to complete.
    closeLink(bleController)

    print "Reconnecting to device..."
    connectToDevice(bleController)

    time.sleep(0.25) # Short delay between commands
    setupCharacteristics(bleController)

    time.sleep(0.25) # Short delay between commands
    results = getVibeValue(bleController)
    vibe_value = results[1]  
    timeout = results[0]

    rangeLo = params['vibe_bt_frequency_lower']
    rangeHi = params['vibe_bt_frequency_upper']

    stopLedAnimation(bleController)
    time.sleep(1)

    print ""
    if timeout:
        testResult = setTimeoutResults(testName, timeout, params)
    else:
        # Compare result against upper/lower bounds and make a pass/fail decision
        if vibe_value >= rangeLo and vibe_value <= rangeHi:
            isPassed = True
            print "\n%s: passed\n" % testName
        else:
            isPassed = False
            print "\n%s: failed: vibe frequency out of range.  Measured: %s , Range: [%s, %s]\n" % (testName, vibe_value, rangeLo, rangeHi)

        testResult = VibeBTTest(isPassed=isPassed, 
                                vibeValue=vibe_value)
        testResult = setResults(testResult, testName, isPassed, params)
    return testResult

def ledBTSelfTest(bleController, params):
    print "================================="
    print "Performing LED BT Self Test" 
    print "=================================\n"    
    testName = "LED BT Self Test"

    result = performLedSelfTest(bleController)
    open_leds = result[1]  
    timeout = result[0]
    isPassed = False

    print ""
    if timeout:
        testResult = setTimeoutResults(testName, timeout, params)
    else:
        try:
            result = open_leds

            if result != 0x0FFF:
                isPassed = False
                errorMessage = ''

                # findout which LED failed
                # Example: 0x0FFE means LED 1 failed
                num_bits = 16
                bits = [(result >> bit) & 1 for bit in range(0, 12, 1)]
                 
                errorMessage = ''
                failedCounter = 0
                counter = 0

                for position, bit in enumerate(bits):
                    if not bit:
                        failedCounter += 1

                counter = failedCounter

                for position, bit in enumerate(bits):
                    if not bit:
                        
                        counter -= 1
                        if counter == 0 and failedCounter > 2:
                            errorMessage += ", and "
                            
                        errorMessage += "LED " + str(position + 1)
                        
                        if counter > 1:
                            errorMessage += ", "

                        if counter == 1 and failedCounter == 2:
                            errorMessage += " and "

                errorMessage += " failed self test."
                result = errorMessage
            else:
                isPassed = True
                result = "LED self test passed."

        except ValueError:
            print "Error: Result not received!\n"
            result = "Didn't receive result."

    
        
        testResult = LEDSelfTest(isPassed=isPassed, 
                                result=result)
        testResult = setResults(testResult, testName, isPassed, params)
    return testResult

def magBTSelfTest(bleController, params):
    print "================================="
    print "Performing Mag BT Self Test" 
    print "=================================\n"    
    testName = "Mag BT Self Test"

    result = performMagSelfTest(bleController)
    mag_result = result[1]  
    timeout = result[0]
    isPassed = False

    print ""
    if timeout:
        testResult = setTimeoutResults(testName, timeout, params)
    else:
        if mag_result == 1:
            isPassed = True
        else:
            isPassed = False
    
        
        testResult = MagSelfTest(isPassed=isPassed, 
                                result=mag_result)
        testResult = setResults(testResult, testName, isPassed, params)
    return testResult

def resetViaBTtest(bleController, params):
    print "================================="
    print "Performing Reset via BT" 
    print "=================================" 
    print ""   
    testName = "Reset via BT"

    testResult = ResetViaBTtest()
    results = resetViaBT(bleController)
    reset_done = results[1]
    timeout = results[0]

    if timeout:
        testResult = setTimeoutResults(testName, timeout, params)
    else:
        if reset_done == True:
            isPassed = True
            print "\n%s: passed\n" % testName
        else:
            isPassed = False
            print "\n%s: failed\n" % testName

        testResult = ResetViaBTtest(isPassed=isPassed)
        testResult = setResults(testResult, testName, isPassed, params)
    return testResult

def duplicateSerialNumTest(instr, params):
    print "================================="
    print "Performing Duplicate Serial Number Test"
    print "=================================\n"       
    testName = "Duplicate Serial Number Test"  
    ieee_address = params['ieee_address']
    serial_number = params['serial_number']

    isPassed = True
    if serial_number == '9876543210':
        print "Warning: default serial number 9876543210."
        isPassed = False
    else:
        device = MDapi.misfitProductionGetDeviceWith(ieee_address, serial_number)
        print str(device)
        if device != -1:
            if device['is_duplicated']:
                print "DUPLICATE!"
                isPassed = False
        else:
            isPassed = False
    print ""

    testResult = DuplicateSNTest(serialNumber=serial_number)
    testResult = setResults(testResult, testName, isPassed, params) 
    return testResult

def recentSyncTest(instr, params):
    print "================================="
    print "Performing Recent Sync Test"
    print "=================================\n"       
    testName = "Recent Sync Test"  
    serial_number = params['serial_number']

    startDate = datetime.date.today()
    endDate = startDate - datetime.timedelta(days=30)
    startDateStr = startDate.strftime('%Y-%m-%d')
    endDateStr = endDate.strftime('%Y-%m-%d')
    print startDateStr + " - " + endDateStr
    syncData = pgdb.getSyncMetaData('shine_prod','serial_number', str(serial_number), startDateStr, endDateStr)
    print "Sync Data: "
    print syncData
    print ""

    if len(syncData) > 1:
         isPassed = False
    else:
        isPassed = True

    testResult = RecentSyncTest()
    testResult = setResults(testResult, testName, isPassed, params) 
    return testResult

def batteryPlotTest(instr, params):
    print "================================="
    print "Performing Battery Plot Test"
    print "=================================\n"       
    testName = "Battery Plot Test"  
    serial_number = params['serial_number']

    startDateStr = '2013-07-01'
    endDate = datetime.date.today() - datetime.timedelta(days=30)
    endDateStr = endDate.strftime('%Y-%m-%d')
    print "Getting battery data..."    
    if CLI_MODE and True:
        subprocess.call(["/home/pi/misfit/Production/src/scripts/runBatteryTests.sh", str(serial_number), startDateStr, endDateStr],stderr=subprocess.STDOUT)        
        # Read status from file
        sf = open(BATTERY_PASSED_FILE,'r')
        passed = sf.readline()
        sf.close()
        print "Passed: %s" % passed        
    else:
        (bat, reset) = pgdb.getBatteryWithResetData('shine_prod','serial_number', str(serial_number), startDateStr, endDateStr)
        passed = pgdb.plotActivityBatterryReset(bat, reset, input, startDateStr, endDateStr, params)
    print ""
    if not passed:
        isPassed = False
    else:
        isPassed = True

    testResult = BatteryPlotTest()
    testResult = setResults(testResult, testName, isPassed, params) 
    return testResult

def vibeTest(instr, params):
    # Get vibe varience
    print "================================="
    print "Performing Vibe Test (test %s/%s)" % (params['testIndex'], params['numTests'])
    print "================================="    
    testName = "Vibe Test"
    testResult = VibeTest()
    isPassed = False
    result = ''
    raw = ''
    port = params['port']
    value = ''
    magnitude = ''

    (result, raw) = findHeaderFromPortRead("!VVT", params)

    print "\nResult: "
    print result
    print ""

    rangeMagnitudeLo = params['vibe_magnitude_lower']
    rangeMagnitudeHi = params['vibe_magnitude_upper']

    try:
        prefix, result = result.split(':')
        value, magnitude = result.split(',')
        value = int(value)
        magnitude = int(magnitude)
        if prefix[-4:] == "!VVT": #VVT = Vibration Variance Test
            # Compare result against upper/lower bounds and make a pass/fail decision
            if (magnitude >= rangeMagnitudeLo and magnitude <= rangeMagnitudeHi):
                isPassed = True
                print "\n%s: passed\n" % testName
            else:
                isPassed = False
                print "\n%s: failed: Variance out of range.  Measured magnitude: %s, Range: [%s, %s]\n" % (testName, magnitude, rangeMagnitudeLo, rangeMagnitudeHi)
        else:
            print "\nIncorrect header.  Expecting !VVT and read back " + prefix

    except ValueError:
        print "Error: no ':' read from serial port. Result not received!\n"


    testResult.vibeValue = value
    testResult.vibeMagnitude = magnitude
    testResult.raw = raw
  
    testResult = setResults(testResult, testName, isPassed, params)
    return testResult

def peak_freq_mag(data, fs, freq_in):

    data = array('I', data)

    #get length
    N = len(data)
    
    #tolerance for picking max frequency (in Hz)
    tolerance = 5

    data = np.array(data)
    #remove mean
    data = data - np.mean(data)

    #apply window function
    window = np.hamming(N)
    data = data*window

    #calculate the fft with 1Hz resolution
    data_fft = np.fft.fft(data, fs)
    
    #get absolute value
    data_fft = np.absolute(data_fft)
    
    #get dB units
    data_fft = 10*np.log10(data_fft)

    #generate the frequency index corresponding to the length of the data
    freq_ind = range(0, fs, 1)

    #look for the peak frequency in the +/- 5Hz range of the input frequency
    mag = data_fft[range(freq_in-tolerance, freq_in+tolerance+1,1)]
    max_index, max_mag = max(enumerate(mag), key=operator.itemgetter(1))
    max_freq = max_index + freq_in - tolerance
    
    return (max_freq, max_mag)

def audioTest(instr, params):
    # Measuring the current consumption on the DUT
    # Also measure the frequency and dB 
    print "================================="
    print "Performing Audio Test (test %s/%s)" % (params['testIndex'], params['numTests'])
    print "================================="    
    testName = "Audio Test"
    testResult = AudioTest()
    p = pyaudio.PyAudio()
    stream = p.open(format = pyaudio.paInt16, channels = 1, rate = 44100, input = True, output = True, frames_per_buffer = 2048)
    frequency = 1
    magnitude = 1

    """
    record audio for 0.5 seconds
    analyze data
    """
    try:
        data = stream.read(2048)
    except:
        print "Unable to get audio data"

    (frequency, magnitude) = peak_freq_mag(data, 44100, 500)

    rangeFreqLo = params['audio_frequency_lower']
    rangeFreqHi = params['audio_frequency_upper']
    rangeMagnitudeLo = params['audio_magnitude_lower']
    rangeMagnitudeHi = params['audio_magnitude_upper']

    # Clean close stream and terminate pyaudio
    stream.stop_stream()
    stream.close()
    p.terminate()
    time.sleep(0.5)

    # Compare result against upper/lower bounds and make a pass/fail decision
    if frequency >= rangeFreqLo and frequency <= rangeFreqHi and magnitude >= rangeMagnitudeLo and magnitude <= rangeMagnitudeHi:
        isPassed = True
        print "\n%s: passed\n" % testName
    else:
        isPassed = False
        print "\n%s: failed: Audio out of range.  Measured frequency: %s, Range: [%s, %s] Measured magnitude: %s, Range: [%s, %s]\n" % (testName, frequency, rangeFreqLo, rangeFreqHi, magnitude, rangeMagnitudeLo, rangeMagnitudeHi)

    testResult.frequency = frequency
    testResult.magnitude = magnitude

    testResult = setResults(testResult, testName, isPassed, params)
    return testResult

def parseUartData(data):

    # Ambiq MCU outputs data on SWO which sends trace packets. The data needs to be parsed without the packets.
    # First remove all \x01 bytes
    result = "".join(data.split('\x01'))

    # Next remove \xb4\x80\x80\x80\x00
    result = "".join(result.split('\xb4\x80\x80\x80\x00'))

    # Next remove \x20\x20\x10\x90\xf0
    result = "".join(result.split('\x20\x20\x10\x90\xf0'))

    # Next remove \x20\x10\x90\xf0\xd
    result = "".join(result.split('\x20\x10\x90\xf0\x0d'))

    # Next remove \x94\x80\x80\x80\x00

    result = "".join(result.split('\x94\x80\x80\x80\x00'))
    
    # remove \x00
    result = "".join(result.split('\x00'))

    # remove \n
    result = "".join(result.split('\n'))

    # Finally remove \r
    result = "".join(result.split('\r'))

    return result


def captouchTest(instr, params):
    # Measuring the current consumption on the DUT
    # Also do a readback of the value on the sense line..
    print "================================="
    print "Performing Captouch Test (test %s/%s)" % (params['testIndex'], params['numTests'])
    print "================================="    
    testName = "Captouch Test"
    testResult = CaptouchTest()
    isPassed = False
    result = ''
    raw = ''
    port = params['port']
    
    (result, raw) = findHeaderFromPortRead("!CTT", params)

    print "\nResults: "
    print result
    print ""

    rangeLo = params['captouch_capacitance_lower']
    rangeHi = params['captouch_capacitance_upper']

    try:
        prefix, result = result.split(':')
        result = int(result)
        if prefix[-4:] == "!CTT":
            # Compare result against upper/lower bounds and make a pass/fail decision
            if result >= rangeLo and result <= rangeHi:
                isPassed = True
                print "\n%s: passed\n" % testName
            else:
                isPassed = False
                print "\n%s: failed: Capacitance out of range.  Measured: %s, Range: [%s, %s] \n" % (testName, result, rangeLo, rangeHi)
        else:
            print "\nIncorrect header.  Expecting !CTT and read back " + prefix

    except ValueError:
        print "Error: Result not received!\n"

    testResult.captouchValue = result
    testResult.raw = raw
  
    testResult = setResults(testResult, testName, isPassed, params)
    return testResult

def vibeCurrentTest(instr, params):
    # Measuring the current consumption on the DUT
    print "================================="
    print "Performing Vibe Current Test (test %s/%s)" % (params['testIndex'], params['numTests'])
    print "================================="    
    testName = "Vibe Current Test"

    instr.setRange(params['default_current_range']) # Set current range back to default
    instr.setNPLC(1)
    time.sleep(0.75)
    testResult = readCurrent(instr, params['num_readings'], params)

    rangeLo = params['vibe_current_lower']
    rangeHi = params['vibe_current_upper']

   # Compare result against upper/lower bounds and make a pass/fail decision
    if testResult.average >= rangeLo and testResult.average <= rangeHi:
        isPassed = True
        print "\n%s: passed\n" % testName
    else:
        isPassed = False
        print "\n%s: Failed: current out of range.  Measured: %s, Range: [%s, %s] \n" % (testName, testResult.average, rangeLo, rangeHi)
    
    testResult = setResults(testResult, testName, isPassed, params)

    return testResult

def vibeBTCurrentTest(bleController, params):
    # Measuring the current consumption on the DUT
    print "================================="
    print "Performing Vibe Current Test"
    print "================================="    
    testName = "Vibe Current Test"
    instr = params['instr']

    stopLedAnimation(bleController)
    time.sleep(1)

    vibeAtFrequency(bleController)
    instr.setRange(params['default_current_range']) # Set current range back to default
    instr.setNPLC(100)
    time.sleep(2)
    testResult = readCurrent(instr, params['num_readings'], params)
    stopVibe(bleController)

    rangeLo = params['vibe_current_lower']
    rangeHi = params['vibe_current_upper']

   # Compare result against upper/lower bounds and make a pass/fail decision
    if testResult.average >= rangeLo and testResult.average <= rangeHi:
        isPassed = True
        print "\n%s: passed\n" % testName
    else:
        isPassed = False
        print "\n%s: Failed: current out of range.  Measured: %s, Range: [%s, %s] \n" % (testName, testResult.average, rangeLo, rangeHi)
    
    testResult = setResults(testResult, testName, isPassed, params)

    return testResult

def audioCurrentTest(instr, params):
    # Measuring the current consumption on the DUT
    print "================================="
    print "Performing Audio Current Test (test %s/%s)" % (params['testIndex'], params['numTests'])
    print "================================="    
    testName = "Audio Current Test"

    instr.setRange(params['default_current_range']) # Set current range back to default
    instr.setNPLC(1)
    time.sleep(0.75)
    testResult = readCurrent(instr, params['num_readings'], params)

    rangeLo = params['audio_current_lower']
    rangeHi = params['audio_current_upper']

    # Compare result against upper/lower bounds and make a pass/fail decision
    if testResult.average >= rangeLo and testResult.average <= rangeHi:
        isPassed = True
        print "\n%s: passed\n" % testName
    else:
        isPassed = False
        print "\n%s: Failed: current out of range.  Measured: %s, Range: [%s, %s] \n" % (testName, testResult.average, rangeLo, rangeHi)
    
    testResult = setResults(testResult, testName, isPassed, params)

    return testResult

def captouchCurrentTest(instr, params):
    # Measuring the current consumption on the DUT
    print "================================="
    print "Performing Captouch Current Test (test %s/%s)" % (params['testIndex'], params['numTests'])
    print "================================="    
    testName = "Captouch Current Test"

    instr.setRange(0.0001) # 100 uA    # Set current range to microamps   
    instr.setNPLC(100)   
    time.sleep(2)
    testResult = readCurrent(instr, params['num_readings'], params)
    instr.setNPLC(1)
    instr.setRange(params['default_current_range']) # Set current range back to default

    rangeLo = params['captouch_current_lower']
    rangeHi = params['captouch_current_upper']

    # Compare result against upper/lower bounds and make a pass/fail decision
    if testResult.average >= rangeLo and testResult.average <= rangeHi:
        isPassed = True
        print "\n%s: passed\n" % testName
    else:
        isPassed = False
        print "\n%s: Failed: current out of range.  Measured: %s, Range: [%s, %s] \n" % (testName, testResult.average, rangeLo, rangeHi)
    
    testResult = setResults(testResult, testName, isPassed, params)

    return testResult

def pogoPinTest(instr, params):
    # Measuring pogo pin resistance
    print "================================="
    print "Performing Pogo Pin Test"
    print "================================="    

    testName = "Pogo Pin Test"

    setGpioPin(POGOPIN_RELAY_PIN)
    time.sleep(0.05)
    setGpioPin(POGOPIN_TEST_PIN)
    # check pogo impedance
    instr.setModeToResistance()
    pogoResistance = instr.getReading()
    instr.setModeToCurrent() 

    clearGpioPin(POGOPIN_TEST_PIN)
    clearGpioPin(POGOPIN_RELAY_PIN)

    pogoPinTestPassed = True

    if pogoResistance >= params['pogoMaxResistance']:
        pogoPinTestPassed = False

    testResult = PogoPinTest(isPassed=pogoPinTestPassed, value=(str(pogoResistance) + " ohms"))

    testResult = setResults(testResult, testName, pogoPinTestPassed, params)
    return testResult

def captouchProgramming(instr, params):
    # Check captouch programming
    print "================================="
    print "Captouch Programming (test %s/%s)" % (params['testIndex'], params['numTests'])
    print "================================="    
    testName = "Captouch Programming"
    port = params['port']
    isPassed = False

    result = ''
    raw = ''

    (result, raw) = findHeaderFromPortRead("!CTP", params)

    print "\nResults: "
    print result
    print ""

    try:
        prefix, result = result.split(':')

        if prefix[-4:] == "!CTP":
            if result[0] == 'P':
                result = 'Captouch programming successful'
                isPassed = True
            else:
                result = 'Captouch programming failed'
        else:
            print "\nIncorrect header.  Expecting !CTP and read back " + prefix

    except ValueError:
        print "Error: Result not received!\n"
        isPassed = False 
        result = "Didn't receive result."

    testResult = CaptouchProgramming(result=result)
    testResult.raw = raw

    testResult = setResults(testResult, testName, isPassed, params)
    return testResult


def playSoundTest(bleController, params):
    print "================================="
    print "Performing Play Sound Test" 
    print "================================="       
    testName = "Play Sound Test"    

    testResult = AudioTest()
    bleController.serial_done = False

    results = playSound(bleController, 500)
    timeout = results[0]
    writeFailed = results[1]

    if not writeFailed:
        print "\n%s: passed\n" % testName
        # print "\n%s: failed\n" % testName

    # Pass the test if we don't timeout and if the write succeeds
    # isPassed = not writeFailed and not timeout 

    # Always pass unless there's a timeout -- use Read Serial Number Test to check if write succeeded
    isPassed = not timeout 

    if timeout:
        testResult = setTimeoutResults(testName, timeout, params)
    else:
        testResult = setResults(testResult, testName, isPassed, params)
    return testResult

def ledSelfTest(instr, params):
    print "================================="
    print "Performing LED Self Test (test %s/%s)" % (params['testIndex'], params['numTests'])
    print "================================="    
    testName = "LED Self Test"
    testResult = LEDSelfTest()
    isPassed = False
    result = ''
    raw = ''
    port = params['port']

    (result, raw) = findHeaderFromPortRead("!LST", params)

    print "\nResults: "
    print result
    print ""

    try:
        prefix, result = result.split(':')
        result = int(result, 16)
        if prefix[-4:] == "!LST":

            if result != 0x0FFF:
                isPassed = False
                errorMessage = ''

                # findout which LED failed
                # Example: 0x0FFE means LED 1 failed
                num_bits = 16
                bits = [(result >> bit) & 1 for bit in range(0, 12, 1)]
                 
                errorMessage = ''
                failedCounter = 0
                counter = 0

                for position, bit in enumerate(bits):
                    if not bit:
                        failedCounter += 1

                counter = failedCounter

                for position, bit in enumerate(bits):
                    if not bit:
                        
                        counter -= 1
                        if counter == 0 and failedCounter > 2:
                            errorMessage += ", and "
                            
                        errorMessage += "LED " + str(position + 1)
                        
                        if counter > 1:
                            errorMessage += ", "

                        if counter == 1 and failedCounter == 2:
                            errorMessage += " and "

                errorMessage += " failed self test."
                result = errorMessage
            else:
                isPassed = True
                result = "LED self test passed."
        else:
            print "\nIncorrect header.  Expecting !LST and read back " + prefix

    except ValueError:
        print "Error: Result not received!\n"
        result = "Didn't receive result."

    testResult.result = result
    testResult.raw = raw

    testResult = setResults(testResult, testName, isPassed, params)
    return testResult

def magSelfTest(instr, params):
    # Check mag self test
    print "================================="
    print "Mag Self Test (test %s/%s)" % (params['testIndex'], params['numTests'])
    print "================================="    
    testName = "Mag Self Test"
    port = params['port']
    isPassed = False

    result = ''
    raw = ''

    (result, raw) = findHeaderFromPortRead("!MST", params)

    print "\nResults: "
    print result
    print ""

    try:
        prefix, result = result.split(':')

        if prefix[-4:] == "!MST":
            if result[0] == 'P':
                result = 'Mag self test passed.'
                isPassed = True
            else:
                result = 'Mag self test failed.'
        else:
            print "\nIncorrect header.  Expecting !MST and read back " + prefix

    except ValueError:
        print "Error: Result not received!\n"
        isPassed = False 
        result = "Didn't receive result."

    testResult = MagSelfTest(result=result)
    testResult.raw = raw

    testResult = setResults(testResult, testName, isPassed, params)
    return testResult

def crystalTest(instr, params):
    print "================================="
    print "Performing Crystal Test (test %s/%s)" % (params['testIndex'], params['numTests'])
    print "================================="       
    testName = "Crystal Test"      

    isPassed = False

    rangeLo = params['crystal_duration_lower']
    rangeHi = params['crystal_duration_upper']

    testResult = CrystalTest()

    start = time.time()
    duration = 0
    toggleDuration = 0

    startPinState = gpio_ns_read(MFG_TOGGLE_PIN) # read the initial pin state

    newPinState = startPinState 

    # Wait or the pin state change.  If it doesn't, there is likely a crystal error.
    while startPinState == newPinState and (duration < 1):
        # Read pin state
        newPinState = gpio_ns_read(MFG_TOGGLE_PIN)
        # Measure time that has passed
        duration = time.time() - start

    if duration < 1:
        # Record start time when the pin changes state
        startTime = time.time()
        startPinState = newPinState
        duration = 0
        start = time.time()

        while startPinState == newPinState and (duration < 1):
            newPinState = gpio_ns_read(MFG_TOGGLE_PIN)
            duration = time.time() - start

        if duration < 1:

            toggleDuration = time.time() - startTime

            print "Duration of toggle is " + str(toggleDuration)

            # Compare result against upper/lower bounds and make a pass/fail decision
            if toggleDuration >= rangeLo and toggleDuration <= rangeHi:
                isPassed = True
                print "\n%s: passed\n" % testName
            else:
                isPassed = False
                print "\n%s: Failed: Toggle time is out of range.  Measured: %s, Range: [%s, %s] \n" % (testName, toggleDuration, rangeLo, rangeHi)

            testResult.toggleDuration = toggleDuration
        else:
            isPassed = False
            print "Pin did not change back to original state."
    else:
        isPassed = False
        print "Pin did not change from initial state."

    testResult = setResults(testResult, testName, isPassed, params)

    return testResult

def captouchBTCalibration(bleController, params):
    print "================================="
    print "Performing Captouch BT Calibration" 
    print "=================================\n"    
    testName = "Captouch BT Calibration"

    results = performCaptouchCalibration(bleController)
    captouch_comp_idac = results[2]  
    captouch_mod_idac = results[1]  
    timeout = results[0]
    isPassed = False

    rangeLo = params['captouch_mod_comp_idac_lower']
    rangeHi = params['captouch_mod_comp_idac_upper']

    print ""
    if timeout:
        testResult = setTimeoutResults(testName, timeout, params)
    else:
        # Compare result against upper/lower bounds and make a pass/fail decision
        if captouch_comp_idac >= rangeLo and captouch_comp_idac <= rangeHi and captouch_mod_idac >= rangeLo and captouch_mod_idac <= rangeHi:
            isPassed = True
            print "\n%s: passed\n" % testName
        else:
            isPassed = False
            print "Failed captouch calibration.  Measured MOD IDAC: %s, Range: [%s, %s]  Measured COMP IDAC: %s, Range: [%s, %s]\n" % (captouch_mod_idac, rangeLo, rangeHi, captouch_comp_idac, rangeLo, rangeHi)

        testResult = CaptouchBTCalibration(isPassed=isPassed, modIdac=captouch_mod_idac, compIdac=captouch_comp_idac)
        testResult = setResults(testResult, testName, isPassed, params)

    return testResult

def vibeBTMagnitudeTest(bleController, params):

    print "================================="
    print "Performing Vibe BT Magnitude Test"
    print "================================="   

    testResult = VibeBTMagnitudeTest()
    testName = "Vibe BT Magnitude Test"
    result = getVibeMagnitude(bleController)
    magnitude = result[1]  
    timeout = result[0]
    isPassed = False

    rangeMagnitudeLo = params['vibe_magnitude_lower']
    rangeMagnitudeHi = params['vibe_magnitude_upper']


    if timeout:
        testResult = setTimeoutResults(testName, timeout, params)
    else:
        # Compare result against upper/lower bounds and make a pass/fail decision
        if (magnitude >= rangeMagnitudeLo and magnitude <= rangeMagnitudeHi):
            isPassed = True
            print "\n%s: passed\n" % testName
        else:
            isPassed = False
            print "\n%s: failed: Magnitude out of range.  Measured magnitude: %s, Range: [%s, %s]\n" % (testName, magnitude, rangeMagnitudeLo, rangeMagnitudeHi)
           

        testResult = VibeBTMagnitudeTest(magnitudeValue=magnitude)   
        testResult = setResults(testResult, testName, isPassed, params)

    return testResult

def drvPartIdTest(instr, params):
    # Check DRV Part ID
    print "================================="
    print "DRV Part ID Test (test %s/%s)" % (params['testIndex'], params['numTests'])
    print "================================="    
    testName = "DRV Part ID Test"
    port = params['port']
    isPassed = False

    result = ''
    raw = ''

    (result, raw) = findHeaderFromPortRead("!DST", params)

    print "\nResults: "
    print result
    print ""

    try:
        prefix, result = result.split(':')

        if prefix[-4:] == "!DST":
            if result[0] == 'P':
                result = 'DRV part ID is correct'
                isPassed = True
            else:
                result = 'DRV part ID is incorrect'
        else:
            print "\nIncorrect header.  Expecting !DST and read back " + prefix

    except ValueError:
        print "Error: Result not received!\n"
        isPassed = False 
        result = "Didn't receive result."

    testResult = DrvPartIdTest(result=result)
    testResult.raw = raw

    testResult = setResults(testResult, testName, isPassed, params)
    return testResult

def rtcPartIdTest(instr, params):
    # Check RTC Part ID
    print "================================="
    print "RTC Part ID Test (test %s/%s)" % (params['testIndex'], params['numTests'])
    print "================================="    
    testName = "RTC Part ID Test"
    port = params['port']
    isPassed = False

    result = ''
    raw = ''

    (result, raw) = findHeaderFromPortRead("!RST", params)

    print "\nResults: "
    print result
    print ""

    try:
        prefix, result = result.split(':')

        if prefix[-4:] == "!RST":
            if result[0] == 'P':
                result = 'RST part ID is correct'
                isPassed = True
            else:
                result = 'RST part ID is incorrect'
        else:
            print "\nIncorrect header.  Expecting !RST and read back " + prefix

    except ValueError:
        print "Error: Result not received!\n"
        isPassed = False 
        result = "Didn't receive result."

    testResult = RtcPartIdTest(result=result)
    testResult.raw = raw

    testResult = setResults(testResult, testName, isPassed, params)
    return testResult

def drvCalibration(instr, params):
    # Check DRV calibration
    print "================================="
    print "DRV Calibration (test %s/%s)" % (params['testIndex'], params['numTests'])
    print "================================="    
    testName = "DRV Calibration"
    port = params['port']
    isPassed = False

    result = ''
    raw = ''

    (result, raw) = findHeaderFromPortRead("!DCT", params)

    print "\nResults: "
    print result
    print ""

    try:
        prefix, result = result.split(':')

        if prefix[-4:] == "!DCT":
            if result[0] == 'P':
                result = 'DRV calibration successful'
                isPassed = True
            else:
                result = 'DRV calibration failed'
        else:
            print "\nIncorrect header.  Expecting !DCT and read back " + prefix

    except ValueError:
        print "Error: Result not received!\n"
        isPassed = False 
        result = "Didn't receive result."

    testResult = DrvCalibration(result=result)
    testResult.raw = raw

    testResult = setResults(testResult, testName, isPassed, params)
    return testResult

def allMovementsCwCurrentTest(instr, params):
    print "================================="
    print "Performing All Movements Clockwise Current Test (test %s/%s)" % (params['testIndex'], params['numTests'])
    print "================================="     
    testName = "All Movements Clockwise Current Test"     

    rangeLo = params['all_movement_current_lower']
    rangeHi = params['all_movement_current_upper']

    instr.setRange(params['default_current_range']) # 100 uA    # Set current range to microamps   
    instr.setNPLC(1)   
    time.sleep(1)
    testResult = readCurrent(instr, params['num_readings'], params)
    #instr.setNPLC(1)
    instr.setRange(params['default_current_range']) # Set current range back to default
    #time.sleep(3)
    # Compare result against upper/lower bounds and make a pass/fail decision
    if testResult.average > rangeLo and testResult.average < rangeHi:
        isPassed = True
        print "\n%s: passed\n" % testName
    else:
        isPassed = False
        print "\n%s: failed: current out of range.  Measured: %s, Range: [%s, %s] \n" % (testName, testResult.average, rangeLo, rangeHi)

    testResult = setResults(testResult, testName, isPassed, params)
    return testResult

def allMovementsCcwCurrentTest(instr, params):
    print "================================="
    print "Performing All Movements Counter-Clockwise Current Test (test %s/%s)" % (params['testIndex'], params['numTests'])
    print "================================="     
    testName = "All Movements Counter-Clockwise Current Test"     

    rangeLo = params['all_movement_current_lower']
    rangeHi = params['all_movement_current_upper']

    instr.setRange(params['default_current_range']) # 100 uA    # Set current range to microamps   
    instr.setNPLC(1)   
    time.sleep(1)
    testResult = readCurrent(instr, params['num_readings'], params)
    #instr.setNPLC(1)
    instr.setRange(params['default_current_range']) # Set current range back to default
    #time.sleep(3)
    # Compare result against upper/lower bounds and make a pass/fail decision
    if testResult.average > rangeLo and testResult.average < rangeHi:
        isPassed = True
        print "\n%s: passed\n" % testName
    else:
        isPassed = False
        print "\n%s: failed: current out of range.  Measured: %s, Range: [%s, %s] \n" % (testName, testResult.average, rangeLo, rangeHi)

    testResult = setResults(testResult, testName, isPassed, params)
    return testResult

def movement1CwCurrentTest(instr, params):
    print "================================="
    print "Performing Movement 1 Clockwise Current Test (test %s/%s)" % (params['testIndex'], params['numTests'])
    print "================================="     
    testName = "Movement 1 Clockwise Current Test"     

    rangeLo = params['movement_current_lower']
    rangeHi = params['movement_current_upper']

    instr.setRange(params['default_current_range']) # 100 uA    # Set current range to microamps   
    instr.setNPLC(1)   
    time.sleep(1)
    testResult = readCurrent(instr, params['num_readings'], params)
    #instr.setNPLC(1)
    instr.setRange(params['default_current_range']) # Set current range back to default
    #time.sleep(3)
    # Compare result against upper/lower bounds and make a pass/fail decision
    if testResult.average > rangeLo and testResult.average < rangeHi:
        isPassed = True
        print "\n%s: passed\n" % testName
    else:
        isPassed = False
        print "\n%s: failed: current out of range.  Measured: %s, Range: [%s, %s] \n" % (testName, testResult.average, rangeLo, rangeHi)

    testResult = setResults(testResult, testName, isPassed, params)
    return testResult   

def movement1CcwCurrentTest(instr, params):
    print "================================="
    print "Performing Movement 1 Counter-Clockwise Current Test (test %s/%s)" % (params['testIndex'], params['numTests'])
    print "================================="     
    testName = "Movement 1 Counter-Clockwise Current Test"     

    rangeLo = params['movement_current_lower']
    rangeHi = params['movement_current_upper']

    instr.setRange(params['default_current_range']) # 100 uA    # Set current range to microamps   
    instr.setNPLC(1)   
    time.sleep(1)
    testResult = readCurrent(instr, params['num_readings'], params)
    #instr.setNPLC(1)
    instr.setRange(params['default_current_range']) # Set current range back to default
    #time.sleep(3)
    # Compare result against upper/lower bounds and make a pass/fail decision
    if testResult.average > rangeLo and testResult.average < rangeHi:
        isPassed = True
        print "\n%s: passed\n" % testName
    else:
        isPassed = False
        print "\n%s: failed: current out of range.  Measured: %s, Range: [%s, %s] \n" % (testName, testResult.average, rangeLo, rangeHi)

    testResult = setResults(testResult, testName, isPassed, params)
    return testResult      

def movement2CwCurrentTest(instr, params):
    print "================================="
    print "Performing Movement 2 Clockwise Current Test (test %s/%s)" % (params['testIndex'], params['numTests'])
    print "================================="     
    testName = "Movement 2 Clockwise Current Test"     

    rangeLo = params['movement_current_lower']
    rangeHi = params['movement_current_upper']

    instr.setRange(params['default_current_range']) # 100 uA    # Set current range to microamps   
    instr.setNPLC(1)   
    time.sleep(1)
    testResult = readCurrent(instr, params['num_readings'], params)
    #instr.setNPLC(1)
    instr.setRange(params['default_current_range']) # Set current range back to default
    #time.sleep(3)
    # Compare result against upper/lower bounds and make a pass/fail decision
    if testResult.average > rangeLo and testResult.average < rangeHi:
        isPassed = True
        print "\n%s: passed\n" % testName
    else:
        isPassed = False
        print "\n%s: failed: current out of range.  Measured: %s, Range: [%s, %s] \n" % (testName, testResult.average, rangeLo, rangeHi)

    testResult = setResults(testResult, testName, isPassed, params)
    return testResult   

def movement2CcwCurrentTest(instr, params):
    print "================================="
    print "Performing Movement 2 Counter-Clockwise Current Test (test %s/%s)" % (params['testIndex'], params['numTests'])
    print "================================="     
    testName = "Movement 2 Counter-Clockwise Current Test"     

    rangeLo = params['movement_current_lower']
    rangeHi = params['movement_current_upper']

    instr.setRange(params['default_current_range']) # 100 uA    # Set current range to microamps   
    instr.setNPLC(1)   
    time.sleep(1)
    testResult = readCurrent(instr, params['num_readings'], params)
    #instr.setNPLC(1)
    instr.setRange(params['default_current_range']) # Set current range back to default
    #time.sleep(3)
    # Compare result against upper/lower bounds and make a pass/fail decision
    if testResult.average > rangeLo and testResult.average < rangeHi:
        isPassed = True
        print "\n%s: passed\n" % testName
    else:
        isPassed = False
        print "\n%s: failed: current out of range.  Measured: %s, Range: [%s, %s] \n" % (testName, testResult.average, rangeLo, rangeHi)

    testResult = setResults(testResult, testName, isPassed, params)
    return testResult       

def movement3CwCurrentTest(instr, params):
    print "================================="
    print "Performing Movement 3 Clockwise Current Test (test %s/%s)" % (params['testIndex'], params['numTests'])
    print "================================="     
    testName = "Movement 3 Clockwise Current Test"     

    rangeLo = params['movement_current_lower']
    rangeHi = params['movement_current_upper']

    instr.setRange(params['default_current_range']) # 100 uA    # Set current range to microamps   
    instr.setNPLC(1)   
    time.sleep(1)
    testResult = readCurrent(instr, params['num_readings'], params)
    #instr.setNPLC(1)
    instr.setRange(params['default_current_range']) # Set current range back to default
    #time.sleep(3)
    # Compare result against upper/lower bounds and make a pass/fail decision
    if testResult.average > rangeLo and testResult.average < rangeHi:
        isPassed = True
        print "\n%s: passed\n" % testName
    else:
        isPassed = False
        print "\n%s: failed: current out of range.  Measured: %s, Range: [%s, %s] \n" % (testName, testResult.average, rangeLo, rangeHi)

    testResult = setResults(testResult, testName, isPassed, params)
    return testResult         
    
def movement3CcwCurrentTest(instr, params):
    print "================================="
    print "Performing Movement 3 Counter-Clockwise Current Test (test %s/%s)" % (params['testIndex'], params['numTests'])
    print "================================="     
    testName = "Movement 3 Counter-Clockwise Current Test"     

    rangeLo = params['movement_current_lower']
    rangeHi = params['movement_current_upper']

    instr.setRange(params['default_current_range']) # 100 uA    # Set current range to microamps   
    instr.setNPLC(1)   
    time.sleep(1)
    testResult = readCurrent(instr, params['num_readings'], params)
    #instr.setNPLC(1)
    instr.setRange(params['default_current_range']) # Set current range back to default
    #time.sleep(3)
    # Compare result against upper/lower bounds and make a pass/fail decision
    if testResult.average > rangeLo and testResult.average < rangeHi:
        isPassed = True
        print "\n%s: passed\n" % testName
    else:
        isPassed = False
        print "\n%s: failed: current out of range.  Measured: %s, Range: [%s, %s] \n" % (testName, testResult.average, rangeLo, rangeHi)

    testResult = setResults(testResult, testName, isPassed, params)
    return testResult        

def boostCurrentTest(instr, params):
    print "================================="
    print "Performing Boost Current Test (test %s/%s)" % (params['testIndex'], params['numTests'])
    print "================================="     
    testName = "Boost Current Test"     

    rangeLo = params['boost_current_lower']
    rangeHi = params['boost_current_upper']

    instr.setRange(0.01)#0001) # 100 uA    # Set current range to microamps   
    instr.setNPLC(100)   
    time.sleep(2)
    testResult = readCurrent(instr, params['num_readings'], params)
    instr.setNPLC(1)
    instr.setRange(params['default_current_range']) # Set current range back to default

    # Compare result against upper/lower bounds and make a pass/fail decision
    if testResult.average > rangeLo and testResult.average < rangeHi:
        isPassed = True
        print "\n%s: passed\n" % testName
    else:
        isPassed = False
        print "\n%s: failed: current out of range.  Measured: %s, Range: [%s, %s] \n" % (testName, testResult.average, rangeLo, rangeHi)

    testResult = setResults(testResult, testName, isPassed, params)
    return testResult

def pusherPushTest(instr, params):
    print "================================="
    print "Performing Pusher Push Test (test %s/%s)" % (params['testIndex'], params['numTests'])
    print "================================="    
    testName = "Pusher Push Test"
    testResult = PusherPushTest()
    isPassed = False
    result = ''
    raw = ''
    port = params['port']

    # wait for toggle change state
    start = time.time()
    timeout = 4
    duration = 0
    toggleDuration = 0

    startPinState = gpio_ns_read(MFG_TOGGLE_PIN) # read the initial pin state
    newPinState = startPinState #save state

    # Wait for the pin state change. Starting pusher push test. 
    while startPinState == newPinState and (duration < 1):
        # Read pin state
        newPinState = gpio_ns_read(MFG_TOGGLE_PIN)
        # Measure time that has passed
        duration = time.time() - start

    if duration < timeout:
        start = time.time() # reset start time
        duration = 0 # reset duration

        # wait for toggle change state
        startPinState = gpio_ns_read(MFG_TOGGLE_PIN) # read the initial pin state
        newPinState = startPinState 

        # acutate pistons
        activatePusherPistions()

        # Wait for the pin state change. Starting pusher release test
        while startPinState == newPinState and (duration < timeout):
            # Read pin state
            newPinState = gpio_ns_read(MFG_TOGGLE_PIN)
            # Measure time that has passed
            duration = time.time() - start

        if duration < timeout:
            start = time.time() # reset start time
            duration = 0 # reset duration

            # deactivate pusher pistons
            startPinState = gpio_ns_read(MFG_TOGGLE_PIN) # read the initial pin state
            newPinState = startPinState 

            deactivatePusherPistons()

            # Wait for the pin state change. Read data
            while startPinState == newPinState and (duration < timeout):
                # Read pin state
                newPinState = gpio_ns_read(MFG_TOGGLE_PIN)
                # Measure time that has passed
                duration = time.time() - start


            if duration < timeout:

                # read data
                (result, raw) = findHeaderFromPortRead("!PRT", params)

                print "\nResults: "
                print result
                print ""

                try:
                    prefix, result = result.split(':')
                    result = int(result, 16)
                    if prefix[-4:] == "!PRT":

                        if result != 0x7:
                            isPassed = False
                            errorMessage = ''

                            # findout which LED failed
                            # Example: 0x0FFE means LED 1 failed
                            num_bits = 3
                            bits = [(result >> bit) & 1 for bit in range(0, 3, 1)]
                             
                            errorMessage = ''
                            failedCounter = 0
                            counter = 0

                            for position, bit in enumerate(bits):
                                if not bit:
                                    failedCounter += 1

                            counter = failedCounter

                            for position, bit in enumerate(bits):
                                if not bit:
                                    
                                    counter -= 1
                                    if counter == 0 and failedCounter > 2:
                                        errorMessage += ", and "
                                        
                                    errorMessage += "Pusher " + str(position + 1)
                                    
                                    if counter > 1:
                                        errorMessage += ", "

                                    if counter == 1 and failedCounter == 2:
                                        errorMessage += " and "

                            errorMessage += " failed push test."
                            result = errorMessage
                        else:
                            isPassed = True
                            result = "Pusher push test passed."
                    else:
                        print "\nIncorrect header.  Expecting !PTT and read back " + prefix

                except ValueError:
                    print "Error: Result not received!\n"
                    result = "Didn't receive result."

                testResult.result = result
                testResult.raw = raw
            else:
                isPassed = False
                testResult.result = "Device timed out."

        else:
            #timeout from dut
            isPassed = False
            testResult.result = "Device timed out."
    else:
        # time out from dut
        isPassed = False
        testResult.result = "Device timed out."

    deactivatePusherPistons() #deactivate pistions 
    testResult = setResults(testResult, testName, isPassed, params)
    return testResult


def dummyPusherPushTest(instr, params):
    """
    Need this to help keep ATE 1 in sync with the tests.  There are 
    TOGGLE state changes that gets ATE 1 out of sync with the DUT.
    """
    print "================================="
    print "Performing Dummy Pusher Push Test (test %s/%s)" % (params['testIndex'], params['numTests'])
    print "================================="  
    print ""  
    testName = "Dummy Pusher Push Test"

    # wait for toggle change state
    start = time.time()
    timeout = 4
    duration = 0
    toggleDuration = 0

    startPinState = gpio_ns_read(MFG_TOGGLE_PIN) # read the initial pin state
    newPinState = startPinState #save state

    # Wait for the pin state change. Starting pusher push test. 
    while startPinState == newPinState and (duration < 1):
        # Read pin state
        newPinState = gpio_ns_read(MFG_TOGGLE_PIN)
        # Measure time that has passed
        duration = time.time() - start

    if duration < timeout:
        start = time.time() # reset start time
        duration = 0 # reset duration

        # wait for toggle change state
        startPinState = gpio_ns_read(MFG_TOGGLE_PIN) # read the initial pin state
        newPinState = startPinState 

        # acutate pistons
        #activatePusherPistions()

        # Wait for the pin state change. Starting pusher release test
        while startPinState == newPinState and (duration < timeout):
            # Read pin state
            newPinState = gpio_ns_read(MFG_TOGGLE_PIN)
            # Measure time that has passed
            duration = time.time() - start

        if duration < timeout:
            start = time.time() # reset start time
            duration = 0 # reset duration

            # deactivate pusher pistons
            startPinState = gpio_ns_read(MFG_TOGGLE_PIN) # read the initial pin state
            newPinState = startPinState 

            # Wait for the pin state change. Read data
            while startPinState == newPinState and (duration < timeout):
                # Read pin state
                newPinState = gpio_ns_read(MFG_TOGGLE_PIN)
                # Measure time that has passed
                duration = time.time() - start


    # Flush the buffer of the UART data.
    port = params['port']
    line = port.readline()

    port.flushInput()


def pusherReleaseTest(instr, params):
    print "================================="
    print "Performing Pusher Release Test (test %s/%s)" % (params['testIndex'], params['numTests'])
    print "================================="    
    testName = "Pusher Release Test"
    testResult = PusherReleaseTest()
    isPassed = False
    result = ''
    raw = ''
    port = params['port']

    (result, raw) = findHeaderFromPortRead("!PRT", params)

    print "\nResults: "
    print result
    print ""

    try:
        prefix, result = result.split(':')
        result = int(result, 16)
        if prefix[-4:] == "!PRT":

            if result != 0x7:
                isPassed = False
                errorMessage = ''

                # findout which LED failed
                # Example: 0x0FFE means LED 1 failed
                num_bits = 3
                bits = [(result >> bit) & 1 for bit in range(0, 3, 1)]
                 
                errorMessage = ''
                failedCounter = 0
                counter = 0

                for position, bit in enumerate(bits):
                    if not bit:
                        failedCounter += 1

                counter = failedCounter

                for position, bit in enumerate(bits):
                    if not bit:
                        
                        counter -= 1
                        if counter == 0 and failedCounter > 2:
                            errorMessage += ", and "
                            
                        errorMessage += "Pusher " + str(position + 1)
                        
                        if counter > 1:
                            errorMessage += ", "

                        if counter == 1 and failedCounter == 2:
                            errorMessage += " and "

                errorMessage += " failed release test."
                result = errorMessage
            else:
                isPassed = True
                result = "Pusher release test passed."
        else:
            print "\nIncorrect header.  Expecting !PRT and read back " + prefix

    except ValueError:
        print "Error: Result not received!\n"
        result = "Didn't receive result."

    testResult.result = result
    testResult.raw = raw

    testResult = setResults(testResult, testName, isPassed, params)
    return testResult


def crystalCalibrationTest(instr, params):
    print "================================="
    print "Performing Crystal Calibration Test (test %s/%s)" % (params['testIndex'], params['numTests'])
    print "================================="  
    print ""  
    testName = "Crystal Calibration Test"
    testResult = CrystalCalibrationTest()
    # wait for toggle change state
    start = time.time()
    timeout = 10
    duration = 0
    toggleDuration = 0

    isPassed = False
    result = ''
    raw = ''
    value = 0

    startPinState = gpio_ns_read(MFG_TOGGLE_PIN) # read the initial pin state
    newPinState = startPinState #save state

    # Wait for the pin state change. Starting crystal calibration test. 
    while startPinState == newPinState and (duration < 1):
        # Read pin state
        newPinState = gpio_ns_read(MFG_TOGGLE_PIN)
        # Measure time that has passed
        duration = time.time() - start


    if duration < timeout:
        #start = time.time() # reset start time
        duration = 0 # reset duration

        # Connect the function generator to DUT by closing relay connection.
        # Use GPIO 12 to close the connection when set high.
        gpio_ns_write(CRYSTAL_CAL_PIN, GPIO_HI)

        startPinState = gpio_ns_read(MFG_TOGGLE_PIN) # read the initial pin state
        newPinState = startPinState #save state
        start = time.time()

        # Wait for the pin state change to read data. 
        while startPinState == newPinState and (duration < timeout):
            # Read pin state
            newPinState = gpio_ns_read(MFG_TOGGLE_PIN)
            # Measure time that has passed
            duration = time.time() - start

        # Open relay because test is done.  Need to disconnect function generator
        # output.
        gpio_ns_write(CRYSTAL_CAL_PIN, GPIO_LO)

        if duration < timeout:

            # Read UART DATA
            port = params['port']

            (result, raw) = findHeaderFromPortRead("!CCT", params)

            print "Results: "
            print result
            print ""

            try:
                prefix, result = result.split(':')

                # Expecting !CCT:value,result
                # value is the calibration value from the device
                # result is either P = pass, F = failed, or T = timeout.
                if prefix[-4:] == "!CCT":

                    value, result = result.split(',')

                    if result == 'P':
                        isPassed = True
                    else:
                        isPassed = False
                else:
                    print "\nIncorrect header.  Expecting !CCT and read back " + prefix

            except ValueError:
                print "Error: Result not received!\n"
                isPassed = False 
                result = "Didn't receive result."
        else:
            # time out from dut
            isPassed = False
            testResult.result = "Device timed out."
    else:
        # time out from dut
        isPassed = False
        testResult.result = "Device timed out."

    # Redundant call to disconnect function generator just in case.
    gpio_ns_write(CRYSTAL_CAL_PIN, GPIO_LO)

    testResult.calibrationValue = value
    testResult.raw = raw

    testResult = setResults(testResult, testName, isPassed, params)
    return testResult

def vibeBTCalibration(bleController, params):
    """
    This function is used in SAM for calibrating the vibrator.

    """
    print "================================="
    print "Performing Vibe BT Calibration" 
    print "=================================\n"    
    testName = "Vibe BT Calibration"

    testResult = VibeBTCalibration()

    bleController.vibe_over_voltage = params['vibe_overvoltage']
    bleController.vibe_rated_voltage = params['vibe_ratedvoltage'] 
    results = drvVibeCalibration(bleController, OVERDRIVE_1000, RATED_1000)

    time.sleep(1)
    timeout = results[0]

    isPassed = False

    print ""
    if timeout:
        testResult = setTimeoutResults(testName, timeout, params)
    else:
        # Calibration result is in result[1]
        if results[1]: 
            isPassed = True
            testResult.vibe_over_voltage = params['vibe_overvoltage']
            testResult.vibe_rated_voltage = params['vibe_ratedvoltage']
            
            print "\n%s: passed\n" % testName
        else:
            isPassed = False
            print "Failed vibe calibration."


        testResult = setResults(testResult, testName, isPassed, params)

    return testResult

def setHandPositions(bleController, params):
    """
    This function is used in SAM for setting the hand postions based on the brand and platform.

    """
    print "================================="
    print "Performing BT Set Hand Postions" 
    print "=================================\n"    
    testName = "BT Set Hand Postions"   
    isPassed = False
    timeout = False
    testResult = BTSetHandPositions()
    current_position = None

    brand_platform = params['serial_number'][2:4] # get the brand and platform from serial number.  this will determine hand positions.
    position = ''
    if brand_platform in handPositions:
        position = handPositions[brand_platform]
        print "Getting hand positions"

    bleController.hand_positions = position

    setHandShipPositions(bleController)

    time.sleep(3)

    results = getHandPositions(bleController)

    timeout = results[0]

    position = ''.join( [ "%02X" % ord( x ) for x in position ] ).strip()
    print "Expected position: " + position
    if not timeout:
        current_position = results[1]

        if current_position == position:
            print "Successfully moved hands to ship positions"
            isPassed = True # setting always true for now, dont' have a response from the device yet.

        else:

            print "Failed to move hands to ship positions"

    testResult.current_position = current_position
    testResult.expected_position = position

    testResult = setResults(testResult, testName, isPassed, params)

    return testResult



def setUtcTime(bleController, params):
    """
    This function is used in SAM for setting the local UTC time.
    To verify the device time has been set, ATE will get the device time and 
    take the difference between that time and the current time.  If that 
    difference is less than the defined limit, it will be considered passed.

    """
    print "================================="
    print "Performing BT Set Time" 
    print "=================================\n"    
    testName = "BT Set Time"  

    timeout = False
    deviceTime = 0 
    isPassed = False
    testResult = None

    # Send BLE command to set time.
    setTime(bleController)

    testResult = BTSetTime()

    # Delay before next command
    time.sleep(BLE_DELAY)

    # Send BLE command to get time.
    results = getTime(bleController)
    timeout = results[0]

    if not timeout:
        deviceTime = results[1]

        now = time.time()

        # Take the difference between the when the time was set and the current time.
        difference = now - deviceTime

        # If the time difference is less than the maximum allowed difference, this means the device has been programmed.
        if difference <= params['time_difference_max']: # If the device time has been programmed
            testResult.device_time = deviceTime
            isPassed = True

        # Save the difference to the database.
        testResult.difference = difference

        testResult = setResults(testResult, testName, isPassed, params)
    else:
        testResult = setTimeoutResults(testName, timeout, params)

    return testResult

#####################
# JUST FOR DATA COLLECTION. REMOVE LATER
"""
Need to calibrate using each test and get vibe strength for each one to 
try to correlate current and vibe strength.
"""
def vibeBTCalibration1(bleController, params):
    """
    This function is used in SAM for calibrating the vibrator.

    """
    print "================================="
    print "Performing Vibe BT Calibration 200 200" 
    print "=================================\n"    
    testName = "Vibe BT Calibration 200 200"

    testResult = VibeBTCalibration()

    results = drvVibeCalibration1(bleController)

    time.sleep(0.25)

    magResults = getVibeMagnitude(bleController)

    timeout = results[0]

    isPassed = False

    print ""
    if timeout:
        testResult = setTimeoutResults(testName, timeout, params)
    else:
        # Calibration result is in result[1]
        if results[1]: 
            isPassed = True
            testResult.magnitude = magResults[1]
            print "\n%s: passed\n" % testName
        else:
            isPassed = False
            print "Failed vibe calibration."


        testResult = setResults(testResult, testName, isPassed, params)

    return testResult

def vibeBTCalibration2(bleController, params):
    """
    This function is used in SAM for calibrating the vibrator.

    """
    print "================================="
    print "Performing Vibe BT Calibration 400 400" 
    print "=================================\n"    
    testName = "Vibe BT Calibration 400 400"

    testResult = VibeBTCalibration()

    results = drvVibeCalibration2(bleController)

    time.sleep(0.25)

    magResults = getVibeMagnitude(bleController)

    timeout = results[0]

    isPassed = False

    print ""
    if timeout:
        testResult = setTimeoutResults(testName, timeout, params)
    else:
        # Calibration result is in result[1]
        if results[1]: 
            isPassed = True
            testResult.magnitude = magResults[1]
            print "\n%s: passed\n" % testName
        else:
            isPassed = False
            print "Failed vibe calibration."


        testResult = setResults(testResult, testName, isPassed, params)

    return testResult

def vibeBTCalibration3(bleController, params):
    """
    This function is used in SAM for calibrating the vibrator.

    """
    print "================================="
    print "Performing Vibe BT Calibration 600 600" 
    print "=================================\n"    
    testName = "Vibe BT Calibration 600 600"

    testResult = VibeBTCalibration()

    results = drvVibeCalibration3(bleController)

    time.sleep(0.25)

    magResults = getVibeMagnitude(bleController)

    timeout = results[0]

    isPassed = False

    print ""
    if timeout:
        testResult = setTimeoutResults(testName, timeout, params)
    else:
        # Calibration result is in result[1]
        if results[1]: 
            isPassed = True
            testResult.magnitude = magResults[1]
            print "\n%s: passed\n" % testName
        else:
            isPassed = False
            print "Failed vibe calibration."


        testResult = setResults(testResult, testName, isPassed, params)

    return testResult

def vibeBTCalibration4(bleController, params):
    """
    This function is used in SAM for calibrating the vibrator.

    """
    print "================================="
    print "Performing Vibe BT Calibration 800 800" 
    print "=================================\n"    
    testName = "Vibe BT Calibration 800 800"

    testResult = VibeBTCalibration()

    results = drvVibeCalibration4(bleController)

    time.sleep(0.25)

    magResults = getVibeMagnitude(bleController)

    timeout = results[0]

    isPassed = False

    print ""
    if timeout:
        testResult = setTimeoutResults(testName, timeout, params)
    else:
        # Calibration result is in result[1]
        if results[1]: 
            isPassed = True
            testResult.magnitude = magResults[1]
            print "\n%s: passed\n" % testName
        else:
            isPassed = False
            print "Failed vibe calibration."


        testResult = setResults(testResult, testName, isPassed, params)

    return testResult

def vibeBTCalibration5(bleController, params):
    """
    This function is used in SAM for calibrating the vibrator.

    """
    print "================================="
    print "Performing Vibe BT Calibration 1000 1000" 
    print "=================================\n"    
    testName = "Vibe BT Calibration 1000 1000"

    testResult = VibeBTCalibration()

    results = drvVibeCalibration5(bleController)

    time.sleep(0.25)

    magResults = getVibeMagnitude(bleController)

    timeout = results[0]

    isPassed = False

    print ""
    if timeout:
        testResult = setTimeoutResults(testName, timeout, params)
    else:
        # Calibration result is in result[1]
        if results[1]: 
            isPassed = True
            testResult.magnitude = magResults[1]
            print "\n%s: passed\n" % testName
        else:
            isPassed = False
            print "Failed vibe calibration."


        testResult = setResults(testResult, testName, isPassed, params)

    return testResult

def vibeBTCalibration6(bleController, params):
    """
    This function is used in SAM for calibrating the vibrator.

    """
    print "================================="
    print "Performing Vibe BT Calibration 1200 1200" 
    print "=================================\n"    
    testName = "Vibe BT Calibration 1200 1200"

    testResult = VibeBTCalibration()

    results = drvVibeCalibration6(bleController)

    time.sleep(0.25)

    magResults = getVibeMagnitude(bleController)

    timeout = results[0]

    isPassed = False

    print ""
    if timeout:
        testResult = setTimeoutResults(testName, timeout, params)
    else:
        # Calibration result is in result[1]
        if results[1]: 
            isPassed = True
            testResult.magnitude = magResults[1]
            print "\n%s: passed\n" % testName
        else:
            isPassed = False
            print "Failed vibe calibration."


        testResult = setResults(testResult, testName, isPassed, params)

    return testResult

def vibeBTCalibration7(bleController, params):
    """
    This function is used in SAM for calibrating the vibrator.

    """
    print "================================="
    print "Performing Vibe BT Calibration 1200 600" 
    print "=================================\n"    
    testName = "Vibe BT Calibration 1200 6"

    testResult = VibeBTCalibration()

    results = drvVibeCalibration7(bleController)

    time.sleep(0.25)

    magResults = getVibeMagnitude(bleController)

    timeout = results[0]

    isPassed = False

    print ""
    if timeout:
        testResult = setTimeoutResults(testName, timeout, params)
    else:
        # Calibration result is in result[1]
        if results[1]: 
            isPassed = True
            testResult.magnitude = magResults[1]
            print "\n%s: passed\n" % testName
        else:
            isPassed = False
            print "Failed vibe calibration."


        testResult = setResults(testResult, testName, isPassed, params)

    return testResult

def vibeBTCalibration8(bleController, params):
    """
    This function is used in SAM for calibrating the vibrator.

    """
    print "================================="
    print "Performing Vibe BT Calibration 900 600" 
    print "=================================\n"    
    testName = "Vibe BT Calibration 900 600"

    testResult = VibeBTCalibration()

    results = drvVibeCalibration8(bleController)

    time.sleep(0.25)

    magResults = getVibeMagnitude(bleController)

    timeout = results[0]

    isPassed = False

    print ""
    if timeout:
        testResult = setTimeoutResults(testName, timeout, params)
    else:
        # Calibration result is in result[1]
        if results[1]: 
            isPassed = True
            testResult.magnitude = magResults[1]
            print "\n%s: passed\n" % testName
        else:
            isPassed = False
            print "Failed vibe calibration."


        testResult = setResults(testResult, testName, isPassed, params)

    return testResult


def packetErrorRateTest(bleController, params):
    """
    Clear the data monitor
    Send packets
    Read Data monitor
    Analyze and report.
    """
    print "================================="
    print "Performing Packet Error Rate Test" 
    print "=================================\n"    
    testName = "Packet Error Rate Test"

    testResult = PerTest()
    totalPackets = {}
    totalErrors = {}
    isPassed = False
    timeout = False

    # Clear the data in the packet monitor.
    clearPacketMonitor(bleController)

    time.sleep(BLE_DELAY)

    # Send data packets to check error rate
    for x in range(0, params['per_packet_count']):
        sendEmptyPacket(bleController)
        time.sleep(0.02)

    time.sleep(BLE_DELAY)

    results = getPacketCountTotal(bleController)
    timeout = results[0]
    if not timeout: #No timeout
        totalPackets = results[1]

        time.sleep(BLE_DELAY)

        results = getPacketCountTotalErrors(bleController)
        timeout = results[0]
        if not timeout:#No timeout
            totalErrors = results[1]

            testResult.total_packets_received = totalPackets['total_packets_received']
            testResult.total_good_packets = totalPackets['total_good_packets']
            testResult.total_crc_errors = totalErrors['total_crc_errors']
            testResult.total_len_errors = totalErrors['total_len_errors']
            testResult.total_mic_errors = totalErrors['total_mic_errors']
            testResult.total_nesn_errors = totalErrors['total_nesn_errors']
            testResult.total_sn_errors = totalErrors['total_sn_errors']
            testResult.total_sync_errors = totalErrors['total_sync_errors']
            testResult.total_type_errors = totalErrors['total_type_errors']
            testResult.total_overflow_errors = totalErrors['total_overflow_errors']

            # Calculate the percentage of successfully sent packets.
            testResult.success_percentage = float(totalPackets['total_good_packets'])/float(totalPackets['total_packets_received']) * 100

            if testResult.success_percentage >= params['per_success_percentage']:
                isPassed = True

            
            testResult = setResults(testResult, testName, isPassed, params)

        else:# Test timed out
            testResult = setTimeoutResults(testName, timeout, params)
    else:# Test timed out
        testResult = setTimeoutResults(testName, timeout, params)

    #Return the result
    return testResult



def boostBTTest(bleController, params):
    """
    This function is used in SAM testing boost functionality.

    """
    print "================================="
    print "Performing Boost BT Test" 
    print "=================================\n"   
    testName = "Boost BT Test"

    testResult = BoostTest()
    noLoadVoltage = None
    loadVoltage = None
    boostVoltage = None
    isPassed = False
    timeout = False



    """ Calibrate device to 1.2V/1.2V """
    print "Calibrating device to 1.2V/1.2V"

    bleController.vibe_over_voltage = params['boost_overvoltage']
    bleController.vibe_rated_voltage = params['boost_ratedvoltage'] 
    results = drvVibeCalibration(bleController, OVERDRIVE_1200, RATED_1200)

    time.sleep(1)
    timeout = results[0]


    print ""
    if timeout:
        isPassed = False
        testResult = setTimeoutResults(testName, timeout, params)
    else:
        # Calibration result is in result[1]
        if results[1]: 
            print "\nCalibration successful\n" 
            isPassed = True
        else:
            print "Failed vibe calibration."
            isPassed = False


    if isPassed:
        results = getBoostVoltage(bleController)
        timeout = results[0]
    
        if not timeout: #No timeout
            noLoadVoltage = results[1]
            loadVoltage = results[2]
            boostVoltage = results[3]
    
            if boostVoltage >= params['boost_voltage_lower'] and boostVoltage <= params['boost_voltage_upper'] and loadVoltage < params['boost_voltage_lower']:
                isPassed = True
    
            testResult.noLoadVoltage = noLoadVoltage
            testResult.loadVoltage = loadVoltage
            testResult.boostVoltage = boostVoltage
    
            testResult = setResults(testResult, testName, isPassed, params)
    
        else:# Test timed out
            testResult = setTimeoutResults(testName, timeout, params)
    else:
        testResult = setTimeoutResults(testName, timeout, params)

    return testResult
