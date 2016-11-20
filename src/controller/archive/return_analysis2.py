'''
Created on 2014-07-30

@author: Rachel Kalmar
'''

from constants import *
from returncodes import *

import os, sys
import collections
import serial
import time
import binascii
import helper.MDapi as MDapi
import datetime
import usbtmc
import numpy
import helper.utils as util
import ast
import subprocess

import helper.mfg_data as MFG
import helper.posgresDB_extractor as pgdb

from pyblehci import BLEBuilder
from pyblehci import BLEParser
from model.device import *
from model.bleDevice import *
from raspberryPi_commands import *
from helper.agilent_34461 import A34461
from stationTests import *
from stationTest_commands import *
from ble_commands import *
from params import *
from pprint import pprint


# Power on and configure the Device Under Test (DUT), instruments, etc.
def __startSequence(instr):

    print "\nInitiating RMA tests for device: %s\n" % DEVICE_TYPE

    internet_on = True

    # Set range, get reading from the Agilent
    instr.setRange(params['default_current_range']) # 100 mA
    if DEBUG_MODE:
        print instr.getReading()

    # Check to see if the internet is on
    if not MDapi.internet_on():
        internet_on = False
        print "\nWarning: RaspberryPi not connected to internet.\n"    
    params['internet_on'] = internet_on

    # Turn on DUT, into customer mode
    configureSuccess = turnOnDUT()

    # Set current local time
    os.environ['TZ'] = TIMEZONE
    time.tzset()
    curr_time = datetime.datetime.now()
    print "Current local time is %s" % datetime.datetime.strftime(curr_time,"%Y-%m-%d %H:%M:%S")

    # Check whether operating current directory exists
    if SAVE_OP_CURRENT_CSV or SAVE_OP_CURRENT_PNG:
        subprocess.call("/home/pi/misfit/ShineProduction/src/scripts/checkOpCurrDirectory.sh")

    return (configureSuccess, params)

# Run the sequence of tests for the DUT
def executeReturnTestSequence(serial_number, serial_number_internal, instr):

    setupSuccess = False
    timeout = False
    overallSuccess = True
    testsCompleted = True
    logentry = {}
    errorlog = []
    results = {}
    allTestResults = []
    ieee_address = None
    ieee_read = False
    fw_rev = None
    rssi = None
    endTests = False

    numTests = len(testOrder)

    logentry['unlocked'] = True                       # Unused
    logentry['station_log_format'] = SCRIPT_VERSION   
    results['logentry'] = logentry

    (setupSuccess, params) = __startSequence(instr)
    logentry['test_began'] = setupSuccess    
    results['setupSuccess'] = setupSuccess  
    logentry['testTimeStart_local'] = datetime.datetime.strftime(datetime.datetime.now(),"%Y-%m-%d %H:%M:%S")
    logentry['testTimeStart_utc'] = time.mktime(datetime.datetime.utcnow().timetuple())

    params['numTests'] = numTests

    print "\nSerial number (entered): %s" % serial_number
    print "Serial number internal (entered): %s\n" % serial_number_internal

    # Get IEEE address from database
    if serial_number_internal is not None:
        (ieee_address, serial_from_database, serial_internal_from_database) = getIEEEfromDatabase(serial_number_internal,'internal')        
        serial_number = serial_from_database
    elif serial_number is not None:
        (ieee_address, serial_from_database, serial_internal_from_database) = getIEEEfromDatabase(serial_number, 'packaging')        
        serial_number_internal = serial_internal_from_database

    params['serial_number'] = serial_number       
    params['serial_number_internal'] = serial_number_internal
    params['ieee_address'] = ieee_address

    print "\nSerial number (from database): %s" % serial_number
    print "Serial number internal (from database): %s\n" % serial_number_internal

    # *****

    # Do RSSI and serial read tests
    (rssi, fw_rev, serial_from_device, allTestResults, error, timeout, bleTestsCompleted) = doBLEtests(ieee_address, serial_number, params, allTestResults)
    print ""

    for test in testOrder:
        testResult = doNextTest(test, instr, params)
        (allTestResults, errorlog, timeout, currentTestIndex, testsCompleted, endTests) = doPostTestSequence(testResult, allTestResults, errorlog, params) 

        if endTests == True:
            break       

    if ieee_address:
        ieee_read = True

    # Store log entries
    logentry['testTimeEnd_local'] = datetime.datetime.strftime(datetime.datetime.now(),"%Y-%m-%d %H:%M:%S")
    logentry['testTimeEnd_utc'] = time.mktime(datetime.datetime.utcnow().timetuple())         
    logentry['params'] = params    
    logentry['timeout'] = timeout
    logentry['testsCompleted'] = testsCompleted
    logentry['ieee_read'] = True    
    logentry['ieee'] = ieee_address 
    logentry['fw_rev'] = fw_rev
    logentry['rssi'] = rssi           
    logentry['serial_number'] = serial_number
    logentry['serial_number_internal'] = serial_number_internal       
    logentry['serial_from_device'] = serial_from_device    
    logentry['errorlog'] = errorlog       

    # Store results
    results['logentry'] = logentry
    results['internet_on'] = params['internet_on']
    results['timeout'] = timeout
    results['testsCompleted'] = testsCompleted
    results['setupSuccess'] = setupSuccess
    results['logentry'] = logentry
    results['allTestResults'] = allTestResults
    results['serial_number'] = serial_number
    results['serial_number_internal'] = serial_number_internal
    results['serial_from_device'] = serial_from_device    
    results['ieee_address'] = ieee_address
    results['rssi'] = rssi
    results['fw_rev'] = fw_rev

    if not setupSuccess:
        print "\nSetup failed. Ending...\n"
    if timeout:
        print "\nTimeout; tests not completed.\n"
    elif testsCompleted:
        print "\nAll tests completed.\n"

    # Do end sequence and send results to database
    overallPass = endSequence(instr, results)

    print "\n\n\n"
    print "RSSI: %s" % rssi
    print "Firmware revision: %s" % fw_rev
    print "Errorlog: %s" % errorlog
    print "Timeout: %s" % timeout
    print "Tests completed: %s" % testsCompleted

    # Return UI to show operator
    if overallPass and params['internet_on']:
        return 0
    elif overallPass:
        return 2
    else:
        return 1
