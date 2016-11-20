'''
Created on 2014-07-07

@author: Rachel Kalmar
'''

from raspberryPi_commands import *
# from model.dut_parameters import DutParameters, FlashRecord, TestRecord
from multiprocessing import Value
from model.device import *
from model.bleDevice import *
from pyblehci import BLEBuilder
from pyblehci import BLEParser
from subprocess import Popen, PIPE
from constants import *
from helper.gpio_no_sudo import *
from helper.agilent_34461 import A34461
from helper.deviceColorLookup import deviceColorLookup
from stationTests import *
from ble_commands import *
from params import *
from testOrder import *
# from testOrderBLE import *
from helper.db_commands import *
from external_commands import *
from gtk_commands import *

import os
import serial
import binascii
import helper.MDapi as MDapi
import datetime
import time
import usbtmc
import numpy
import helper.utils as util
from pprint import pprint
import ast
import subprocess


# Power on and configure the Device Under Test (DUT), instruments, etc.
def __startSequence(instr, numTests, input_type, allTestResults):

    md_api_on = True
    internet_on = True
    port = None
    programming_success = True
    configureSuccess = True
    # programming_done = params['programming_done']

    if input_type == 'cli':
        # Set current local time
        os.environ['TZ'] = TIMEZONE
        time.tzset()
        curr_time = datetime.datetime.now()
        print "\nCurrent local time is %s\n" % datetime.datetime.strftime(curr_time,"%Y-%m-%d %H:%M:%S")
                
        # Initialize the Agilent 34461
        instr = A34461(AGILENT_BASE_ADDRESS, AGILENT_SUB_ADDRESS)
        if instr.instr is not None:
            instr.setModeToCurrent()

        # Initialize the DUT
        initDUT()            

    # Turn on power to DUT
    if MCU == "Ambiq" and PROGRAM_DEVICE: #STATION_ID == 1 or (STATION_ID == 2 and DEVICE_TYPE == 'SAM'):
        unlockToProgram()
    else:
        turnOnDUT()

    if STATION_ID == 1 or (STATION_ID == 2 and DEVICE_TYPE == 'SAM'):
        if True: #PROGRAM_DEVICE:
            # Pause between tests in debug mode
            if DEBUG_MODE:
                choice = raw_input("Hit 'Enter' to continue: ")
                print ""

            if PROGRAM_DEVICE: 
                # Turn on power to programmer
                if DEBUG_MODE:
                    if LUNCHBOX:
                        print "Setting IN_JTAG_VCC_CTL to %s" % GPIO_HI
                    else:
                        print "Setting IN_JTAG_VCC_CTL to %s" % GPIO_LO
                if LUNCHBOX:
                    gpio_ns_pull(MFG_TOGGLE_PIN, "tri")
                    gpio_ns_write(IN_JTAG_VCC_CTL, GPIO_HI)
                else:
                    gpio_ns_write(IN_JTAG_VCC_CTL, GPIO_LO)   

                time.sleep(0.1) # added for time stability.  


                programming_success = runProgrammingSequence()
                testResult = McuProgramming()
                testResult.is_passed = programming_success

                # Add programming step to results
                allTestResults.append(testResult)

                # Pause between tests in debug mode
                if DEBUG_MODE:
                    choice = raw_input("Hit 'Enter' to continue: ")
                    print ""

                # Turn off power to programmer
                if DEBUG_MODE:
                    if LUNCHBOX:
                        print "Setting IN_JTAG_VCC_CTL to %s" % GPIO_LO
                    else:
                        print "Setting IN_JTAG_VCC_CTL to %s" % GPIO_HI
                if LUNCHBOX:
                    gpio_ns_write(IN_JTAG_VCC_CTL, GPIO_LO)
                    gpio_ns_pull(MFG_TOGGLE_PIN, "up")
                else:
                    gpio_ns_write(IN_JTAG_VCC_CTL, GPIO_HI)        

                # Pause between tests in debug mode
                if DEBUG_MODE:
                    choice = raw_input("Hit 'Enter' to continue: ")
                    print ""

                print "Programming success: %s" % programming_success
                print "\nResetting device..."
            # powerCycleDUT("reset")
            # if programming_success:
            if DEVICE_TYPE == "SAM": 
                enterTestModeSequence()  # Use this for new sequence for entering hardware test.
                #configureSuccess = powerCycleDUT("configure")  
            else:
                print "\nConfiguring GPIOs (post-programming)"                    
                configureSuccess = powerCycleDUT("configure") 

            # programming_done = True  
            # else:
            #     configureSuccess = False
            #     programming_done = False
            # params['programming_done'] = programming_done
        elif programming_success:
            # Set GPIO pins to appropriate configuration 
            print "\nConfiguring GPIOs (no programming)"
            configureSuccess = configureGPIOs("configure")   
        else:
            print "Device programming unsuccessful; aborting tests."
            configureSuccess = False

        # Open serial port
        # (TODO: flush this at the beginning)
        try:
            port = serial.Serial(SERIAL_PORT, 
                                baudrate=params['baud_rate'], 
                                timeout=params['serial_timeout'])  
        except:
            print "Could not open serial port (%s); please reset." % SERIAL_PORT
            configureSuccess = False

        if DEBUG_MODE:
            pprint(port)      
    else:
        configureSuccess = True

    # Set range, get reading from the Agilent
    params['dmm_connected'] = True
    if instr.instr is not None:
        try:
            instr.setRange(params['default_current_range']) # 100 mA
        except:
            print "Warning: can't set default current range -- please check Agilent connection"
            configureSuccess = False
            params['dmm_connected'] = False
        try:            
            instr.disableAutoZero()
        except:
            print "Warning: can't disable auto zero -- please check Agilent connection"
            configureSuccess = False 
            params['dmm_connected'] = False           
        if DEBUG_MODE:
            print instr.getReading()
    elif numTests > 0:
        print "Error: Agilent not found. Aborting tests.\n"
        params['dmm_connected'] = False
        configureSuccess = False
                                 
    # Check to see if the internet is on
    if INTERNET_REQUIRED:
        internet_on = checkInternetWithRetries()
    if not internet_on:
        if INTERNET_REQUIRED == True:
            configureSuccess = False
            print "\nError: RaspberryPi not connected to internet. Aborting.\n"            
        else:
            print "\nWarning: RaspberryPi not connected to internet.\n"

    # TODO: figure out appropriate database call
    # # Check to see if the database can be accessed
    md_api_on = checkDatabaseWithRetries()
    if not md_api_on:
        if DATABASE_ACCESS_REQUIRED == True:
            configureSuccess = False
            print "\nError: RaspberryPi can't access database. Aborting.\n"            
        else:
            print "\nWarning: RaspberryPi can't access database.\n"            

    params['port'] = port
    params['md_api_on'] = md_api_on
    params['internet_on'] = internet_on
    params['instr'] = instr

    # If the programming failed, set configureSuccess to False to fail out of the test run and prevent waiting for a timeout.
    if not programming_success:
        configureSuccess = False

    return (configureSuccess, params, instr, allTestResults)

# Run the sequence of tests for the DUT
def executeTestSequence(serial_number, serial_number_internal, serial_number_smt, instr, input_type):

    current_state = 1
    new_state = 0
    currentTestIndex = 1
    ledIndex = 1
    vibeCurrentIndex = 1
    setupSuccess = False
    timeout = False
    testsCompleted = True
    logentry = {}
    errorlog = []
    results = {}
    allTestResults = []
    ieee_address = None
    ieee_read = False
    fw_rev = None
    rssi = None
    serial_from_device = None
    endTests = False
    duplicateEntries = False
    port = None
    voltageTest = None
    ieee_from_database = None

    scriptStartTime = resetTimer()
    logentry['scriptTimeStart_local'] = datetime.datetime.strftime(datetime.datetime.now(),"%Y-%m-%d %H:%M:%S")
    logentry['station_log_format'] = SCRIPT_VERSION   
    results['logentry'] = logentry
    results['is_duplicated'] = False

    # Run start sequence
    numTests = len(testOrder)  
    (setupSuccess, params, instr, allTestResults) = __startSequence(instr, numTests, input_type, allTestResults)    
    logentry['test_began'] = setupSuccess    
    results['setupSuccess'] = setupSuccess   
    testStartTime = resetTimer()
    logentry['testTimeStart_local'] = datetime.datetime.strftime(datetime.datetime.now(),"%Y-%m-%d %H:%M:%S")
    logentry['testTimeStart_utc'] = time.mktime(datetime.datetime.utcnow().timetuple())

    params['numTests'] = numTests
    params['scriptStartTime'] = scriptStartTime
    params['testIndex'] = currentTestIndex
    params['ledIndex'] = ledIndex
    params['vibeCurrentIndex'] = vibeCurrentIndex
    params['ble_dongle_connected'] = False
    params['rotating_plate_error'] = True
    gpio_ns_pull(MFG_INFO_PIN, "alt0")
    gpio_ns_pull(MFG_TOGGLE_PIN, "in")

    time.sleep(0.1)
    print "Pin state check..."
    print "MFG_TRIG_PIN: %d" % gpio_ns_read(MFG_TRIG_PIN)
    print "MFG_INFO_PIN: %d" % gpio_ns_read(MFG_INFO_PIN)
    print "MFG_TOGGLE_PIN: %d" % gpio_ns_read(MFG_TOGGLE_PIN)
    deactivatePusherPistons() # deactivate just in case pistons are stuck

    if STATION_ID == 2 and DEVICE_TYPE == 'SAM' and not MFG_DB_STAGING:
        if not rotatingPlateIsInCorrectPosition(serial_number_internal):
            #print "\nRotating plate is not correct\n"
            params['rotating_plate_error'] = False
            setupSuccess = False

    if setupSuccess:
        print "\nSetup successful\n"    

        print "Initiating Station %s tests for %s" % (STATION_ID, DEVICE_TYPE)
        print "ATE: %s.%s.%s\n" % (ATE_ID, STATION_ID, STATION_INDEX)

        if STATION_ID == 1 or (STATION_ID == 2 and DEVICE_TYPE == 'SAM'):

            if params['md_api_on'] or (DATABASE_ACCESS_REQUIRED and params['md_api_on']):
                (ieee_from_database, b, c, d, duplicateEntries) = getIEEEfromDatabase(serial_number_internal, 'internal')
            new_state = current_state


            if (STATION_ID == 2 and DEVICE_TYPE == 'SAM') and ieee_from_database != None:
                ieee_address = ieee_from_database
            if DEVICE_TYPE == "Silvretta":
                serial_number = serial_number_internal
            # Get number of tests that will be run 
            print "Running %s tests...\n" % params['numTests']
    
            if DEBUG_MODE:
                print "Starting state of MFG_TOGGLE_PIN: %s" % current_state

            # Run through the tests, breaking if timeout 
            while currentTestIndex <= params['numTests'] and not endTests and not duplicateEntries:
                startTime = util.resetTimer()

                while current_state == new_state:
                    new_state = gpio_ns_read(MFG_TOGGLE_PIN)

                    # If timeout, end tests and return fail.
                    if util.getTimePassed(startTime) > STATE_MACHINE_TIMEOUT:
                        (timeout, testResult, currentTestIndex, error, testsCompleted) = timeoutProcessing(params, testOrder[currentTestIndex-1]['name'])
                        allTestResults.append(testResult)
                        errorlog.append(error)
                        break                 

                    # If state has changed, do the next test           
                    if current_state != new_state:

                        # Set pins to test mode
                        #setPinsToTestMode()

                        if testOrder[currentTestIndex-1]['testFunction'] == 'LEDtest':
                            ledIndex = int(testOrder[currentTestIndex-1]['name'][-1])

                        if DEBUG_MODE:
                            print "\nCurrent test index: %d" % (currentTestIndex-1)
                            print "LED index: %d" % (ledIndex-1)
                            print "testFunction: %s\n" % testOrder[currentTestIndex-1]['testFunction']

                        params['testIndex'] = currentTestIndex
                        params['ledIndex'] = ledIndex

                        """
                        if testOrder[currentTestIndex-1]['testFunction'] == 'vibeCurrentTest':
                            vibeCurrentIndex = int(testOrder[currentTestIndex-1]['name'][-1])

                        if DEBUG_MODE:
                            print "\nCurrent test index: %d" % (currentTestIndex-1)
                            print "Vibe Current Test Index: %d" % (vibeCurrentIndex-1)
                            print "testFunction: %s\n" % testOrder[currentTestIndex-1]['testFunction']

                        params['testIndex'] = currentTestIndex
                        params['vibeCurrentIndex'] = vibeCurrentIndex
                        """
                        # Start the next test
                        testResult = doNextOrderedTest(currentTestIndex, instr, params)  
                          
                        # Set ieee_address after MAC test
                        if hasattr(testResult, 'macMasked') and testResult.is_passed == True:
                            ieee_address = getattr(testResult, 'macMasked')
                            if ieee_from_database != None and ieee_from_database != ieee_address:
                                duplicateEntries = True
                                results['is_duplicated'] = True
                                break
                        elif hasattr(testResult, 'macMasked'):
                            ieee_address = getattr(testResult, 'macMasked')

                        if hasattr(testResult, 'name') and MEASURE_PI_VOLTAGE and (testResult.name == "Load Test" or testResult.name == "Idle Mode Test"):
                            voltageTest = voltageMeasurementTest(instr, params)

                        # If operating with limited pin set, take last char of orientation test output, use this as self test
                        if LIMITED_PIN_SET and hasattr(testResult, 'name') and testResult.name == "Accelerometer Orientation Test" and hasattr(testResult, 'pin_state'):
                            params['pinState'] = getattr(testResult, 'pin_state')
                            accelSelfTestResult = accelSelfTest(instr, params)
                            allTestResults.append(accelSelfTestResult)

                        (allTestResults, errorlog, timeout, testsCompleted, endTests) = doPostTestSequence(testResult, allTestResults, errorlog, params)

                        if voltageTest is not None:
                            allTestResults.append(voltageTest)
                            voltageTest = None

                        if endTests == True:
                            break

                        if DEBUG_MODE:
                            if new_state != gpio_ns_read(MFG_TOGGLE_PIN):
                                errorstring = "MFG_TOGGLE_PIN is not in starting state"
                                errorlog.append(__storeErrorLog(errorstring, testResult))
                                break     

                            if not LIMITED_PIN_SET and gpio_ns_read(MFG_INFO_PIN) == 1:
                                errorstring = "MFG_INFO_PIN is high"
                                errorlog.append(__storeErrorLog(errorstring, testResult))                        
                                break

                        currentTestIndex += 1   

                # Toggle button pin
                toggleButton(current_state, new_state)

                current_state = new_state   
        # Get IEEE address from database for stations 2 or 3    
        elif STATION_ID == 1.5:
            if params['md_api_on'] or (DATABASE_ACCESS_REQUIRED and params['md_api_on']):
                print "\nReading IEEE address from database."   
                if GET_IEEE_FROM_SERIAL_INTERNAL:
                    (ieee_address, serial_from_database, serial_internal_from_database, serial_smt_from_database, duplicateEntries) = getIEEEfromDatabase(serial_number_internal, 'internal')
                    
                    # Check if the internal serial number from the database matches the scanned internal serial number.
                    # if the internal serial numbers aren't equal, there's a duplicate.
                    if serial_internal_from_database != None and serial_internal_from_database != serial_number_internal:
                        print "\nFound duplicate serial number\n"
                        duplicateEntries = True                        
                        # this variable is used to update the database, set it to none to prevent updating database with the scanned serial number.
                        params['serial_from_database'] = None

                else:
                    (ieee_address, serial_from_database, serial_internal_from_database, serial_smt_from_database, duplicateEntries) = getIEEEfromDatabase(serial_number,'packaging')                
                serial_number_smt = serial_smt_from_database
                readIEEEtest = ReadIEEEaddressTest(isPassed=True, ieeeAddress=ieee_address, ieeeAddressSource='db')
                allTestResults.append(readIEEEtest)        
        # Get IEEE address from database for stations 2 or 3    
        elif STATION_ID == 2 and DEVICE_TYPE != "BMW":
            if params['md_api_on'] or (DATABASE_ACCESS_REQUIRED and params['md_api_on']):
                print "\nReading IEEE address from database."   
                if GET_IEEE_FROM_SERIAL_INTERNAL:
                    (ieee_address, serial_from_database, serial_internal_from_database, serial_smt_from_database, duplicateEntries) = getIEEEfromDatabase(serial_number, 'packaging')
                    
                    # Check if the internal serial number from the database matches the scanned internal serial number.
                    # if the internal serial numbers aren't equal, there's a duplicate.
                    if serial_internal_from_database != None and serial_internal_from_database != serial_number_internal:
                        print "\nFound duplicate serial number\n"
                        duplicateEntries = True

                    if not duplicateEntries:
                        (ieee_address, serial_from_database, serial_internal_from_database, serial_smt_from_database, duplicateEntries) = getIEEEfromDatabase(serial_number_internal, 'internal')
                        params['serial_from_database'] = serial_from_database
                else:
                    (ieee_address, serial_from_database, serial_internal_from_database, serial_smt_from_database, duplicateEntries) = getIEEEfromDatabase(serial_number,'packaging')                
                serial_number_smt = serial_smt_from_database
                
                # check the ieee address if it is None
                isPassed = True
                if ieee_address == None:
                    isPassed = False    
                
                readIEEEtest = ReadIEEEaddressTest(isPassed=isPassed, ieeeAddress=ieee_address, ieeeAddressSource='db')
                allTestResults.append(readIEEEtest)
            else:
                print "\nReading IEEE address from radio." 
                time.sleep(2); # TODO: do we need this sleep here?
                ieee_address = scanForDeviceWithRSSIandSerial(serial_number)

                # check the ieee address if it is None
                isPassed = True
                if ieee_address == None:
                    isPassed = False    
                
                readIEEEtest = ReadIEEEaddressTest(isPassed=isPassed, ieeeAddress=ieee_address, ieeeAddressSource='scan')
                allTestResults.append(readIEEEtest)                
        elif STATION_ID == 2 and DEVICE_TYPE == "BMW":
            #allTestResults.append(operatingCurrentTest(instr, params))
            print "\nReading IEEE address from radio." 
            time.sleep(2); # TODO: do we need this sleep here?
            ieee_address = scanForDeviceWithRSSIandSerial(serial_number)

            isPassed = True
            if ieee_address == None or ieee_address == "" or (len(ieee_address) != 12):
                isPassed = False

            readIEEEtest = ReadIEEEaddressTest(isPassed=isPassed, ieeeAddress=ieee_address, ieeeAddressSource='scan')
            allTestResults.append(readIEEEtest) 

            # Look up the device information using packaging serial number from data base
            # check if serial number is used in the database for duplicate SN

            if isPassed:
                (ieee_from_database, serial_from_database, serial_internal_from_database, serial_smt_from_database, duplicateEntries) = getIEEEfromDatabase(serial_number,'packaging')

                if ieee_from_database != None and ieee_from_database != ieee_address:
                    duplicateEntries = True
                    print "Found duplicate serial number"
        elif STATION_ID == 3:
            print "\nReading IEEE address from database."                           
            if serial_number_internal is not None:
                (ieee_address, serial_from_database, serial_internal_from_database, serial_smt_from_database, duplicateEntries) = getIEEEfromDatabase(serial_number,'packaging')        
                #serial_number = serial_from_database
                serial_number_smt = serial_smt_from_database 

                # Check if the packaging serial number from the database matches the scanned packaging serial number.
                # if the packaging serial numbers aren't equal, there's a duplicate.
                if serial_internal_from_database != None and serial_internal_from_database != serial_number_internal:
                    print "\nFound duplicate serial number\n"
                    duplicateEntries = True 
                    params['serial_from_database'] = None

                if not duplicateEntries:
                    (ieee_address, serial_from_database, serial_internal_from_database, serial_smt_from_database, duplicateEntries) = getIEEEfromDatabase(serial_number_internal, 'internal')
                    params['serial_from_database'] = serial_from_database

            elif serial_number is not None:
                (ieee_address, serial_from_database, serial_internal_from_database, serial_smt_from_database, duplicateEntries) = getIEEEfromDatabase(serial_number, 'packaging')        
                serial_number_internal = serial_internal_from_database      
                serial_number_smt = serial_smt_from_database                        
        if ieee_address is None and not duplicateEntries and SCAN_DEVICES_FOR_IEEE and MANUFACTURER_NAME == 'VS' and STATION_ID == 3 and DEVICE_TYPE == 'Apollo':
            if serial_number is None:
                print "\nError: no serial number, can't scan for IEEE.\n"
            else:
                print "\nScanning for device with serial number: %s...\n" % serial_number
                ieee_address = scanForDeviceWithSerial(serial_number)

        # Do BLE tests
        if duplicateEntries:
            print "\nError: Multiple ieee_addresses for this serial number.  Ending tests."
            testResult = DuplicateSNTest()
            testResult.serial_number = serial_number
            testResult.serial_number_internal = serial_number_internal
            testResult.is_passed = False
            testResult.ieee_from_device = ieee_address
            testResult.ieee_from_database = ieee_from_database
            allTestResults.append(testResult)

            ieee_address = None
            testsCompleted = False
            endTests = True
        elif ieee_address is None or ieee_address == "0":
            print "\nError: No ieee_address.  Ending tests."
            testsCompleted = False
            endTests = True
            if STATION_ID == 3:
                print "\n================================="
                print "TESTS FAILED:"            
                print "     Serial number not in database/no ieee address\n"
                print "=================================\n"
        elif STATION_ID == 3:
            #if serial_number is None:
            #   print "\nError: missing serial number. Ending tests.\n"    
            #    testsCompleted = False
            #    endTests = True                            
            if serial_number_internal is None:
                print "\nError: missing internal serial number. Ending tests.\n"
                testsCompleted = False
                endTests = True

        if ((not timeout and testsCompleted and not endTests) or not params['stop_after_fail']) and ieee_address is not None:
            if (DEVICE_TYPE == 'Pluto') and STATION_ID == 1:
                setPinsToTestMode()
                allTestResults.append(hibernationModeTest(instr, params))
                resetDUT()
                allTestResults.append(pogoPinTest(instr, params))  #perform pogo pin test before going into customer mode.
            powerCycleDUT("customer")

            # Need to activate BLE advertising by holding down the Pusher 2 button to establish BLE connection between ATE and DUT.
            if ACTIVATE_BLE:
                print "Activating Bluetooth..."
                gpio_ns_pull(MFG_TRIG_PIN, "out")
                gpio_ns_write(MFG_TRIG_PIN, GPIO_HI)
                time.sleep(2)

            (rssi, fw_rev, serial_from_device, allTestResults, error, timeout, testsCompleted, endTests) = doBLEtests(ieee_address, serial_number, params, allTestResults, errorlog)
            if timeout:
                errorlog.append(error)

        params['serial_number'] = serial_number       
        params['serial_number_internal'] = serial_number_internal
        params['serial_number_smt'] = serial_number_smt
        params['ieee_address'] = ieee_address
        params['fw_rev'] = fw_rev

        # Do current tests for Station 2 or 3
        if (STATION_ID == 2 or STATION_ID == 3) and DEVICE_TYPE != 'SAM':
            if (not timeout and testsCompleted and not endTests):
                for test in testOrder:
                    testResult = doNextTest(test, instr, params)
                    (allTestResults, errorlog, timeout, testsCompleted, endTests) = doPostTestSequence(testResult, allTestResults, errorlog, params)

                    if endTests == True:
                        testsCompleted = False
                        break

        if ieee_address:
            ieee_read = True

    ###### TESTS DONE ######
    deactivatePusherPistons() # deactivate just in case pistons are stuck

    # Remove serial port from params
    port = params['port']
    params.pop('port', None)

    params.pop('instr', None)

    # Add serial numbers to a test object
    # In theory, this should only pass if there's database access
    serialNumberObject = LinkSerialInDBtest(isPassed=True,
                                            serialNumber=serial_number,
                                            serialNumberInternal=serial_number_internal,
                                            serialNumberSMT=serial_number_smt)
    allTestResults.append(serialNumberObject)

    # Add git commit hash to a test object
    gitCommitObject = StoreGitCommitHash(isPassed=True,
                                         gitCommitHash=params['git_commit_hash'])
    allTestResults.append(gitCommitObject)

    # Add field to store whether test object is uploaded via cron
    cronTestObject = UploadedViaCronTest(isPassed=True, 
                                        uploadedViaCron=False)
    allTestResults.append(cronTestObject)

    # Store log entries
    logentry['station_id'] = STATION_ID
    logentry['station_index'] = STATION_INDEX
    logentry['testTime_elapsed'] = getTimePassed(testStartTime) 
    endTime = datetime.datetime.now()   
    logentry['testTimeEnd_local'] = datetime.datetime.strftime(endTime,"%Y-%m-%d %H:%M:%S")
    logentry['testTimeEnd_utc'] = time.mktime(datetime.datetime.utcnow().timetuple())        
    logentry['params'] = params
    logentry['timeout'] = timeout
    logentry['testsCompleted'] = testsCompleted
    logentry['ieee_read'] = ieee_read   
    logentry['ieee'] = ieee_address 
    logentry['fw_rev'] = fw_rev
    logentry['rssi'] = rssi        
    logentry['serial_number'] = serial_number
    logentry['serial_number_internal'] = serial_number_internal       
    logentry['serial_number_smt'] = serial_number_smt           
    logentry['serial_from_device'] = serial_from_device
    logentry['errorlog'] = errorlog     
    logentry['git_commit_hash'] = params['git_commit_hash']

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
    results['serial_number_smt'] = serial_number_smt               
    results['serial_from_device'] = serial_from_device
    results['ieee_address'] = ieee_address
    results['rssi'] = rssi
    results['fw_rev'] = fw_rev
    results['end_time'] = datetime.datetime.strftime(endTime, "%Y%m%d%H%M%S")

    if not setupSuccess:
        print "\nSetup failed. Ending...\n"
    if timeout:
        print "\nTimeout; tests not completed.\n"
    elif testsCompleted and not endTests:
        print "\nAll tests completed.\n"
    elif testsCompleted:
        print "\nTests completed.\n"

    # Do end sequence and send results to database
    (overallPass, logPosted, testsFailed) = endSequence(instr, port, results, input_type)

    print "\nFull script time elapsed: %s seconds\n" % getTimePassed(params['scriptStartTime'])

    # Return UI to show operator
    if overallPass and logPosted:
        return (0, testsFailed)
    elif overallPass:
        return (2, testsFailed)
    elif not params['md_api_on'] or not params['internet_on']:
        return (5, "Unable to connect to the internet.  Please check your connection or contact your IT support!")
    elif not params['dmm_connected']:
        return (5, "Unable to connect to the DMM.  Please check the USB connection from the DMM to the ATE fixture.  Reset the DMM and try again.")
    #elif not params['ble_dongle_connected']:
    #    return (5, "Bluetooth dongle is not connected.  Please check connection of the BLE dongle to the ATE fixture.")
    elif not params['rotating_plate_error']:
        return (5,"Rotating plate is not in correct orientation. Set the plate to position " + serial_number_internal[4])
    else:
        return (1, testsFailed)

# Store error types and the test that preceded the error
def __storeErrorLog(errorstring, testResult):
    error = {}
    error['type'] = errorstring
    if testResult == None:
        error['testName'] = "None"
    else:
        error['testName'] = testResult.name
    print "Error: %s. Previous test: %s" % (error['type'], error['testName'])
    return error

# If timeout, return TimeoutTest result and end tests
def timeoutProcessing(params, name):
    print "\nWarning: timeout after being in current state for %s seconds. Exiting." % STATE_MACHINE_TIMEOUT                
    timeout = True  
    testResult = TimeoutTest()
    testResult.timeout = timeout
    testResult.is_passed = False
    testResult.name = name
    currentTestIndex = params['numTests'] + 1    
    error = __storeErrorLog("timeout", testResult)
    testsCompleted = False                                
    return (timeout, testResult, currentTestIndex, error, testsCompleted)

def doNextOrderedTest(testIndex, instr, params):

    # This takes in the test referenced by testIndex from the testOrder list, and calls that function
    testResult = eval("%s(instr, params)" % testOrder[testIndex-1]['testFunction'])
    return testResult

def doNextTest(test, instr, params):

    # This takes in the next test from the testOrder list, and calls that function
    testResult = eval("%s(instr, params)" % test['testFunction'])
    return testResult

def doNextBLEtest(test, bleController, params):
    time.sleep(BLE_DELAY) # Short delay between tests to ensure stability of ATE 2.  This is chose arbitrarily and should be revisited after the first 10k.
    # This takes in the next test from the testOrder list, and calls that function
    testResult = eval("%s(bleController, params)" % test['testFunction'])
    return testResult

def doPostTestSequence(testResult, allTestResults, errorlog, params):

    timeout = False
    testsCompleted = True
    endTests = False

    # Abort rest of tests if there's been a timeout
    if hasattr(testResult,'timeout') and testResult.timeout == True:
        (timeout, testResult, currentTestIndex, error, testsCompleted) = timeoutProcessing(params, testResult.name)
        allTestResults.append(testResult)
        errorlog.append(error)
        testsCompleted = False
        endTests = True

    if hasattr(testResult,'name') and testResult.name == "Crystal Test" and testResult.is_passed == False:
        endTests = True

    # Pause between tests in debug mode
    if DEBUG_MODE:
        choice = raw_input("Hit 'Enter' to continue: ")
        print ""
    # else:
    #     time.sleep(1)

    # Append to test results list
    if testResult != None and not hasattr(testResult, 'timeout'):
        allTestResults.append(testResult)

    # Abort rest of tests if any test has failed
    if params['stop_after_fail'] and hasattr(testResult,'isPassed') and testResult.isPassed == False:
        print "%s failed; ending tests." % testResult.name
        testsCompleted = False                            
        endTests = True          

    return (allTestResults, errorlog, timeout, testsCompleted, endTests)

def doBLEtests(ieee_address, serial_number, params, allTestResults, errorlog):
    print ""
    print "================================="
    print "Starting BLE tests..."
    print "================================="    
    print ""

    if DEBUG_MODE:
        choice = raw_input("Hit 'Enter' to continue: ")
        print ""

    testsCompleted = True
    timeout = False
    error = ''
    rssi = None
    serial_from_device = None
    params['serial_number'] = serial_number
    endTests = False

    # This is only applicable for Pluto ATE 2.  The reset is necessary to obtain an accurate cap touch measurement since the
    # the measurment is taken when the device boots/wakes up.  It is possible that when the operator wakes up the device, that
    # the cap touch measurement will also add more capacitance to the measurment.
    if (DEVICE_TYPE == "Pluto" and STATION_ID == 2) or (DEVICE_TYPE == "BMW" and STATION_ID == 1.5):
        # Open the connection to the device.
        (bleController, fw_rev, timeout) = openConnection(ieee_address)
        # Send reset command to device.
        resetViaBT(bleController)
        # Close connection with device to ensure BLE dongle is in a good state.
        closeConnection(bleController)

    # Open BLE Connection
    (bleController, fw_rev, timeout) = openConnection(ieee_address)

    # Pause between tests in debug mode
    if DEBUG_MODE:
        choice = raw_input("Hit 'Enter' to continue: ")
        print ""

    if timeout:
        error = __storeErrorLog("BLE connection timeout", None)
        bleConnectTest = BluetoothConnectedTest()
        bleConnectTest.is_passed = False
        allTestResults.append(bleConnectTest)
        testsCompleted = False
        endTests = True
    elif fw_rev not in FW_VERSIONS:
        # Checking for exepected firmware version.  If it doesn't then log the expected version with the read back version.
        allTestResults.append(FirmwareCheckTest(isPassed=False, expectedFW=FW_VERSIONS, fwVersion=fw_rev))
        testsCompleted = False
        endTests = True
    else:
        bleConnectTest = BluetoothConnectedTest()
        bleConnectTest.is_passed = True
        allTestResults.append(bleConnectTest)

        # Release the Pusher 2 button since BLE connection is successful.
        gpio_ns_write(MFG_TRIG_PIN, GPIO_LO)  
        gpio_ns_pull(MFG_TRIG_PIN, "in")   

        # Update the connection parameters to a faster connection
        updateLinkInterval(bleController)
        
        for test in testOrderBLE:
            # Start the next test
            testResult = doNextBLEtest(test, bleController, params)    

            # Get RSSI after RSSI test
            if hasattr(testResult, 'average_rssi') and testResult.is_passed == True:
                rssi = getattr(testResult, 'average_rssi')

            if hasattr(testResult,'serial_from_device'):
                serial_from_device = getattr(testResult,'serial_from_device')

            (allTestResults, errorlog, timeout, testsCompleted, endTests) = doPostTestSequence(testResult, allTestResults, errorlog, params) 

            if endTests == True:
                testsCompleted = False
                break

        allBleTestsPassed = True
        # Check if all tests passed.
        for test in allTestResults:
            if not test.is_passed:
                allBleTestsPassed = False
                break

        # If all tests passed for RMM on station 3, program serial number.
        if (PROGRAM_SERIAL_NUMBER and allBleTestsPassed):
            time.sleep(BLE_DELAY) # Short delay between tests to ensure stability
            # Write the serial number.
            testResult = writeSNTest(bleController, params)
            (allTestResults, errorlog, timeout, testsCompleted, endTests) = doPostTestSequence(testResult, allTestResults, errorlog, params) 

            time.sleep(BLE_DELAY) # Short delay between tests to ensure stability

            # Readback the serial number
            testResult = getSNTest(bleController, params)
            serial_from_device = testResult.serial_from_device
            (allTestResults, errorlog, timeout, testsCompleted, endTests) = doPostTestSequence(testResult, allTestResults, errorlog, params) 

        if (STATION_ID == 2 or STATION_ID == 3):
            # Reset the device via BLE.
            time.sleep(BLE_DELAY) # Short delay between tests to ensure stability
            allTestResults.append(resetViaBTtest(bleController, params))

    closeConnection(bleController)

    return (rssi, fw_rev, serial_from_device, allTestResults, error, timeout, testsCompleted, endTests)

def endSequence(instr, port, results, input_type):

    # Compute overall pass/fail based on whether all tests passed or not
    logentry = results['logentry']
    overallPass = True
    post_success = False
    testsPassed = []
    testsFailed = []

    # If setup failed, abort tests
    if results['setupSuccess'] == False:
        overallPass = False
        print "Error: startup sequence failed, aborting."
        if STATION_ID == 3:
            print "\n================================="
            print "TESTS FAILED:"            
            print "     Startup sequence failed\n"
            print "=================================\n"
    elif results['timeout']:
        pass
    elif ((STATION_ID != 1 and STATION_ID != 1.5) and (DEVICE_TYPE != 'SAM' and STATION_ID == 2)) and results['serial_from_device'] is None:
        overallPass = False
        print "Error: no serial number from device."
        if STATION_ID == 3:
            print "\n================================="
            print "TESTS FAILED:"            
            print "     No serial number on device\n"
            print "=================================\n"
    elif (STATION_ID == 1 or (STATION_ID == 2 and DEVICE_TYPE == 'SAM')) and results['is_duplicated']:
        overallPass = False

    # Calculate overallPass, display which tests passed/failed
    if results['timeout'] == True or results['testsCompleted'] == False:
        overallPass = False
        print ""
        print "================================="
        print "TIMEOUT"
        print "================================="
        print ""
    for testResult in results['allTestResults']:
        if not testResult.is_passed:
            overallPass = False
            testsFailed.append(testResult)
        else:
            testsPassed.append(testResult)

    print ""
    print "================================="
    print "TESTS PASSED:"
    for testPassed in testsPassed:
        print "     %s" % testPassed.name

    print ""
    print "TESTS FAILED:"
    for testFailed in testsFailed:
        print "     %s" % testFailed.name
    print ""
    print "================================="
    print ""

    if MANUFACTURER_NAME == "Endor":
        createTestReport(results, testsFailed)

    logentry['overallPass'] = overallPass
    print "\nOverall Pass: %s\n" % overallPass

    # Create station test object, for this station
    stationTestObject = StationTest(ateID=str(ATE_ID) + "." + str(STATION_ID) + "." + str(STATION_INDEX), 
                                    isPassed=overallPass, 
                                    scriptVersion=SCRIPT_VERSION, 
                                    firmwareVersion=results['fw_rev'], 
                                    tests=results['allTestResults'], 
                                    date=time.mktime(datetime.datetime.utcnow().timetuple()))

    if DEBUG_MODE:
        print "Station Test Object: "
        pprint (vars(stationTestObject))
        print ""

    """
    if STATION_ID != 1 and results['serial_number'] is not None:
        # Get color based on serial number
        deviceColor = deviceColorLookup(results['serial_number'])
        print "Device color for %s is %s\n" % (results['serial_number'], deviceColor)
    else:
        deviceColor = None
    """
    if results['serial_from_device'] != results['serial_number']:
        print "Warning, SN from device (%s) does not match SN entered by user (%s). Using SN from device.\n" % (results['serial_from_device'], results['serial_number'])

    # If IEEE is None, set it to 0 so the data base could capture this run.
    if results['ieee_address'] == None:
        results['ieee_address'] = "0"

    # If a bad MAC address is received, do not set serial numbers in the database.
    if results['ieee_address'] == "0":
        results['serial_from_device'] = ""
        results['serial_number_internal'] = ""
        results['serial_number_smt'] = ""

    # Create device object, physicals object, etc
    misfitDevice = BLEdevice(serial_number=results['serial_from_device'],
                             serial_number_internal=results['serial_number_internal'],
                             serial_number_smt=results['serial_number_smt'],
                             ieee=results['ieee_address'],
                             ieeeString=results['ieee_address'],
                             rssi=results['rssi']
    )

    # Update device fields 
    misfitDevice.physical['color'] = None#deviceColor
    misfitDevice.fw_rev = results['fw_rev']
    misfitDevice.is_passed = overallPass
    misfitDevice.addStationTest(stationTestObject)

    # Post every run to the database.
    if params['md_api_on']:
        posted_update = False   
        posted_physicals = False 

        #post entry to DB.  If device doesn't exist in DB, then it will create an entry.
        # Doing this first because DB needs to have an entry before updating the results.
        post_success = postTestEntryToMFGdb(stationTestObject, misfitDevice)

        # For ATE 1 or ATE 2, Update internal serial number, ieee, and over all pass
        if STATION_ID == 1 or STATION_ID == 2:
            posted_update = updateDeviceWithPass(results['ieee_address'], overallPass)

            # If the station is ATE 1, we need to clear the database of the packaging serial number because the device could
            # be assigned a new serial number and we want to prevent a possible duplicate serial number.
            if STATION_ID == 1:
                posted_update = updateDeviceWithSerialNumAndPass(results['ieee_address'], None, overallPass)
        # For ATE 3, Update Serial number, ieee, and over all pass, and physicals  
        elif STATION_ID == 3: 
            if overallPass: # Device passed, update the database with the packaging serial number and the Passed result
                posted_update = updateDeviceWithSerialNumAndPass(results['ieee_address'], results['serial_from_device'], True)
            elif results['ieee_address'] == "0": # No serial number or it is duplicated.  Clear the serial number so it doesn't create a duplicate when updating device IEEE 0.
                posted_update = updateDeviceWithSerialNumAndPass("0", None, False)
            else: # Device failed, do not update the serial number the Failed result.
                posted_update = updateDeviceWithSerialNumAndPass(results['ieee_address'], None, False)

            posted_physicals = updateDeviceWithPhysicals(results['ieee_address'], misfitDevice.physical)                
            print "posted_physicals: %s" % posted_physicals 

        """  
        if STATION_ID == 2 or (STATION_ID == 1 and STATION_INDEX == -2):
            if not overallPass:
                posted_update = updateDeviceWithSerialNumAndPass(results['ieee_address'], params['serial_from_database'], overallPass)
            else:  
                posted_update = updateDeviceWithSerialNumAndPass(results['ieee_address'], results['serial_from_device'], overallPass)
            posted_physicals = updateDeviceWithPhysicals(results['ieee_address'], misfitDevice.physical)                
            print "posted_physicals: %s" % posted_physicals                
        else:
            posted_update = updateDeviceWithPass(results['ieee_address'], overallPass)

            #if device is Silvretta, update database with serial number since the write serial number is done in ATE 1.
            if DEVICE_TYPE == 'Silvretta' or DEVICE_TYPE == 'RMM':
                posted_update = updateDeviceWithSerialNumAndPass(results['ieee_address'], results['serial_from_device'], overallPass)
        """
    else:
        post_success = False
        print "No connection to database; cannot update database with results!"

    if DEBUG_MODE:
        print "\nMisfit Device: "
        pprint (vars(misfitDevice))

    """
    # Add entry to manufacturing database
    if params['md_api_on']:
        post_success = postTestEntryToMFGdb(stationTestObject, misfitDevice)
        print "\nPost success: %s" % post_success
    else:
        post_success = False
        print "\nPost success: false (no internet)" 
    """
    
    md = util.my_dict(misfitDevice)
    logentry['misfit_device'] = md
    logentry['mfg_db_post_success'] = post_success

    if not results['setupSuccess']:
        logentry['test_began'] = False
        logentry['misfit_device'] = {}
        logentry['mfg_db_post_success'] = False

    logentry['scriptTimeEnd_local'] = datetime.datetime.strftime(datetime.datetime.now(),"%Y-%m-%d %H:%M:%S")
    logentry['scriptTime_elapsed'] = getTimePassed(params['scriptStartTime'])
    print "\nScript runtime: %s seconds\n" % logentry['scriptTime_elapsed']

    print "\nlogentry:"
    logentryJSON = json.dumps(logentry, indent=4)
    print ""
    print logentryJSON

    # Upload test results to GT MES
    if MANUFACTURER_NAME == "GT" and not MFG_DB_STAGING:
        if STATION_ID == 2:
            sn = results["serial_number"]
        else:
            sn = results['serial_number_internal']
            
        stationCode = 'ATE' + str(STATION_ID) + "-" + str(STATION_INDEX)
        stationDesc = ""
        sectionCode = "B0."+ str(STATION_ID) + "." + str(STATION_INDEX)
        sectionDesc = ""
        lineCode = "S01"
        lineName = "BMW"
        tester = ""
        test_time = ""
        testResult = 0

        if not overallPass:
            testResult = 1 # this indicates a test failed.

        ResultType = 1
        errorCode = ""
        errorDesc = ""
        testdata = ""
        testFileName = datetime.datetime.strftime(datetime.datetime.now(), "_%Y_%m_%d_%H%M_") + sn + ".json" # example: _YYYY_MM_DD_HHMM_xx where xx is the serial number?
        testFileByte = logentryJSON

        status = CommitTestDataToMES(sn=sn, stationCode=stationCode, stationDesc=stationDesc, sectionCode=sectionCode, sectionDesc=sectionDesc, lineCode=lineCode, 
                        lineName=lineName, tester=tester, test_time=test_time, testResult=testResult, ResultType=ResultType, errorCode=errorCode, errorDesc=errorDesc,
                        testdata=testdata, testFileName=testFileName, testFileByte=testFileByte)

        if status == -1:
            print "Failed to upload data to MES"
        else:
            print "Uploaded data to MES successful"

    print "Script runtime: %s seconds\n" % getTimePassed(params['scriptStartTime'])

    if results['serial_number_internal'] is not None:
        logname = results['serial_number_internal']
    else:
        logname = 'XXXXXXXXXX'
    if logentry['mfg_db_post_success'] == True:
        print "\nLogPostedEntry..."
        logPostedEntry(logentryJSON, logname)
    else:
        print "\nLogUnpostedEntry, will post later."
        logUnpostedEntry(logentryJSON, logname)

    print "Script runtime: %s seconds\n" % getTimePassed(params['scriptStartTime'])

    if input_type == 'cli':
        # Save JSON to temporary file
        sf = open(JSON_FILE,'w')
        try:
            sf.write(str(logentryJSON) + '\n')
        finally:
            sf.close()

    # At the end turn everything from start sequence into opposite state
    if not port is None:
        port.close()
    if instr.instr is not None:
        instr.reset()

    resetDUT()

    return (overallPass, post_success, testsFailed)



