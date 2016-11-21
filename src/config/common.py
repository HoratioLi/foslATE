#!/usr/bin/env python
"""
Common Configuration File
Created: 2015 Nov 11
Author: James Quen

Description:
Common configuration file for all project.
"""

import os
import itertools
from ate_settings import *
from local_constants import *
from utilities.gitCommands import *

#===============================================================================
# PROJECTS
#===============================================================================
projectList=["Venus", "Apollo", "Aquila", "SaturnMKII", "Pluto", "BMW", "Silvretta", "Sausage", "SAM"]

#===============================================================================
# SERIAL PORT CONFIGURATION
#===============================================================================
USB_RADIO_PATH = '/dev/ttyACM0' # Set this based on the appropriate serial port on the Raspberry Pi
SERIAL_PORT = '/dev/ttyAMA0'    # Set this based on the appropriate serial port on the Raspberry Pi

AGILENT_BASE_ADDRESS = 2391
AGILENT_SUB_ADDRESS = 6663

LUNCHBOX = True                 # Set this based on the appropriate version of the ATE station.

#===============================================================================
# Number of retries for state machine, BT commands, database commands
#===============================================================================
MAX_NUM_RETRIES_BT = 3              # Max number of retries for bluetooth
BT_TIMEOUT = 10                     # 10 seconds is maximum time we will wait from issuing a BT command to receiving a response
STATE_MACHINE_TIMEOUT = 10
SCAN_FOR_DUT = False                # Scan for devices while opening connection

# Set behavior around database posts and timeouts
MAX_DATABASE_POST_ATTEMPTS = 10
DB_POST_TIMEOUT = 5                 # Seconds to try before timing out

# Set behavior around database reads and timeouts
MAX_DATABASE_READ_ATTEMPTS = 10     
DB_READ_TIMEOUT = 2                 # Seconds to try before timing out

# Set behavior around internet/database checking and timeouts
MAX_INTERNET_CONNECT_ATTEMPTS = 3

BLE_DELAY = 0.5                    # Delay 0.5 seconds between BLE tests.  If the commands are issued too quickly, it's possible there could be a BLE timeout.
#===============================================================================
# GPIO pins for Raspberry Pi
#===============================================================================

PADS_0_TO_27                        = 0     #This is the 0th pad groupd for the raspberry pi
GPIO_DRIVE_STRENGTH_PADS_0_TO_27    = 7     #This is the pad drive strength 5 = 12mA
                                            #                       default 3 = 8mA
                                            # 7 = 16mA

# Programming control pins
FLASHER_OK_PIN = 7
FLASHER_BUSY_PIN = 8 
FLASHER_START_PIN = 25
#PROGRAMMER_ENABLED = True
IN_JTAG_VCC_CTL = 11          

# Test Pins
MFG_TRIG_PIN = 17               # Signal from RPi to DUT.  Enters test mode and also tells DUT to move to next test.
MFG_TOGGLE_PIN = 22             # Signal from DUT to RPi.  Tells RPi to move to next test..
MFG_INFO_PIN = 15               # Signal from DUT to RPi.  Communicates UART data to RPi.
     
POWER_PIN = 24
VOLTAGE_TEST_PIN = 4
GPIO_HI = str(1)
GPIO_LO = str(0)
GP_DELAY_TIME = 0.001
POGOPIN_TEST_PIN = 5
POGOPIN_RELAY_PIN = 6
FIXTURE_CLOSED_PIN = 2

# This only gets used for Aquila
# Turn this on for the mac address test and the orientation test for Aquila only, else it stays off
IN_MFG_INFO_CTL = 10

# For SAM.  Configure them as inputs to read the rotating plate encoder
ENCODER_A0=16
ENCODER_A1=20
ENCODER_A2=21

# For SAM.  Configure them as outputs to actuate the pusher pistons.
PUSH1_ACTUATOR=13
PUSH2_ACTUATOR=19
PUSH3_ACTUATOR=26

# For SAM. Used for controlling relay to connect function generator to DUT.
CRYSTAL_CAL_PIN=12
#===============================================================================
# COMMON SETTINGS
#===============================================================================

# True if the code is being run on a Raspberry Pi
IS_RUNNING_ON_PI = os.path.isdir("/home/pi")

# DEFAULTS 
NUM_READINGS = 1                # How many readings to take for each measurement
DEFAULT_CURRENT_RANGE = 0.1     # 100 mA
MAX_INVALID_RSSI_COUNT = 10
SERIAL_TIMEOUT = 0.25
BUTTON_TOGGLE_TIME = 0.1      # Duration of the GPIO button pin toggle 

PI_VOLTAGE_LOWER = 2.0          
PI_VOLTAGE_UPPER = 5.0

if STATION_ID == 2:
    SAVE_OP_CURRENT_CSV = False # Set to True to save operating current test results in a csv
    SAVE_OP_CURRENT_PNG = False # Set to True to save operating current test results as a png
elif STATION_ID == 3:
    SAVE_OP_CURRENT_CSV = False # Set to True to save operating current test results in a csv
    SAVE_OP_CURRENT_PNG = False # Set to True to save operating current test results as a png

#===============================================================================
# FILE PATHS
#===============================================================================

PATH_TO_LOGS = '/home/pi/misfit/Production/src/'
STATUS_FILE = '/home/pi/misfit/Production/src/prev_test_data/status.txt'
BATTERY_PASSED_FILE = '/home/pi/misfit/Production/src/prev_test_data/battery_passed.txt'
JSON_FILE = '/home/pi/misfit/Production/src/prev_test_data/test_json'
IMAGE_FILE_PATH = '/home/pi/misfit/Production/src/view/images/batteryPlot.png'

DELIMITER = '_'

#========================================================================================
# COMMON PARAMETER SETUP
#========================================================================================
params = {}

params['device_type'] = DEVICE_TYPE
params['debug_mode'] = DEBUG_MODE
params['verbose_mode'] = VERBOSE_MODE
params['stop_after_fail'] = STOP_AFTER_FAIL
params['num_readings'] = NUM_READINGS
params['serial_timeout'] = SERIAL_TIMEOUT
params['testIndex'] = 0
params['numTests'] = 0
params['img_file_path'] = IMAGE_FILE_PATH
params['isRunningOnPi'] = IS_RUNNING_ON_PI
params['default_current_range'] = DEFAULT_CURRENT_RANGE
params['pi_voltage_lower'] = PI_VOLTAGE_LOWER
params['pi_voltage_upper'] = PI_VOLTAGE_UPPER
params['git_commit_hash'] = gitGetCommitHash()
#========================================================================================
# TEST NAME MAP
#========================================================================================

testNameMap = {
            "Electrical Current Test":'electricalCurrentTest',
            "Get Mac Address Test":'getMACTest',
            "Idle Mode Test":'idleModeTest',
            "LED Test 1":'LEDtest',
            "LED Test 2":'LEDtest',
            "LED Test 3":'LEDtest',
            "LED Test 4":'LEDtest',
            "LED Test 5":'LEDtest',
            "LED Test 6":'LEDtest',
            "LED Test 7":'LEDtest',
            "LED Test 8":'LEDtest',
            "LED Test 9":'LEDtest',
            "LED Test 10":'LEDtest',
            "LED Test 11":'LEDtest',
            "LED Test 12":'LEDtest',
            "Load Test":'loadTest',
            "BT DTM Test":'btDTMtest',
            "Accelerometer Self Test":'accelSelfTest',
            "Accelerometer Orientation Test":'accelOrientationTest',
            "Accelerometer Current Test":'accelCurrentTest',
            "Deep Sleep Test":'deepSleepTest',
            "Dummy Test":'dummyTest',
            "Duplicate Serial Number Test":'duplicateSerialNumTest',
            "Operating Current Test":'operatingCurrentTest',
            "Recent Sync Test":'recentSyncTest',
            "Battery Plot Test":'batteryPlotTest',
            "Get RSSI Test":'getRSSITest',
            "Write Serial Number Test":'writeSNTest',
            "Read Serial Number Test":'getSNTest',
            "Accelerometer BT Self Test":'accelBTSelfTest',
            "Battery BT Test":'batteryBTTest',
            "Reset via BT":'resetViaBTtest',
            "Accelerometer Streaming Test":'accelStreamingTest',
            "Vibe Test":'vibeTest',
            "Vibe Current Test":'vibeCurrentTest',
            "Audio Test":'audioTest',
            "Audio Current Test": 'audioCurrentTest',
            "Captouch Test":'captouchTest',
            "Captouch Programming": 'captouchProgramming',
            "Captouch Current Test": 'captouchCurrentTest',
            "Play Sound Test": 'playSoundTest',
            "LED Self Test": 'ledSelfTest',
            "Captouch BT Test": 'captouchBTTest',
            "Vibe BT Test": 'vibeBTTest',
            "Mag Self Test": 'magSelfTest',
            "LED BT Self Test": 'ledBTSelfTest',
            "Mag BT Self Test": 'magBTSelfTest',
            "Crystal Test": 'crystalTest',
            "Vibe BT Magnitude Test":'vibeBTMagnitudeTest',
            "Vibe BT Current Test": 'vibeBTCurrentTest',
            "Captouch BT Calibration": 'captouchBTCalibration',
            "DRV Part ID Test": 'drvPartIdTest',
            "RTC Part ID Test": 'rtcPartIdTest',
            "DRV Calibration": 'drvCalibration',
            "All Movements Clockwise Current Test": 'allMovementsCwCurrentTest',
            "All Movements Counter-Clockwise Current Test": 'allMovementsCcwCurrentTest',
            "Movement 1 Clockwise Current Test": 'movement1CwCurrentTest',
            "Movement 1 Counter-Clockwise Current Test": 'movement1CcwCurrentTest',
            "Movement 2 Clockwise Current Test": 'movement2CwCurrentTest',
            "Movement 2 Counter-Clockwise Current Test": 'movement2CcwCurrentTest',
            "Movement 3 Clockwise Current Test": 'movement3CwCurrentTest',
            "Movement 3 Counter-Clockwise Current Test": 'movement3CcwCurrentTest',
            "Boost Current Test": 'boostCurrentTest',
            "Pusher Push Test": 'pusherPushTest',
            "Pusher Release Test": 'pusherReleaseTest',
            "Pusher Dummy Test": 'dummyPusherPushTest',
            "Crystal Calibration Test": 'crystalCalibrationTest',
            "Hibernation Mode Test": 'hibernationModeTest',
            "Vibe Current Test 1":'vibeCurrentTest',
            "Vibe Current Test 2":'vibeCurrentTest',
            "Vibe Current Test 3":'vibeCurrentTest',
            "Vibe Current Test 4":'vibeCurrentTest',
            "Vibe Current Test 5":'vibeCurrentTest',
            "Vibe Current Test 6":'vibeCurrentTest',
            "Vibe Current Test 7":'vibeCurrentTest',
            "Vibe Current Test 8":'vibeCurrentTest',
            "Vibe Current Test 9":'vibeCurrentTest',
            "Vibe Current Test 10":'vibeCurrentTest',
            "Vibe Current Test 11":'vibeCurrentTest',
            "Vibe Current Test 12":'vibeCurrentTest',
            "Vibe BT Calibration": 'vibeBTCalibration',
            "Set Hand Positions": 'setHandPositions',
            "Set UTC Time": 'setUtcTime',
            "Vibe BT Calibration 200 200": 'vibeBTCalibration1',
            "Vibe BT Calibration 400 400": 'vibeBTCalibration2',
            "Vibe BT Calibration 600 600": 'vibeBTCalibration3',
            "Vibe BT Calibration 800 800": 'vibeBTCalibration4',
            "Vibe BT Calibration 1000 1000": 'vibeBTCalibration5',
            "Vibe BT Calibration 1200 1200": 'vibeBTCalibration6',
            "Vibe BT Calibration 1200 600": 'vibeBTCalibration7',
            "Vibe BT Calibration 900 600": 'vibeBTCalibration8',
            "Get Average RSSI Test":'getAverageRssiTest',
            "Packet Error Rate Test":'packetErrorRateTest',
            "Boost BT Test": 'boostBTTest'
            }


# Create list structure for creating lists of ATE tests
def createTestOrder(testList):
    testOrder = []
    testIndex = 0
    for testName in testList:
        test = {}
        testIndex +=1
        test['name'] = testName
        test['testFunction'] = testNameMap[testName]
        test['index'] = testIndex
        testOrder.append(test)
    return testOrder


def flattenList(inputList):
    return list(itertools.chain.from_iterable(itertools.repeat(x,1) if isinstance(x,str) else x for x in inputList))
