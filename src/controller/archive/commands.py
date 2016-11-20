'''
Created on 19-06-2013

@author: Michael Akilian
'''

#from helper.log_utils import writeLog
from model.dut_parameters import DutParameters, FlashRecord, TestRecord
from multiprocessing import Value
from model.device import *
from pyblehci import BLEBuilder
from pyblehci import BLEParser
from subprocess import Popen, PIPE
from stationonecodes import *
from constants import *

import helper.ni_usb_6800 as NI
import helper.source_meter as SM
import serial
import time
import binascii
import MDapi
import datetime

#TEST BOUNDS
MCU_Current_LOWER = .0033       # equals 3.3 milliamps
MCU_Current_UPPER = .0038       # equals 3.8 milliamps

#now for 1 LED at a time
LED_Current_Delta_LOWER = .0055 # equals 5.5 miliamps
LED_Current_Delta_UPPER = .0076 # equals 7.6 miliamps

LED_6_Current_UPPER = 3*LED_Current_Delta_UPPER + MCU_Current_UPPER
LED_6_Current_LOWER = 3*LED_Current_Delta_LOWER + MCU_Current_LOWER

Low_Power_Current_UPPER = .0000055 #equals 5.5 microamps
Low_Power_Current_LOWER = .000003 #equals 3 microamps

RSSI_LOWER = -60
RSSI_UPPER = -30
MAX_INVALID_RSSI_COUNT = 10

BT_TIMEOUT = 10
invalidRSSICount = 0

def resetState():
    global rssi
    global is_rssi_retrieved
    global scan_done
    global link_established
    global rssi_success
    global rssi_read
    global rssi_invalid
    global output
    global current_state
    global invalidRssiCount
    global startTime

    current_state = 0
    output = 0
    rssi = 0
    startTime = 0
    is_rssi_retrieved = False
    scan_done = False
    link_established = False
    rssi_success = False
    rssi_read = False
    rssi_invalid = False
    invalidRssiCount = 0

def __convertAnalogToDigital(Ain):
    temp = 0
    for a in Ain:
        temp = temp + a
    temp = temp / len(Ain)    
    if (temp < .5):
        return 0
    elif (temp > 2.3):
        return 1
    else:
        return -1

def __waitForContinueMessage():
    global current_state
    
    test = -1
    while test == current_state or test == -1:  
        test = NI.captureAnalogInput('Dev1/ai2', 5, 10000)
        test = __convertAnalogToDigital(test)
        
    current_state = test

def __sendContinueMessage():
    global output
    if output == 3.0:
        output = 0
    else:
        output = 3.0
    NI.setAnalogOutput('Dev1/ao1', output)

def batchMeasureCurrent():
    initialCurrent = SM.measureBatchCurrent1()
    currents = initialCurrent.split(',')
    currents2 = []
    i = 0
    while i < len(currents):
        if i % 5 == 1:
            currents2.append(float(currents[i]))
        i+= 1
    return currents2

def measureCurrent():
    current = SM.senseCurrent()
    current = current.replace('\n', '')
    current = current.split(',')
    current = float(current[1])
    return current

def powerSetup():
    output = 0
    NI.setAnalogOutput('Dev1/ao1', output)
    NI.setDigitalOutput('Dev1/port0/line0:5', 63)
    
    print "enabling power @3v & compliance @100ma, ARM system"
    success = SM.initialize()
    if success:
        SM.setOutputVoltageTo3v()
    return success
    
def programmingSequence(dut_parameters, log_queue):
    results = {}

    #unlock EFM
    passed = False
    print "Unlocking EFM"
    unlockStatus = unlockEFM(dut_parameters, log_queue)
    if unlockStatus == 0:
        passed = True
    unlock = UnlockEFMTest(isPassed=passed, timestamp=time.time())
    results['unlock'] = unlock

    if unlockStatus:
        print "Something wrong unlocking EFM."
        return results

    #program cc

    passed = False
    print "Programming CC"
    ccStatus = loadCc2541Firmware(dut_parameters, log_queue)
    if ccStatus == 0:
        passed = True
    programCC = ProgramCCTest(isPassed=passed, timestamp=time.time(), ccFirmware="SBLplusController_v1.3.1_noPM3_SBLcommand_small_20130627.hex")
    results['programCC'] = programCC

    if ccStatus: #if it's not zero then it failed.
        print "Something wrong with CC."
        return results

    ieee = readCc2541IEEEAddress(dut_parameters, log_queue)
    results['ieee'] = ieee

    #load firmware to EFM32 chipset
    print "programming Efm with testing firmware"
    passed = False
    efmStatus = loadEfm32Firmware(dut_parameters, log_queue, 0)
    if efmStatus == 0:
        passed = True
    programEFM = ProgramEFMTest(isPassed=passed, timestamp=time.time(), efmTestFirmware="0.0.21.ht03")
    results['programEFM'] = programEFM

    if efmStatus:
        print "Something wrong with EFM."
        return results

    return results

def powerCycle():
    #disconnect programmer
    print "disconnecting programmers"
    NI.setDigitalOutput('Dev1/port0/line0:5', 0)

    print "power cycling"
    SM.outputOff()
    time.sleep(0.1)
    SM.setOutputVoltageTo3v()
    time.sleep(0.1)

def singleLEDCurrentTests():
    passes = [True, True, True, True, True, True, True]
    ledCurrents = []
    mcuCurrent = 0
    passed = True

    for i in range(0, 7):
        __waitForContinueMessage()
        ledCurrent = measureCurrent()
        
        if i == 0: #check MCU current
            print "MCU Current  %s" % ledCurrent
            mcuCurrent = ledCurrent
            if (ledCurrent > MCU_Current_UPPER) or (ledCurrent < MCU_Current_LOWER):
                print "MCU Current fail"
                passes[i] = False
                
        if i != 0: #check each LED current
            ledCurrent = ledCurrent - mcuCurrent 
            print "LED %s Current %s" % (i,ledCurrent)
            if (ledCurrent > LED_Current_Delta_UPPER) or (ledCurrent < LED_Current_Delta_LOWER):
                print "LED %s current fail" % i
                passes[i] = False
                passed = False
        
        ledCurrents.append(ledCurrent)
        __sendContinueMessage()

    results = {}
    results['mcu'] = MCUCurrentTest(isPassed=passes[0], timestamp=time.time(), mcuCurrent=ledCurrents[0])
    results['led'] = LEDCurrentTest(isPassed=passed, timestamp=time.time(), ledCurrents=ledCurrents[1:], passes=passes[1:])
    return results

def sixLEDCurrentTest():
    passed = True
    #wait for LEDs to be on
    __waitForContinueMessage()

    #setup keithley to take batch current measurement
    SM.setupVoltageAndBatchCurrent1()
    
    sixLEDCurrent = batchMeasureCurrent()
    average = 0
    for each in sixLEDCurrent:
        average += each
        if (each > LED_6_Current_UPPER) or (each < LED_6_Current_LOWER):
                print "6 LED Current Fail"
                passed = False
    print "Six LED current: %s" % sixLEDCurrent
    average /= 6
    
    #send done with measuring current message
    __sendContinueMessage()

    #waiting for LEDs to turn off
    __waitForContinueMessage()

    return SixLEDCurrentTest(isPassed=passed, timestamp=time.time(), avgCurrent=average, allCurrent=sixLEDCurrent)

def accelerometerSelfTest():
    passed = True
    #sending continue to accel test message
    __sendContinueMessage()

    #waiting for accel test to finish
    __waitForContinueMessage()
    
    ##NI - determine success of accelerometer self test
    etm = NI.captureAnalogInput('Dev1/ai3', 5, 10000) ### get mapping
    etm = __convertAnalogToDigital(etm)
    if etm:
        print "ACCEL SUCCESS: %s" % etm
    else:
        print "ACCEL FAIL: %s" % etm
        passed = False

    return AccelSelfTest(isPassed=passed, timestamp=time.time())

def lowPowerTest():
    passed = True
    #print "SENDING CONTINUE TO LOW POWER"
    __sendContinueMessage() #this will be outputting 0v if first toggle is 0v

    #waiting for low power mode message
    __waitForContinueMessage()

    #efm in low power mode
    __sendContinueMessage() #this will be outputting 0v if first toggle is 0v
    time.sleep(.05)

    #SETTING COMPLIANCE CURRENT TO 100uA
    foo = SM.setComplianceCurrent('100e-6')
    time.sleep(.05)
    
    lowPowerCurrentTest = batchMeasureCurrent()
    sum = 0
    for each in lowPowerCurrentTest:
        if each < Low_Power_Current_LOWER or each > Low_Power_Current_UPPER:
            print "low power current fail"
            passed = False
        sum += each
        
    lowPowerAverage = sum/len(lowPowerCurrentTest)
    print "low power currents: %s" % lowPowerCurrentTest
    print "low power current average: %s" % lowPowerAverage
    if lowPowerAverage < Low_Power_Current_LOWER  or lowPowerAverage > Low_Power_Current_UPPER:
        print "low power current average fail"
        passed = False

    #SETTING COMPLIANCE CURRENT TO 100mA
    foo = SM.setComplianceCurrent('100e-3')
    time.sleep(.05)

    return LowPowerCurrentTest(isPassed=passed, timestamp=time.time(), avgCurrent=lowPowerAverage, allCurrent=lowPowerCurrentTest)

def flashFinalFirmware(dut_parameters, log_queue):
    passed = True

    ##NI - ENABLE CC2541 & EFM32 CONNECTIONS
    print "enabling efm and cc connections"
    NI.setDigitalOutput('Dev1/port0/line0:5', 63)

    ##load firmware to EFM32 chipset
    print "programming EFM"
    efmStatus = loadEfm32Firmware(dut_parameters, log_queue, 1)

    if efmStatus:
        passed = False

    ##disconnect programmers
    print "disconnecting programmers"
    NI.setDigitalOutput('Dev1/port0/line0:5', 0)

    ##reset both CC and EFM
    print "power cycle"
    SM.outputOff()
    time.sleep(.1)
    SM.setOutputVoltageTo3v()
    time.sleep(.1)

    ##NI - ENABLE CC2541 & EFM32 CONNECTIONS
    print "enabling efm and cc connections"
    NI.setDigitalOutput('Dev1/port0/line0:5', 63)

    return FinalFlashTest(isPassed=passed, timestamp=time.time(), finalFW="0.0.28x.boot2_prod")

def connectToShineDUT(ble_builder, ieee):
    global link_established
    timeout = False
   
    link_established = False
    #initialise the device
    print "COMMAND: Initialising device"
    ble_builder.send("fe00", max_scan_rsps="\x59")
    
    #set scanning length operating parameter value
    ble_builder.send("fe30", param_id="\x02", param_value="\x23\x88")

    #open connection to Shine
    print "Opening Bluetooth Connection with Shine of lowest RSSI"
    ieee = [_ for _ in reversed(ieee.split('.'))]
    ieeeString = ''
    for each in ieee:
        ieeeString += each
    ieeeString = str(binascii.unhexlify(ieeeString))
    ble_builder.send("fe09", high_duty_cycle = '\x01', peer_addr=ieeeString)
    
    #wait for link
    resetTimer()
    while not link_established:
        if getTimePassed() > BT_TIMEOUT:
            timeout = True  
            break
        print "Waiting for link"
        time.sleep(.1)
    print "Link Established: ", link_established

    return timeout

def measureAverageRSSI(ble_builder):
    global testFailures
    global averageRSSI
    global rssi_read
    global rssi
    global rssi_success
    global rssis
    global rssi_invalid
    global invalidRssiCount

    results = {}
    rssiPassed = True
    invalidPassed = True
    results['timeout'] = True

    rssi_success = False
    #HCI COMMAND TO READ RSSI
    rssis = [0, 0, 0, 0, 0]
    count = 0
    while count < 5:
        ble_builder.send("1405") # READ RSSI COMMAND
        resetTimer()
        while not rssi_read: #wait until the next reading
            if getTimePassed() > BT_TIMEOUT:
                results['timeout'] = True
                return results
            time.sleep(.1)
        if rssi_success: #latest reading was valid, increment count
            rssis[count] = rssi
            count += 1
        if rssi_invalid: #too many invalid RSSI readings - done
            invalidPassed = False
            results['invalid'] = InvalidRSSITest(isPassed=invalidPassed, timestamp=time.time(), invalidCount=invalidRSSICount)
            return results
        rssi_read = False

    #calculate average RSSI
    averageRSSI = 0

    for each in rssis:
        averageRSSI += each
    averageRSSI = averageRSSI/(len(rssis))

    print rssis
    print "Average RSSI: %s" % averageRSSI
    
    #apply threshold
    if averageRSSI < RSSI_LOWER or averageRSSI > RSSI_UPPER:
        rssiPassed = False
        print "rssi fail"

    results['rssi'] = RSSIValueTest(isPassed=rssiPassed, timestamp=time.time(), rssiValues=rssis, avgRssi=averageRSSI)
    results['invalid'] = InvalidRSSITest(isPassed=invalidPassed, timestamp=time.time(), invalidCount=invalidRSSICount)
    results['timeout'] = False
    return results

def resetTimer():
    global startTime
    startTime = time.time()

def getTimePassed():
    global startTime
    return time.time() - startTime

def executeTestSequence(dut_parameters, log_queue):
    global current_state
    global output

    output = 0
    current_state = 0
    setupSuccess = False
    overallPass = False
    logentry = {}

    if not MDapi.internet_on():
        resetState()
        return -2

    #reset globals
    resetState()
    
    #SET UP KEITHLEY POWER
    worked = powerSetup()

    if not worked:
        return -3

    #INSTALL CORRECT FIRMWARE ON DEVICE FOR TESTING
    results = programmingSequence(dut_parameters, log_queue)
    stationOneTests = []

    if 'programEFM' in results:
        unlockEFM = results['unlock']
        programCC = results['programCC']
        programEFM = results['programEFM']
        setupSuccess = (unlockEFM.is_passed and programCC.is_passed and programEFM.is_passed)
        stationOneTests.append(unlockEFM)
        stationOneTests.append(programCC)
        stationOneTests.append(programEFM)
    else:
        unlockEFM = results['unlock']
        logentry['unlocked'] = unlockEFM.is_passed
        if 'programCC' in results:
            programCC = results['programCC']
            logentry['ieee_read'] = programCC.is_passed
            if programCC.is_passed:
                logentry['ieee'] = results['ieee'].translate(None, '.')

    #DEVICE CORRECTLY SET UP FOR TESTING
    if setupSuccess:
        ieee = results['ieee']
        logentry['unlocked'] = True
        logentry['ieee_read'] = True
        logentry['test_began'] = True
        logentry['ieee'] = ieee.translate(None, '.')

        powerCycle()

        ledTests = singleLEDCurrentTests()
        stationOneTests.append(ledTests['mcu'])
        stationOneTests.append(ledTests['led'])

        sixLEDTest = sixLEDCurrentTest()
        stationOneTests.append(sixLEDTest)

        accelSelf = accelerometerSelfTest()
        stationOneTests.append(accelSelf)

        lowPower = lowPowerTest()
        stationOneTests.append(lowPower)

        flashFinal = flashFinalFirmware(dut_parameters, log_queue)
        stationOneTests.append(flashFinal)

        #initialise BT module and USB Dongle
        serial_port = serial.Serial(port=COM_PORT, baudrate=57600)
        ble_builder = BLEBuilder(serial_port)
        ble_parser = BLEParser(serial_port, callback=__analysePacket)
        
        timeout1 = connectToShineDUT(ble_builder, ieee)
        timeout2 = False

        if not timeout1:
            btTests = measureAverageRSSI(ble_builder)
            timeout2 = btTests['timeout']
            #if we timed out, we didn't complete these tests, so don't include them.
            if not timeout2:
                if 'rssi' in btTests: #check to make sure we completed the rssi test
                    stationOneTests.append(btTests['rssi'])
                stationOneTests.append(btTests['invalid']) #this one will always be in there if there wasn't a timeout

        #close link
        ble_builder.send("fe0a")

        #close device
        ble_parser.stop()
        serial_port.close()
        ieee =  ieee.translate(None, '.')

        timeoutPass = True
        if timeout1 or timeout2:
            timeoutPass = False

        map_timeout = {'True':1, 'False':0}

        timeoutTest = StationOneTimeoutTest(isPassed=timeoutPass, timestamp=time.time(), timeouts=[map_timeout[str(timeout1)], map_timeout[str(timeout2)]])
        stationOneTests.append(timeoutTest)

        #TEST DONE
        #create the overall station test object
        overallPass = True
        for each in stationOneTests:
            if not each.is_passed:
                overallPass = False

        #CREATED STATION ONE TEST OBJECT
        stationOneTest = StationTest("1."+str(ATE_ID), overallPass, "log_format_7", "0.0.21.ht03", stationOneTests, time.time())

        #CREATE MISFIT DEVICE OBJECT
        misfitDevice = Device(serial_number="",
                                ieee=ieee,
                                manufacturer='MisfitVS',
                                creation_time=time.time()
        )
        misfitDevice.physical['mechanical_revision'] = "1.0"
        misfitDevice.physical['pcb_revision'] = "0.9"
        misfitDevice.physical['pcba_revision'] = "0.9"
        misfitDevice.physical['color'] = "TBD"
        misfitDevice.physical['model_number'] = "TBD"
        misfitDevice.addStationTest(stationOneTest)

        #ADD ENTRY TO MFG DATABASE
        post_success = postTestEntryToMFGdb(stationOneTest, misfitDevice)

        # if this is false, it failed 5 times so ostensibly the internet is down.  do we fail the unit?  or pass and wait to import later?
        st = my_dict(stationOneTest)
        logentry['station_test'] = st
        logentry['mfg_db_post_success'] = post_success
    else:
        logentry['test_began'] = False
        logentry['station_test'] = {}
        logentry['mfg_db_post_success'] = False
        
    logentry['station_one_log_format'] = 'log_format_7'


    if logentry['mfg_db_post_success'] == True:
        logPostedEntry(logentry)
    else:
        logUnpostedEntry(logentry)


    #return UI to show operator
    if overallPass:
        return 0
    else:
        return 1

def logPostedEntry(logEntry):
    device_log_file = open('log_posted\\device.log', 'a')
    try:
        device_log_file.write(str(logEntry) + '\n')
    finally:
        device_log_file.close()

def logUnpostedEntry(logEntry):
    device_log_file = open('log_unposted\\device.log', 'a')
    try:
        device_log_file.write(str(logEntry) + '\n')
    finally:
        device_log_file.close()

def my_dict(obj):
    if not  hasattr(obj,"__dict__"):
        return obj
    result = {}
    for key, val in obj.__dict__.items():
        if key.startswith("_"):
            continue
        if isinstance(val, list):
            element = []
            for item in val:
                element.append(my_dict(item))
        else:
            element = my_dict(val)
        result[key] = element
    return result

def postTestEntryToMFGdb(stationOneTest, misfitDevice):
    tries = 0
    status = ''
    status2 = ''
    failed = True

    #TRY POSTING THIS ENTRY UP TO 5 TIMES
    if misfitDevice.ieee_address:
        while tries < 5 and failed:
            failed = False
            status = addStation1TestToDevice(misfitDevice.ieee_address, stationOneTest)
            if status == '400': #doesn't exist in DB, so create it
                status2 = postMisfitDeviceWithStation1Test(misfitDevice)
            
            if (status != '{}' and status != '400') or (status == '400' and status2 != '{}'):
                failed = True
                tries += 1
            print "attempt"
            print status
            print status2
        #IF IT FAILED 5 TIMES -> LOG IT TO FAIL FILE - FAIL THE UNIT?
        if tries == 5:
            print "FAILED STATION ONE ENTRY - INTERNET?"
            return False
    else:
        print "FAILED STATION ONE ENTRY - NO IEEE?"
        return False
    return True

def addStation1TestToDevice(ieee, stationOneTest):
    #TRANSLATE TO JSON AND POST
    testJSON = stationOneTest.jsonize()
    status = MDapi.misfitProductionPostStationTestForDevice(ieee, testJSON)
    return status

def postMisfitDeviceWithStation1Test(misfitDevice):
    #TRANSLATE TO JSON AND POST
    mdJSON = misfitDevice.jsonize()
    status = MDapi.misfitProductionPostMisfitDevice(mdJSON)
    return status

# Wrapper for launching a function in multiple instances
def runParallel(function, iterable, returned_code_list, log_queue):
    from multiprocessing import Process
    process = []
    for i in range(len(iterable)):
        process.append(Process(target=function,
                args=(iterable[i], returned_code_list, log_queue)))
        process[i].start()
    for p in process:
        p.join()

def readCc2541IEEEAddress(dut_parameters, log_queue):
    process = Popen(dut_parameters.srfpc_args_ieee, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    if 'IEEE MAC address read successfully' in stdout:
        return stdout[len(stdout)-17:]
    else:
        print stdout
        print stderr

def unlockEFM(dut_parameters, log_queue):
    process = Popen(dut_parameters.eac_args_unlock, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    print stdout
    print stderr
    #timeout = 5
    #start = datetime.datetime.now()
    #while process.poll() is None:
    #    time.sleep(0.1)
    #    now = datetime.datetime.now()
    #    if (now - start).seconds > timeout:
    #        return 2

    return process.returncode

def loadCc2541Firmware(dut_parameters, log_queue):
    process = Popen(dut_parameters.srfpc_args, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    print stdout
    print stderr
    return process.returncode

def loadEfm32Firmware(dut_parameters, log_queue, final):
    if final:
        process = Popen(dut_parameters.eac_args_final, stdout=PIPE, stderr=PIPE)
    else:
        process = Popen(dut_parameters.eac_args, stdout=PIPE, stderr=PIPE)

    stdout, stderr = process.communicate()
    print stdout
    print stderr
    return process.returncode

def __pretty(hex_string, seperator=None):
    '''
    pretty("\x01\x02\x03\xff")
    '01 02 03 FF'
    '''
    if seperator: 
        sep = seperator 
    else:
        sep = ' '
    hex_string = hex_string.encode('hex')
    a = 0
    out = ''
    for i in range(len(hex_string)):
        if a == 2:
            out = out + sep
            a = 0
        out = out + hex_string[i].capitalize()
        a = a + 1
    return out

def print_orderedDict(dictionary):
	result = ""
	for idx, key in enumerate(dictionary.keys()):
		if dictionary[key]:
			#convert e.g. "data_len" -> "Data Len"
			title = ' '.join(key.split("_")).title()
			if isinstance(dictionary[key], list):
				for idx2, item in enumerate(dictionary[key]):
					result += "{0} ({1})\n".format(title, idx2)
					result += print_orderedDict(dictionary[key][idx2])
			elif isinstance(dictionary[key], type(collections.OrderedDict())):
				result += '{0}\n{1}'.format(title, print_orderedDict(dictionary[key]))
			else:
				result += "{0:15}\t: {1}\n\t\t  ({2})\n".format(title, __pretty(dictionary[key][0], ':'), dictionary[key][1])
		else:
			result += "{0:15}\t: None".format(key)
	return result

def print_output((packet, dictionary)):
	result = print_orderedDict(dictionary)
	result += 'Dump:\n{0}\n'.format(__pretty(packet))
	return result

def __analysePacket((packet, dictionary)):
    global rssi
    global is_rssi_retrieved
    global scan_done
    global link_established
    global rssi_read
    global rssi_success
    global rssi_invalid
    global invalidRssiCount
    
    packet_str = __pretty(packet, '.')
    eventCode = packet_str[9:14]
    rssiValues = []
    print packet_str
    #PARSE RSSI RESPONSE
    if packet_str[3:5] == '0E':
        if packet_str[18:20] == '00' and packet_str[27:29] != '7F': #7F is -129 RSSI - invalid
            rssi = int(packet_str[27:29], 16) - 256
            rssi_read = True
            rssi_success = True
            print "PARSING RSSI: %s" % rssi
        else:
            if packet_str[27:29] == '7F':
                invalidRssiCount += 1
                if invalidRssiCount > MAX_INVALID_RSSI_COUNT:
                    rssi_invalid = True
            rssi_success = False
            rssi_read = True
            rssi = 0

    #LINK ESTABLISHED RESPONSE
    if eventCode == '05.06':
        print "Link established"
        link_established = True
