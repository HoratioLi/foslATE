from constants import *
from stationtwocodes import *

import sys
import collections
import serial
import time
import binascii
import MDapi

import helper.source_meter as SM

from pyblehci import BLEBuilder
from pyblehci import BLEParser
from model.device import *


#======================
# TO BE LOGGED
#======================
serialFromShine = ''
serialQR = ''
serialNumber = ''
zData1 = ''
zData2 = ''
zData3 = ''
zData = [zData1, zData2, zData3]
shineSelectedScanOne = {'ieee':'', 'rssi':'', 'currentSN':''}
shineSelectedScanTwo = {'ieee':'', 'rssi':'', 'currentSN':''}
rssi = ''
ieeeLog = ''
ieee = ''
ieeeLogReverse = ''
fw_rev = ''
testFailures = [-1, -1, -1, -1, -1, -1, -1, -1, -1]
operatingCurrent = []
avgOperatingCurrent = ''
accelCurrent = []
avgAccelCurrent = '-1'
timeout = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

#==========================
# STATE MANAGEMENT
#==========================
furthest = 0
testStatus = 0
link_established = False
is_rssi_retrieved = False
serial_done = False
serialReceived = False
serial_failed = False
zDataStatus = 2
scan_done = False
curent_scan = 1
fw_rev_read = False
charReadCount = 0
files_erased = False
got_file = False
erase_count = 0
streamCount = 0
startTime = 0
timeout_count = 0
adv_samples = 0

RSSI_THRESHOLD = -75
OPERATING_CURRENT_THRESHOLD_UPPER = .000170 #150 microamps
OPERATING_CURRENT_THRESHOLD_LOWER = .000110 #110 microamps
LEDCONFIRM_CURRENT_THRESHOLD_UPPER = .0046 #4.6 miliamps
LEDCONFIRM_CURRENT_THRESHOLD_LOWER = .0025 #2.5 miliamps

#=========================
# Number of retries for BT commands
#=========================
MAX_NUM_RETRIES = 3


Z_DATA_THRESHOLD_LOWER = 64025
Z_DATA_THRESHOLD_UPPER = 65075

ADV_SAMPLE_THRESHOLD = .000240 #200 microamps



BT_TIMEOUT = 10  #10 seconds is maximum time we will wait from issuing a BT command to receiving a response



colorMap = {
            'A':'GRAY', 
            'B':'BLACK', 
            'F':'RED', 
            'G':'TOPAZ', 
            'H':'CHAMPAGNE', 
            }




def resetState():
    #STATE MANAGEMENT
    global testStatus
    global furthest
    global link_established
    global is_rssi_retrieved
    global serial_done
    global serial_failed
    global serialFromShine
    global serialReceived
    global scan_done
    global current_scan
    global fw_rev_read
    global charReadCount
    global files_erased
    global got_file
    global erase_count
    global streamCount
    global startTime
    global timeout_count

    #LOGGING
    global ieee
    global rssi
    global ieeeLog
    global ieeeLogReverse
    global shineSelectedScanOne
    global shineSelectedScanTwo
    global zData
    global zData1
    global zData2
    global zData3
    global zDataStatus
    global serialQR
    global fw_rev
    global testFailures
    global operatingCurrent
    global avgOperatingCurrent
    global accelCurrent
    global avgAccelCurrent
    global serialNumber
    global serialFromShine
    global timeout
    global adv_samples

    #STATE MANAGEMENT    
    zDataStatus = 2
    serialReceived = False
    furthest = 0
    testStatus = 0
    link_established = False
    is_rssi_retrieved = False
    serial_done = False
    scan_done = False
    current_scan = 1
    fw_rev_read = False
    charReadCount = 0
    files_erased = False
    got_file = False
    erase_count = 0
    streamCount = 0
    startTime = 0
    timeout_count = 0

    #LOGGING
    serialFromShine = ''
    ieee = ''
    ieeeLog = ''
    ieeeLogReverse = ''
    rssi = ''
    zData1 = ''
    zData2 = ''
    zData3 = ''
    zData = [zData1, zData2, zData3]
    operatingCurrent = []
    avgOperatingCurrent = ''
    accelCurrent = []
    avgAccelCurrent = ''
    serialNumber = ''
    timeout = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
    shineSelectedScanOne = {'ieee':'', 'rssi':'', 'currentSN':''}
    shineSelectedScanTwo = {'ieee':'', 'rssi':'', 'currentSN':''}
    serialQR = ''
    fw_rev = ''
    testFailures = [-1, -1, -1, -1, -1, -1, -1, -1, -1]
    adv_samples = ''

def initializeSourceMeter():
    #initialize source meter and reset device
    success = SM.initialize()
    print str(success)
    if success:
        SM.outputOff()
        time.sleep(0.25)
        SM.setupVoltageAndBatchCurrent1()
        time.sleep(1)
    return success

def scanForShine():
    global shineSelectedScanOne
    global shineSelectedScanTwo
    global testFailures
    global ble_builder
    global current_scan
    
    testFailures[SCAN_FAIL] = 0

    discover_saturn_count = 0
    while discover_saturn_count < 3:
        #STARTING SCAN NUMBER ONE
        current_scan = 1
        print(print_output(ble_builder.send("fe04", mode="\x03")))

        #2.3 seconds of scanning is long enough!
        time.sleep(2.8)
        print(print_output(ble_builder.send("fe05")))

        #STARTING SCAN NUMBER TWO
        scan_done = False
        current_scan = 2
        print(print_output(ble_builder.send("fe04", mode="\x03")))

        #2.5 seconds of scanning is long enough!       
        time.sleep(2.8)
        print(print_output(ble_builder.send("fe05")))            
            
        print "Shine One: %s" % shineSelectedScanOne
        print "Shine Two: %s" % shineSelectedScanTwo
        
        if (shineSelectedScanOne['ieee'] != shineSelectedScanTwo['ieee']) or (shineSelectedScanOne['ieee'] == '' and shineSelectedScanTwo['ieee'] == ''):
            print "No matching shines with (max RSSIs, RSSI above threshold, & default serial)."
            if discover_saturn_count == 2:
                print "Three tries and no matches.  FAIL TEST."
                testFailures[SCAN_FAIL] = 1
                discover_saturn_count += 1
                shineSelectedScanOne = {'ieee':'', 'rssi':'', 'currentSN':''}
                shineSelectedScanTwo = {'ieee':'', 'rssi':'', 'currentSN':''}
            else:
                print "Trying again."
                resetState()
                discover_saturn_count += 1
        else:
            # we are done.  break from loop
            print "Shines match!"
            discover_saturn_count = 4

def operatingCurrentTest():
    global testFailures
    
    testFailures[ADV_SAMPLES_FAIL] = 0
    testFailures[AVG_CURRENT_FAIL] = 0

    operatingCurrent = []
    i = 0
    print "Measuring operating current."
    operatingCurrent = batchMeasureCurrent()
    averageOperatingCurrent = 0
    advSamples = 0
    for c in operatingCurrent:
        if c > ADV_SAMPLE_THRESHOLD:
            advSamples += 1
        else:
            averageOperatingCurrent += c

    if advSamples < 1 or advSamples > 2:
        print "not advertising or weird current failure"
        testFailures[ADV_SAMPLES_FAIL] = 1

    print "Adv Samples: %s" % advSamples

    if len(operatingCurrent) - advSamples != 0:
        averageOperatingCurrent = averageOperatingCurrent/(len(operatingCurrent) - advSamples)
        print "Average operating current: %s" % averageOperatingCurrent
        
        if averageOperatingCurrent > OPERATING_CURRENT_THRESHOLD_UPPER:
            print "max avg current fail"
            testFailures[AVG_CURRENT_FAIL] = 1
        if averageOperatingCurrent < OPERATING_CURRENT_THRESHOLD_LOWER:
            print "min avg current fail"
            testFailures[AVG_CURRENT_FAIL] = 1

    return (operatingCurrent, averageOperatingCurrent, advSamples)

def setupVariables():
    global shineSelectedScanTwo
    global ieeeString
    global ieeeLog
    global ieeeLogReverse
    global ble_builder

    ieeeLog = ieeeLog.split('.')
    ieeeLogReverse = ''
    ieeeString = ''
    for each in shineSelectedScanTwo['ieee']:
        ieeeLogReverse = ieeeLogReverse + each + '.'
        ieeeString = each + ieeeString
    ieeeLogReverse = ieeeLogReverse[0:len(ieeeLogReverse) - 1]
    print "IEEE LOG Reverse: " + str(ieeeLogReverse).translate(None, '.')
    print "IEEE String: " + ieeeString
    ieeeString = str(binascii.unhexlify(ieeeString))
    print shineSelectedScanTwo
    print ieeeString

    # #for log purposes
    # ieeeLog = ieeeLog.split('.')
    # ieeeLogReverse = ''
    # for each in ieeeLog:
    #     ieeeLogReverse += each[::-1]
    #     ieeeLogReverse += '.'
    # ieeeLogReverse = ieeeLogReverse[0:len(ieeeLogReverse)-1]

    # #for connecting
    # ieeeString = ''
    # for each in shineSelectedScanTwo['ieee']:
    #     ieeeString = each + ieeeString
    # ieeeString = str(binascii.unhexlify(ieeeString))


def connectToShine():
    global ieeeString
    global ble_builder
    global link_established
    global timeout_count
    global timeout
    
    retry_count = 0
    link_established = False
    while retry_count < MAX_NUM_RETRIES and link_established == False:

        #open connection to Shine
        print "Opening Bluetooth Connection with Shine of lowest RSSI"
        print ieeeString
        print(print_output(ble_builder.send("fe09", high_duty_cycle = '\x01', peer_addr=ieeeString)))

        #wait for link
        resetTimer()
        while not link_established:
            time.sleep(0.1)
            if getTimePassed() > BT_TIMEOUT:
                retry_count = retry_count + 1
                if retry_count == MAX_NUM_RETRIES:
                    timeout[timeout_count][CONNECT_TO_SHINE] += 1
                break
            pass
        pass



def sendBTCommandWRetry(var_name, command, handle, value, phase):
    global serial_done    
    global ble_builder
    global got_file
    global testFailures
    global streamCount
    global currCount
    global erase_count
    global fw_rev_read
    global serialReceived


    retry_count = 0
    while retry_count < MAX_NUM_RETRIES and (eval(var_name) == False or eval(var_name) == ''):

        #open connection to Shine
        print "Sending " + command + " and checking " + var_name + " Retry count " + str(retry_count)
        print(print_output(ble_builder.send(command, handle=handle, value=value)))

        #wait for link
        resetTimer()
        while not eval(var_name) or eval(var_name) == '':
            time.sleep(0.1)
            if getTimePassed() > BT_TIMEOUT:
                retry_count += 1
                if retry_count == MAX_NUM_RETRIES:
                    timeout[timeout_count][phase] += 1
                break
            pass
        pass



def setupCharacteristics():
    global serial_done
    global ble_builder

    serial_done = False
    print "enabling notifications for data characteristic"
    sendBTCommandWRetry("serial_done", "fd92", handle="\x03\x02", value="\x01\x00", phase=CONNECT_TO_SHINE)
    serial_done = False


    sendBTCommandWRetry("serial_done", "fd92", handle="\x06\x02", value="\x01\x00", phase=CONNECT_TO_SHINE)
    serial_done = False

    sendBTCommandWRetry("serial_done", "fd92", handle="\x09\x02", value="\x01\x00", phase=CONNECT_TO_SHINE)
    serial_done = False
    
def getAndEraseFiles():
    global ble_builder
    global got_file
    global testFailures
    global streamCount
    global currCount
    global erase_count

    got_file = False
    streamCount = 0
    print "Getting the latest file."
    sendBTCommandWRetry("got_file", "fd92", handle="\x05\x02", value="\x01\x00\x01\x00\x00\x00\x00\xFF\x00\x00\x00", phase=GET_AND_ERASE_FILES)
 
    print "Aborting get."
    print(print_output(ble_builder.send("fd92", handle="\x05\x02", value="\x07\x00\x01"))) #abort
    time.sleep(.5)
    streamCount += 1 # so accel streaming works.
        
    print "Erasing file."
    currCount = 0
    print(print_output(ble_builder.send("fd92", handle="\x05\x02", value="\x03\x00\x01"))) #erase file
    resetTimer()
    while not files_erased:
        if erase_count != currCount:
            print "Erasing file."
            print(print_output(ble_builder.send("fd92", handle="\x05\x02", value="\x03\x00\x01"))) #erase file 
            resetTimer()
            currCount = erase_count
        time.sleep(0.1)
        if getTimePassed() > BT_TIMEOUT:
            timeout[timeout_count][GET_AND_ERASE_FILES] += 1
            break 
        pass
    print "Done erasing files."

def checkFirmwareRevision():
    global ble_builder
    global fw_rev_read
    global fw_rev
    global testFailures
    fw_rev_read = False
    
    testFailures[CHECK_FW_FAIL] = 0

    streamCount = 0
    print "Getting the latest file."
    sendBTCommandWRetry("fw_rev_read", "fd8a", handle="\x36\x00", value=None, phase=CHECK_FW_REV)

    # print "Checking firmware revision"
    # print(print_output(ble_builder.send("fd8a", handle="\x36\x00")))
    # resetTimer()
    # while not fw_rev_read:
    #     time.sleep(0.1)
    #     if getTimePassed() > BT_TIMEOUT:
    #         timeout[timeout_count][CHECK_FW_REV] += 1
    #         break
    #     pass

    if fw_rev != '0.0.28x.boot2_prod':
        print "wrong firmware!"
        print(print_output(ble_builder.send("fe0a")))
        testFailures[CHECK_FW_FAIL] = 1

def checkAccelerometerStreaming():
    global ble_builder
    global zData1
    global serial_done
    global testFailures
    global zDataStatus

    testFailures[ACCEL_STREAM_FAIL] = 0

    zData1 = ''
    serial_done = False
    
    #start streaming accelerometer data
    print "streaming accelerometer data"
    sendBTCommandWRetry("zData1", "fd92", handle="\x05\x02", value="\x01\x01\x80\x00\x00\x00\x00\x00\x00\x00\x00", phase=ACCEL_STREAMING)
   
    # print(print_output(ble_builder.send("fd92", handle="\x05\x02", value="\x01\x01\x80\x00\x00\x00\x00\x00\x00\x00\x00")))
    # resetTimer()
    # while zData1 == '':
    #     time.sleep(0.1)
    #     if getTimePassed() > BT_TIMEOUT:
    #         print "TIMED OUT1"
    #         timeout[timeout_count][ACCEL_STREAMING] += 1
    #         break
    #     pass

    #abort streaming
    serial_done = False
    sendBTCommandWRetry("serial_done", "fd92", handle="\x05\x02", value="\x07\x01\x80", phase=ACCEL_STREAMING)
    serial_done = False

    # serial_done = False
    # print(print_output(ble_builder.send("fd92", handle="\x05\x02", value="\x07\x01\x80")))
    # resetTimer()
    # while not serial_done:
    #     time.sleep(0.1)
    #     if getTimePassed() > BT_TIMEOUT:
    #         print "TIMED OUT2"
    #         timeout[timeout_count][ACCEL_STREAMING] += 1
    #         break
    #     pass
    # serial_done = False

    if zDataStatus == 0:
        print "Z data fail"
        testFailures[ACCEL_STREAM_FAIL] = 1

def confirmLEDCurrent():
    global testFailures

    testFailures[CONFIRM_LED_FAIL] = 0
    
    accelCurrent = batchMeasureCurrent()
    sum = 0
    
    for each in accelCurrent:
        sum += each
    average = sum/len(accelCurrent)
    
    print "Average LED CONFIRM current: %s" % average
    
    if average < LEDCONFIRM_CURRENT_THRESHOLD_LOWER or average > LEDCONFIRM_CURRENT_THRESHOLD_UPPER:
        print "LED CONFIRM Current fail: %s" % average
        testFailures[CONFIRM_LED_FAIL] = 1
    
    time.sleep(.5)
    return (accelCurrent, average)

def serialProgramSequence():
    global shineSelectedScanTwo
    global serialQR
    global ble_builder
    global serial_done
    global testFailures
    global serial_failed
    global serialReceived
    global serialNumberX
    global serialFromShine

    testFailures[SN_PROGRAM_FAIL] = 0
    testFailures[SN_READ_FAIL] = 0
    
    if shineSelectedScanTwo['currentSN'] != serialQR:
        #send BT program Serial command with serial from QR
        #verify serial was programmed
        serial_done = False
        serialReceived = False
        serial_failed = False
        
        # print "Sending set serial # command over BT"
        # print(print_output(ble_builder.send("fd92", handle="\x02\x02", value="\x02\x07\x01" + serialNumberX + "\x00")))
        # time.sleep(0.5)
        # resetTimer()
        
        # while not serial_done:
        #     print "%s" % serial_done
        #     time.sleep(0.1)
        #     if getTimePassed() > BT_TIMEOUT:
        #         timeout[timeout_count][SERIAL_PROGRAMMING] += 1
        #         break
        #     if serial_failed:
        #         print "Failed to write serial # after establishing link."
        #         testFailures[SN_PROGRAM_FAIL] = 1
        #         break
        #     pass
        
        retry_count = 0
        while retry_count < MAX_NUM_RETRIES and not serial_done:
            serial_failed = False
            #open connection to Shine
            print "Sending set serial # command over BT"
            print(print_output(ble_builder.send("fd92", handle="\x02\x02", value="\x02\x07\x01" + serialNumberX + "\x00")))
            time.sleep(0.5)
            #wait for link
            resetTimer()
            while not serial_done:
                time.sleep(0.1)
                if getTimePassed() > BT_TIMEOUT:
                    retry_count += 1
                    if retry_count == MAX_NUM_RETRIES:
                        timeout[timeout_count][phase] += 1
                    break

                if serial_failed:
                    print "Failed to write serial # after establishing link."
                    retry_count += 1
                    if retry_count == MAX_NUM_RETRIES:
                        testFailures[SN_PROGRAM_FAIL] = 1
                    break
                pass
            pass

        #read serial from shine 
        sendBTCommandWRetry("serialReceived", "fd8a", handle="\x34\x00", value=None, phase=SERIAL_PROGRAMMING)
    
        # print(print_output(ble_builder.send("fd8a", handle="\x34\x00")))
        # resetTimer()
        # while not serialReceived:
        #     time.sleep(0.1)
        #     if getTimePassed() > BT_TIMEOUT:
        #         timeout[timeout_count][SERIAL_PROGRAMMING] += 1
        #         break
        #     pass

        print "Serial received from shine: %s vs. serial from QR scan: %s" % (serialFromShine, serialNumberX)
        #check if they are equal
        if not (serialFromShine == serialNumberX):
            print "Failed to verify serial # after establishing link."
            testFailures[SN_READ_FAIL] = 1
    else:
        serialFromShine = serialNumberX #for logging purposes.
        
def initializeDongle():
    print(print_output(ble_builder.send("fe00", max_scan_rsps='\x59')))
    
def closeLink():
    print(print_output(ble_builder.send("fe0a")))

def executeQRSerialSequence(serialNumber):
    global testStatus
    global link_established
    global is_rssi_retrieved
    global serial_done
    global serial_failed
    global serialFromShine
    global ieee
    global ieeeLog
    global ieeeLogReverse
    global scan_done
    global rssi
    global serialReceived
    global shineSelectedScanOne
    global shineSelectedScanTwo
    global current_scan
    global zData1
    global zData2
    global zData3
    global zDataStatus
    global serialQR
    global fw_rev_read
    global testFailures
    global files_erased
    global got_file
    global erase_count
    global streamCount
    global ble_builder
    global serialNumberX
    global operatingCurrent
    global avgOperatingCurrent
    global accelCurrent
    global avgAccelCurrent
    global serialFromShine
    global fw_rev
    global adv_samples
    

################## ADDED BY GABE ########### FORCE ALL VARS TO INIT STATE
    resetState()
#########################################################################

    stationTwoTests = []

    if not MDapi.internet_on():
        resetState()
        return -2

    #SERIAL NUMBER CLEANING
    serialNumberX = serialNumber
    average = 0
    ieeeLogReverse = ''
    b = 1
    for letter in serialNumber:
        hex = letter.encode('hex')
        hex = hex.upper()
        serialQR += hex
        if b < len(serialNumber):
            serialQR += '.'
        b += 1

    #initialize
    success = initializeSourceMeter()
    if not success:
        return -1

    #connect to USB radio
    serial_port = serial.Serial(port=COM_PORT, baudrate=57600)

    #setup bt module
    ble_builder = BLEBuilder(serial_port)
    ble_parser = BLEParser(serial_port, callback=__analysePacket)

    #test sequence
    while(testStatus < 10):
        testStatus = executeNextStep(testStatus)

    #close port and stop ble parsing
    ble_parser.stop()
    serial_port.close()

    #return pass or fail to screen
    totalFailures = 0
    print "Failures: %s" % testFailures
    for each in testFailures:
        if each != -1:
            totalFailures += each

    print "TOTAL FAILURES: " + str(totalFailures)

    if not totalFailures:
        global_pass = True
    else:
        global_pass = False

    #BUILD STATION TEST OBJECT
    initialSerial = cleanSN(shineSelectedScanTwo['currentSN'])

    timestamp = time.time()

    if testFailures[SCAN_FAIL] != -1:
        stationTwoTests.append(ScanTest(not testFailures[SCAN_FAIL], timestamp, shineSelectedScanTwo['rssi']))
    if testFailures[ADV_SAMPLES_FAIL] != -1:
        stationTwoTests.append(AdvSamplesTest(not testFailures[ADV_SAMPLES_FAIL], timestamp, adv_samples))
    ### WTF??? What is testFailures[OPCURTEST]?????
    if testFailures[AVG_CURRENT_FAIL] != -1:
        stationTwoTests.append(OperCurrentTest(not testFailures[AVG_CURRENT_FAIL], timestamp, operatingCurrent, avgOperatingCurrent))
    ### WTF??? What is testFailures[CHECK_FW_REV]?????  CHECK_FW_FAIL ????
    if testFailures[CHECK_FW_FAIL] != -1:
        stationTwoTests.append(FirmwareCheckTest(not testFailures[CHECK_FW_FAIL], timestamp, "0.0.28x.boot2_prod", fw_rev))
    if testFailures[ACCEL_STREAM_FAIL] != -1:
        stationTwoTests.append(AccelZDataTest(not testFailures[ACCEL_STREAM_FAIL], timestamp, zData))
    if testFailures[CONFIRM_LED_FAIL] != -1:
        stationTwoTests.append(ConfirmLEDCurrentTest(not testFailures[CONFIRM_LED_FAIL], timestamp, accelCurrent, avgAccelCurrent))
    if testFailures[SN_PROGRAM_FAIL] != -1:
        stationTwoTests.append(WriteSerialTest(not testFailures[SN_PROGRAM_FAIL], timestamp, serialNumber))
    if testFailures[SN_READ_FAIL] != -1:
        stationTwoTests.append(ReadSerialTest(not testFailures[SN_READ_FAIL], timestamp, initialSerial, serialFromShine))
    if testFailures[TIMEOUT_FAIL] != -1:
        stationTwoTests.append(StationTwoTimeoutTest(not testFailures[TIMEOUT_FAIL], timestamp, timeout[0]))
 
    st = StationTest("2."+str(ATE_ID), global_pass, "log_format_7", fw_rev, stationTwoTests, timestamp)

    #initialize log stuff
    post_success = False
    update_success = False
    duplicate = ''
    ieee_db = ''

    entry = {}
    #POST STATION TEST TO MANUFACTURING DATABSE
    if ieeeLogReverse:
        ieee_db = str(ieeeLogReverse).translate(None, '.')
        print "Serial from Shine: " + serialFromShine
        print "SerialQR: " + serialQR
        (post_success, update_success, duplicate) = testToMFGDB(ieee_db, serialFromShine, st)
        print duplicate
        global_pass = global_pass and not duplicate
    
    entry['ieee'] = ieee_db
    entry['station_two_test'] = my_dict(st) #OBJECT -> DICTIONARY
    entry['final_serial'] = serialFromShine

    #did we fail or pass the unit in the factory?
    entry['global_pass'] = global_pass

    #what was the format?
    entry['station_two_log_format'] = 'log_format_7'

    #did we successfully post the test?
    entry['mfg_db_post_success'] = post_success

    #did we update serial/pass, physicals, and update/check duplicate?
    entry['mfg_db_update_success'] = update_success

    # was it a duplicate?
    entry['duplicate'] = duplicate
    
    #makes it easier to manage logs
    if post_success and update_success:
        print "Entry Successfully posted and updated in database"
        logPostedEntry(entry)
    else:
        print "Failed to log into database. Entry logged for future upload"
        logUnpostedEntry(entry)
    
    #UPDATE UI FOR FACTORY OPERATOR
    if global_pass:
        resetState()
        return 1
    else:
        resetState()
        return 0

def testToMFGDB(ieee_db, serialFromShine, st):
    (post_success, update_sucess, duplicate) = stationTwoEntryToDB(ieee_db, serialFromShine, st)
    return (post_success, update_sucess, duplicate)


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

def lookupPhysicalsForSerial(serial):
    if len(serial) > 6:
        if serial[3] in colorMap:
            return (colorMap[serial[3]], serial[0:5])
        else:
            return ('UNKNOWN', serial[0:5])
    else:
        return ('UNKNOWN', 'XXXXXX')

def executeNextStep(phase):
    global furthest
    global timeout_count
    global timeout
    global accelCurrent
    global avgAccelCurrent
    global operatingCurrent
    global avgOperatingCurrent
    global zData
    global adv_samples
    
    testFailures[TIMEOUT_FAIL] = 0

    if phase == INITIALIZE_DONGLE:
        print "Initializing USB Dongle."
        initializeDongle() #HAS TO WORK
    elif phase == SCANNING:
        print "Scanning for Shine"
        scanForShine() #HAS TO WORK
    elif phase == OPERATING_CURRENT_TEST:
        print "Testing Operating Current"
        result = operatingCurrentTest()
        operatingCurrent = result[0]
        avgOperatingCurrent = result[1]
        adv_samples = result[2]
        #if we didn't find a shine it's done
        if testFailures[SCAN_FAIL] == 1:
            phase = CLOSE_LINK
            return phase
        setupVariables()

        #### CHeck if Serial number already in database.
        #### If it is, then Check if this is the same device
        #### otherwise, this is about to create a duplicate SN, so STOP

        print "ENS: IEEE: " + ieeeLogReverse
        ieee_db = str(ieeeLogReverse).translate(None, '.')
        print "ENS: SerialQR: " + serialQR
        print "ENS: SerialNumber: " + serialNumberX
        SNexists = checkForDeviceFromSerial(serialNumberX)
        print "SNexists: " + str(SNexists)
        if SNexists:
            response = MDapi.misfitProductionGetDeviceWith(ieee_db, serialNumberX)
            print response
            if response == -1:
                print "Device not found. This is not the entry in the dbase"
                print "DUPLICATE SN FOUND!!!, ENDING TESTS"
                ### Re-using the SN Program Fail tag

                testFailures[SN_PROGRAM_FAIL] = 1
                phase = CLOSE_LINK
                return phase
            else:
                print "Updating entry in dbase, ok to proceed" 
                print "Is Duplicate SN: " + str(response['is_duplicated'])


    elif phase == CONNECT_TO_SHINE:
        print "Connecting to Shine."
        connectToShine() #HAS TO WORK
        setupCharacteristics()#HAS TO WORK
    elif phase == GET_AND_ERASE_FILES:
        print "Getting and Erasing Files."
        getAndEraseFiles()
    elif phase == CHECK_FW_REV:
        print "Checking FW"
        checkFirmwareRevision() #this can fail
    elif phase == ACCEL_STREAMING:
        print "Accel streaming"
        checkAccelerometerStreaming() #this can fail
        zData = [zData1, zData2, zData3]
    elif phase == CONFIRM_LED_CURRENT:
        print "LED curr"
        results = confirmLEDCurrent() #this can fail
        accelCurrent = results[0]
        avgAccelCurrent = results[1]
    elif phase == SERIAL_PROGRAMMING:
        print "SERIAL PROGRAMMING"
        serialProgramSequence() #this can fail
    elif phase == CLOSE_LINK:
        closeLink() #NEEDS TO RUN
        phase += 1
        return phase
    else:
        pass

    #if we haven't had a timeout before
    if timeout_count == 0:
        #if this phase didnt time out, continue.
        if timeout[0][phase] == 0:
            phase += 1
        else: #this phase timed out, so we're done
            testFailures[TIMEOUT_FAIL] = 1
            phase = CLOSE_LINK

    return phase

def resetTimer():
    global startTime
    startTime = time.time()

def getTimePassed():
    global startTime
    return time.time() - startTime

def addStation2TestToDevice(ieee, st):
    testJSON = st.jsonize()
    status = ''
    tries = 0

    while status != '{}' and tries < 5:
        status = MDapi.misfitProductionPostStationTestForDevice(ieee, testJSON)
        tries += 1

    if tries == 5:
        return False
    else:
        return True

def updateDeviceWithSerialAndPass(ieee, serial, passed):
    update = {'device':{'serial_number': serial, 'is_passed':passed}}
    updateJSON = json.dumps(update)

    status = -1
    tries = 0

    while status == -1 and tries < 5:
        status = MDapi.misfitProductionUpdateDeviceWith(ieee, updateJSON)
        tries += 1

    if tries == 5:
        return False
    else:
        return True

def updateDevicePhysicalsWithColorAndModel(ieee, color, model_number):
    update = {'physical':{'color':color, 'model_number':model_number}}
    updateJSON = json.dumps(update)

    status = -1
    tries = 0

    while status == -1 and tries < 5:
        status = MDapi.misfitProductionUpdateDevicePhysicals(ieee, updateJSON)
        tries += 1

    if tries == 5:
        return False
    else:
        return True

def isDuplicate(ieee, serial):
    device = MDapi.misfitProductionGetDeviceWith(ieee, serial)
    
    if device != -1:
        if device['is_duplicated']:
            return (True, True)
        else:
            return (True, False)
    return (False, False)

def checkForDeviceFromSerial(serial):
    results = MDapi.misfitProductionGetDeviceFromSerial(serial)
    if results == -1:
        print "No Response from dbase - Serial Query"
        return False
    if results['devices']:
        print results['devices']
        print "Serial Number found in Database"
        return True
    return False  

def stationTwoEntryToDB(ieee, serial, stationTest):
    posted_st = False
    did_updates = False
    duplicate = False

    (color, model_number) = lookupPhysicalsForSerial(serial)
    posted_st = addStation2TestToDevice(ieee, stationTest)
    
    if posted_st and stationTest.is_passed:
        did_updates = updateDeviceWithSerialAndPass(ieee, serial, stationTest.is_passed)
        print "Updated Serial and Pass " + str(did_updates)
        did_updates = updateDevicePhysicalsWithColorAndModel(ieee, color, model_number)
        print "Updated Device Physicals with Color and Model " + str(did_updates)
        (did_updates, duplicate) = isDuplicate(ieee, serial)
        print "Checked for Duplicate SNs " + str(did_updates)
        if duplicate:
            did_updates = updateDeviceWithSerialAndPass(ieee, serial, False)
            print "Is Duplicate!!! " + str(did_updates)

    if stationTest.is_passed == False:
        did_updates = True

    #RETURN WHETHER BOTH PARTS COMPLETED SUCCESSFULLY OR NOT - and if it is a duplicate
    return (posted_st, did_updates, duplicate)

def cleanSN(sn):
    initial = sn.split('.')
    logInitialSN = ''
    for each in initial:
        logInitialSN += each.decode('hex')
    return logInitialSN

def logPostedEntry(entry):
    serial_log_file = open('log_posted\\serial.log', 'a')
    try:
        serial_log_file.write(str(entry) + '\n')
    finally:
        serial_log_file.close()

def logUnpostedEntry(entry):
    serial_log_file = open('log_unposted\\serial.log', 'a')
    try:
        serial_log_file.write(str(entry) + '\n')
    finally:
        serial_log_file.close()

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
    return ''
    return result

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

def __analysePacket((packet, dictionary)):
    global link_established
    global serial_done
    global serial_failed
    global ieee
    global ieeeLog
    global is_rssi_retrieved
    global serialFromShine
    global scan_done
    global rssi
    global serialReceived
    global shineSelectedScanOne
    global shineSelectedScanTwo
    global serialQR
    global zData1
    global zData2
    global zData3
    global zDataStatus
    global fw_rev_read
    global charReadCount
    global fw_rev
    global testFailures
    global files_erased
    global got_file
    global erase_count
    global streamCount
    
    packet_str = __pretty(packet, '.')
    eventCode = packet_str[9:14]
    status = packet_str[15:17]
    eventType = packet_str[18:20]

    #DEVICE INFORMATION EVENT
    if eventCode == '0D.06':
        print "Device Info Packet"
        #only look at packets where serial number is default (not set yet)
        #connectable undirect advertisement (has serial number & rssi)
        if eventType == '00':
            currentSN = packet_str[69:98]
            if currentSN == '39.38.37.36.35.34.33.32.31.30' or currentSN == serialQR:
                tempRSSI = int(packet_str[42:44], 16) - 256
                print "got blank or current serial, getting RSSI", packet_str[42:44], tempRSSI, (packet_str[24:41])
                if tempRSSI > RSSI_THRESHOLD:
                    rssi = tempRSSI #only write to global after pass checks
                    ieeeLog = (packet_str[24:41])[::-1]
                    ieee = [_ for _ in reversed(packet_str[24:41].split('.'))]
                    is_rssi_retrieved = True
                    print "RSSI", rssi
                    if current_scan == 1:
                        if tempRSSI > shineSelectedScanOne['rssi'] or shineSelectedScanOne['rssi'] == '':
                            shineSelectedScanOne['rssi'] = tempRSSI
                            shineSelectedScanOne['ieee'] = ieee
                            shineSelectedScanOne['currentSN'] = currentSN
                    else:
                        if tempRSSI > shineSelectedScanTwo['rssi'] or shineSelectedScanTwo['rssi'] == '':
                            shineSelectedScanTwo['rssi'] = tempRSSI
                            shineSelectedScanTwo['ieee'] = ieee
                            shineSelectedScanTwo['currentSN'] = currentSN

    #Read Char 
    if eventCode == '0B.05':
        if charReadCount == 0:
            fwRevReceived = [_ for _ in reversed(packet_str[27:80].split('.'))]
            fwRev = ''
            for each in fwRevReceived:
                fwRev = each + fwRev
            fw_rev = str(binascii.unhexlify(fwRev))
            print fw_rev
            fw_rev_read = True
            charReadCount += 1
        else:
            print "SN PACKET", packet_str[27:56]
            snRecieved = [_ for _ in reversed(packet_str[27:56].split('.'))]
            snRecievedString = ''
            for each in snRecieved:
                snRecievedString = each + snRecievedString
            print "SN Packet: %s " % snRecievedString
            serialFromShine = str(binascii.unhexlify(snRecievedString))
            print "SN Packet: %s " % serialFromShine
            serialReceived = True

    #ATT Value Notification
    if eventCode == '1B.05':
        #streaming data and s/n and file data sent in these type of packets
        if packet_str[24:26] == '16' and zData1 =='':
            if streamCount == 0:
                pass
            else:
                print "Stream"
                #streaming data
                zData1 = packet_str[54:56] + packet_str[51:53]
                zData2 = packet_str[72:74] + packet_str[69:71]
                zData3 = packet_str[90:92] + packet_str[87:89]
                zData1 = int(zData1, 16)
                zData2 = int(zData2, 16)
                zData3 = int(zData3, 16)
                if zData1 > Z_DATA_THRESHOLD_UPPER or zData1 < Z_DATA_THRESHOLD_LOWER:
                    zDataStatus = 0
                if zData2 > Z_DATA_THRESHOLD_UPPER or zData2 < Z_DATA_THRESHOLD_LOWER:
                    zDataStatus = 0
                if zData3 > Z_DATA_THRESHOLD_UPPER or zData3 < Z_DATA_THRESHOLD_LOWER:
                    zDataStatus = 0
                print "zdata", zData1, zData2, zData3
        if packet_str[33:35] == '02':
            #GET RESPONSE
            print "GET RESPONSE PACKET"
            if packet_str[42:44] == '02' or packet_str[36:38] == '00':
                print "Get response successful."
                got_file = True
        if packet_str[33:35] == '04':
            print "ERASE RESPONSE PACKET"
            erase_count += 1 #this will cause the main thread to erase another file
            if packet_str[42:44] == '02':
                #invalid file handle so we've erase all files
                files_erased = True

    #DEVICE DISCOVERY DONE
    if eventCode == '01.06':
        print "Device discovery done"
        scan_done = True

    #LINK ESTABLISHED RESPONSE
    if eventCode == '05.06':
        print "Link established"
        link_established = True

    #ATT_ErrorRsp
    if eventCode == '01.05':
        serial_failed = True
    
    #successful ATT_ReadRsp
    if eventCode == '13.05' and status == '00':
        serial_done = True
    

if __name__ == "__main__":
    main(sys.argv[1:])