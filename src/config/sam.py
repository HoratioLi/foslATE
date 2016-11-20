#!/usr/bin/env python
"""
Pluo Configuration File
Created: 2016 Mar 3
Author: James Quen

Description:
Configuration file for the SAM project.
"""

from common import *

#===============================================================================
# STATION SOFTWARE VERSION
#===============================================================================
#Version scheme is defined as
#<station_type>.<product>.<major>.<minor>.<internal_rev>.<prod | dev>

STATION = "ATE"             # Can be either ATE or RMA
PRODUCT = DEVICE_TYPE       # The product type
MAJOR = "0"                 # Major version
MINIOR = "0"                # Minior version
INTERNAL = "43"              # Internal version - used for development.
RELEASE_TYPE = "dev"        # Can be either prod or dev - prod indicates that it is used on the production floor.  dev indicates it's used for development.
STATION_SOFTWARE_VERSION = STATION + "." + PRODUCT + "." + MAJOR + "." + MINIOR + "." + INTERNAL + "." + RELEASE_TYPE

#===============================================================================
# SUPPORTED DEVICE FIRMWARE VERSIONS
#===============================================================================
FW_VERSIONS=["HW0.0.0.5r.prod.v14", "HW0.0.0.5r.prod.v15"]

#===============================================================================
# MANUFACTURER INFORMATION
#===============================================================================
MANUFACTURER_NAME='Endor'
TEST_LOCATION='China'

#===============================================================================
# DEVICE PHYSICAL INFORMATION
#===============================================================================
MECHANICAL_REVISION="1.0"
PCB_REVISION=""                 
PCBA_REVISION=""                
DEVICE_COLOR=None                 
MODEL_NUMBER="SH2"                  
LED_COLOR="RGB"    

colorMapPluto = {
            'R':'ROSE GOLD',
            'G':'CARBON BLACK'
            }

subeyeLocations = {
      '1':'2', # 1.5 o'clock
      '3':'1', # 3 o'clock
      '4':'0', # 4.5 o'clock
      '6':'7', # 6 o'clock
      '7':'6', # 7.5 o'clock
      '9':'5', # 9 o'clock
      'A':'4', # 10.5 o'clock
      'C':'3'  # 12 o'clock
}

# Positions in Little Endian format.
POSTION00 = "\x00\x00" # 12 O'Clock
POSTION01 = "\x1E\x00" # 1 O'Clock
POSTION02 = "\x3C\x00" # 2 O'Clock
POSTION03 = "\x5A\x00" # 3 O'Clock
POSTION04 = "\x78\x00" # 4 O'Clock
POSTION05 = "\x96\x00" # 5 O'Clock
POSTION06 = "\xB4\x00" # 6 O'Clock
POSTION07 = "\xD2\x00" # 7 O'Clock
POSTION08 = "\xF0\x00" # 8 O'Clock
POSTION09 = "\x0E\x01" # 9 O'Clock
POSTION10 = "\x2C\x01" # 10 O'Clock
POSTION11 = "\x4A\x01" # 11 O'Clock

# Brand Shipping positions. The order is subeye, minute, and then hour hand.
handPositions = {
      'F0':POSTION00 + POSTION02 + POSTION10, #Fossil Men's Q Crewmaster
      'F1':POSTION00 + POSTION02 + POSTION10, #Fossil Men's Q Nate
      'F2':POSTION00 + POSTION02 + POSTION10, #Fossil Womens's Q Gazer
      'F3':POSTION00 + POSTION02 + POSTION10, #Fossil Womens's Q Taylor
      'C0':POSTION00 + POSTION02 + POSTION10, #Chaps Gent's 
      'C1':POSTION00 + POSTION02 + POSTION10, #Chaps Ladies's 
      'K0':POSTION00 + POSTION02 + POSTION10, #Kate Spade 
      'M0':POSTION00 + POSTION02 + POSTION10, #Michael Kors Gage
      'M1':POSTION00 + POSTION02 + POSTION10, #Michael Kors Runway
      'D0':POSTION00 + POSTION11 + POSTION05, #Diesel Sleeper
      'E0':POSTION06 + "\x30\x00" + POSTION10, #Emporio Armani Renato
      'S0':POSTION00 + POSTION00 + POSTION06, #Skagen Hagen
      'W0':POSTION00 + POSTION06 + POSTION00, #Misfit
      'L':'',
      'A':'',
      'Y':'',
      'R':''
}

MCU="Ambiq"

#===============================================================================
# SERIAL NUMBER SCHEME
#===============================================================================
ATE_ID = 'HW' # Hybrid Watch              
SERIAL_NUM_PREFIX = ''  

if not MFG_DB_STAGING:
      MATCHSTR_INTERNAL_REGEX = 'W0[0-9A-Z]{2}[134679AC][^BbOoSsIi]{5}'        
      MATCHSTR_REGEX = 'W0[FCKMDESLAYRWJTXZ][0-9A-Z]{3}[^BbOoSsIi]{4}'
else:
      MATCHSTR_INTERNAL_REGEX = '.{10}'        
      MATCHSTR_REGEX = '.{10}'   

SERIAL_NUMBER_LENGTH = 10
#========================================================================================
# TEST LIMITS / DEFINITIONS
#========================================================================================
# All limits have been determined by histogram data from EV 2.
MCU_CURRENT_LOWER = 0.0011                # equals 1.1 milliamps
MCU_CURRENT_UPPER = 0.002                 # equals 2 milliamps
ACCEL_CURRENT_LOWER = 0.000007            # equals 7 microamps
ACCEL_CURRENT_UPPER = 0.000015            # equals 15 microamps
Z_DATA_THRESHOLD_LOWER = 525              # accelerometer reading
Z_DATA_THRESHOLD_UPPER = 675              # accelerometer reading

RSSI_LOWER = -70                  # -75 dB - arbitrarily chose based on ATE 1 tests. TODO: need histogram study to get values
RSSI_UPPER = -30                  # -30 dB - Need to update test to use specific values for this

BATT_BASE_VOLTAGE_THRESH_LOWER = 2750     # equals 2750 mV - This voltage is used to screen for bad batteries.  Value needs to be revisited based on histogram after first 10k.
BATT_BASE_LOAD_VOLTAGE_DIFFERENCE = 120   # equals 120 mV - This is the limit used to determine the status of a battery. A difference of anything greater than 120 mV indicates a bad battery.
BATT_BASE_VOLTAGE_THRESH_UPPER = 3300     # equals 3300 mV - Will be used with new ship_mode FW
BATT_LOAD_VOLTAGE_THRESH_LOWER = 2750     # equals 2750 mV - Will be used with new ship_mode FW
BATT_LOAD_VOLTAGE_THRESH_UPPER = 3300     # equals 3300 mV - Will be used with new ship_mode FW   
SERIAL_BAUDRATE = 38400                   # the baudrate used for UART communication
VIBE_CURRENT_LOWER = 0.0275               # equals 27.5 milliamps.
VIBE_CURRENT_UPPER = 0.035                # equals 35 milliamps
VIBE_MAGNITUDE_LOWER = 8                  # equals a magnitude of 8
VIBE_MAGNITUDE_UPPER = 12                 # equals a magnitude of 12
HIBERNATION_CURRENT_LOWER  = 0.0000006    # equals 0.6 microamps (decreased to below hibernate value to remove failure)
HIBERNATION_CURRENT_UPPER  = 0.0000023    # equals 2.3 microamps

CRYSTAL_DURATION_LOWER = 0.150            # equals 150 milliseconds
CRYSTAL_DURATION_UPPER = 0.250            # equals 250 milliseconds

MOVEMENT_CURRENT_LOWER = 0.00185          # equals 1.85 milliamps
MOVEMENT_CURRENT_UPPER = 0.0025           # equals 2.5 milliamps

ALL_MOVEMENT_CURRENT_LOWER = 0.00255      # equals 2.55 milliamps
ALL_MOVEMENT_CURRENT_UPPER = 0.00375      # equals 3.75 milliamps

NUM_LED_TESTS = 0
BOOST_CURRENT_LOWER = 0.000009            # equals 9 microamps
BOOST_CURRENT_UPPER = 0.020000            # equals 20 milliamps (upper limit no longer a fail condition)

NUM_VIBE_CURRENT_TESTS = 0

VIBE_OVERVOLTAGE              = 1000            # 1200 mV. Used in DRV vibe calibration
VIBE_RATEDVOLTAGE             = 1000            # 1200 mV. Used in DRV vibe calibration

ACTIVATE_BLE = True
# Command, Rated Voltage, Overdrive Voltage
VIBE_CAL = ""
VIBE_CAL_200_200 = "\x01\xF2\x09\x08\x09"     # 200mV 200mV
VIBE_CAL_400_400 = "\x01\xF2\x09\x10\x13"     # 400mV 400mV
VIBE_CAL_600_600 = "\x01\xF2\x09\x17\x1C"     # 600mV 600mV
VIBE_CAL_800_800 = "\x01\xF2\x09\x1F\x26"     # 800mV 800mV
VIBE_CAL_1000_1000 = "\x01\xF2\x09\x27\x2F"     # 1000mV 1000mV
VIBE_CAL_1200_1200 = "\x01\xF2\x09\x2F\x39"           # 1200mv 1200mv
VIBE_CAL_1200_600= "\x01\xF2\x09\x2F\x1C"     # 1200mv 600mv
VIBE_CAL_900_600= "\x01\xF2\x09\x23\x1C"     # 900mv 600mv

OVERDRIVE_1200 = "\x2F"
OVERDRIVE_1000 = "\x27"
OVERDRIVE_800 = "\x1F"
OVERDRIVE_600 = "\x17"
OVERDRIVE_400 = "\x10"
OVERDRIVE_200 = "\x08"

RATED_1200 = "\x39"
RATED_1000 = "\x2F"
RATED_800 = "\x26"
RATED_600 = "\x1C"
RATED_400 = "\x13"
RATED_200 = "\x09"


STREAMED_X_DATA_LOWER=-75                 # Streamed x data lower
STREAMED_X_DATA_UPPER=75                  # Streamed x data upper
STREAMED_Y_DATA_LOWER=-75                 # Streamed y data lower
STREAMED_Y_DATA_UPPER=75                  # Streamed y data upper
STREAMED_Z_DATA_LOWER=400                 # Streamed z data lower
STREAMED_Z_DATA_UPPER=700                 # Streamed z data upper

ACCEL_STREAMED_DATA_LOWER=[STREAMED_X_DATA_LOWER, STREAMED_Y_DATA_LOWER, STREAMED_Z_DATA_LOWER]
ACCEL_STREAMED_DATA_UPPER=[STREAMED_X_DATA_UPPER, STREAMED_Y_DATA_UPPER, STREAMED_Z_DATA_UPPER]

PER_PACKET_COUNT = 200
PER_SUCCESS_PERCENTAGE=90                 # The success rate for passing the PER test.
TIME_DIFFERENCE_MAX=5                     # The maximum time difference between current time and device time to determine if time has be set on device.

NUM_READINGS_BASELINE = 100     # How many readings to take for purpose of estimating baseline (for operating current test)
BASELINE_WINDOW_SIZE = 4        # Sliding window size for estimating baseline

BOOST_OVERVOLTAGE = 1200        # Vibe calibration settings required to allow boost test to work
BOOST_RATEDVOLTAGE = 1200

BOOST_VOLTAGE_LOWER = 3000          # 3.0 Volts
BOOST_VOLTAGE_UPPER = 3200          # 3.2 Volts

ledTestList = []
for ledIndex in range(1, NUM_LED_TESTS+1):
      ledTestList.append("LED Test %s" % ledIndex)

vibeCurrentTestList = []
for vibeCurrentTestIndex in range (1, NUM_VIBE_CURRENT_TESTS + 1):
      vibeCurrentTestList.append("Vibe Current Test %s" % vibeCurrentTestIndex)

testList = []
bleTestList = []

#========================================================================================
# ATE 1 TESTS
#========================================================================================
if STATION_ID == 1:
      SMT_SN_REQUIRED = False
      INTERNAL_SN_REQUIRED = True
      PACKAGING_SN_REQUIRED = False

      PROGRAM_DEVICE = True               # Program the device

      PROGRAM_SERIAL_NUMBER = False

      RSSI_AVERAGE_LOWER = -60                    # -60 dB - Based on histogramm data of EV2
      RSSI_AVERAGE_UPPER = -30                    # -30 dB - Based on histogramm data of EV2

      testList = [
            "Electrical Current Test",
            "Get Mac Address Test",
            "DRV Part ID Test",
            "Accelerometer Orientation Test",
            "Accelerometer Current Test",
            "Crystal Calibration Test",
            "Boost Current Test",
            "Crystal Test",
            "All Movements Counter-Clockwise Current Test",
            "All Movements Clockwise Current Test",
            "Movement 1 Counter-Clockwise Current Test",
            "Movement 1 Clockwise Current Test",
            "Movement 2 Counter-Clockwise Current Test",
            "Movement 2 Clockwise Current Test",
            "Movement 3 Counter-Clockwise Current Test",
            "Movement 3 Clockwise Current Test",
            "Hibernation Mode Test",
      ]

      bleTestList = [
            "Get Average RSSI Test",
      ]

#========================================================================================
# ATE 2 TESTS
#========================================================================================
elif STATION_ID == 2:
      SMT_SN_REQUIRED = False
      INTERNAL_SN_REQUIRED = True
      PACKAGING_SN_REQUIRED = False

      PROGRAM_DEVICE = False              # Program the device

      PROGRAM_SERIAL_NUMBER = False

      RSSI_AVERAGE_LOWER = -70                    # -60 dB - Based on histogramm data of EV2
      RSSI_AVERAGE_UPPER = -30                    # -30 dB - Based on histogramm data of EV2

      testList = [
            "Electrical Current Test",
            "Get Mac Address Test",
            "DRV Part ID Test",
            "Accelerometer Orientation Test",
            "Accelerometer Current Test",
            "Crystal Calibration Test",
            "Boost Current Test",
            "Crystal Test",
            "All Movements Counter-Clockwise Current Test",
            "All Movements Clockwise Current Test",
            "Movement 1 Counter-Clockwise Current Test",
            "Movement 1 Clockwise Current Test",
            "Movement 2 Counter-Clockwise Current Test",
            "Movement 2 Clockwise Current Test",
            "Movement 3 Counter-Clockwise Current Test",
            "Movement 3 Clockwise Current Test",
            "Hibernation Mode Test",
            "Vibe Current Test",
            "Vibe Test",
            "Pusher Push Test",
      ]

      bleTestList = [
            "Get Average RSSI Test",
      ]

#========================================================================================
# ATE 3 TESTS
#========================================================================================
elif STATION_ID == 3:
      SMT_SN_REQUIRED = False
      INTERNAL_SN_REQUIRED = True
      PACKAGING_SN_REQUIRED = True

      PROGRAM_DEVICE = False              # Program the device
      ACTIVATE_BLE = False                # DUT is not physically connected to ATE. Activating BLE advertising must be manual.
      PROGRAM_SERIAL_NUMBER = True

      RSSI_AVERAGE_LOWER = -70                    # -60 dB - Based on histogramm data of EV2
      RSSI_AVERAGE_UPPER = -30                    # -30 dB - Based on histogramm data of EV2

      bleTestList = [
            "Battery BT Test",
            "Boost BT Test",
            "Get Average RSSI Test",
            "Packet Error Rate Test",
            "Vibe BT Calibration",
            "Vibe BT Magnitude Test",
            "Accelerometer Streaming Test",
            "Set Hand Positions",
            "Set UTC Time"
      ]

#========================================================================================
# PARAMETER SETUP
#========================================================================================
if STATION_ID == 1:
      params['programming_done'] = False
params['mcu_current_lower'] = MCU_CURRENT_LOWER
params['mcu_current_upper'] = MCU_CURRENT_UPPER
params['accel_current_lower'] = ACCEL_CURRENT_LOWER
params['accel_current_upper'] = ACCEL_CURRENT_UPPER  
params['z_data_threshold_lower'] = Z_DATA_THRESHOLD_LOWER
params['z_data_threshold_upper'] = Z_DATA_THRESHOLD_UPPER 
params['batt_base_voltage_lower'] = BATT_BASE_VOLTAGE_THRESH_LOWER
params['batt_base_load_voltage_difference_limit'] = BATT_BASE_LOAD_VOLTAGE_DIFFERENCE
params['batt_base_voltage_upper'] = BATT_BASE_VOLTAGE_THRESH_UPPER
params['batt_load_voltage_lower'] = BATT_LOAD_VOLTAGE_THRESH_LOWER
params['batt_load_voltage_upper'] = BATT_LOAD_VOLTAGE_THRESH_UPPER    
params['rssi_lower'] = RSSI_LOWER
params['rssi_upper'] = RSSI_UPPER
params['rssi_average_lower'] = RSSI_AVERAGE_LOWER
params['rssi_average_upper'] = RSSI_AVERAGE_UPPER
params['baud_rate'] = SERIAL_BAUDRATE 
params['vibe_current_lower'] = VIBE_CURRENT_LOWER
params['vibe_current_upper'] = VIBE_CURRENT_UPPER
params['vibe_magnitude_lower'] = VIBE_MAGNITUDE_LOWER
params['vibe_magnitude_upper'] = VIBE_MAGNITUDE_UPPER
params['hibernation_current_lower'] = HIBERNATION_CURRENT_LOWER
params['hibernation_current_upper'] = HIBERNATION_CURRENT_UPPER
params['crystal_duration_lower'] = CRYSTAL_DURATION_LOWER
params['crystal_duration_upper'] = CRYSTAL_DURATION_UPPER  
params['movement_current_lower'] = MOVEMENT_CURRENT_LOWER
params['movement_current_upper'] = MOVEMENT_CURRENT_UPPER
params['all_movement_current_lower'] = ALL_MOVEMENT_CURRENT_LOWER
params['all_movement_current_upper'] = ALL_MOVEMENT_CURRENT_UPPER
params['boost_current_lower'] = BOOST_CURRENT_LOWER
params['boost_current_upper'] = BOOST_CURRENT_UPPER
params['vibe_overvoltage'] = VIBE_OVERVOLTAGE
params['vibe_ratedvoltage'] = VIBE_RATEDVOLTAGE

params['accel_streamed_data_lower'] = ACCEL_STREAMED_DATA_LOWER
params['accel_streamed_data_upper'] = ACCEL_STREAMED_DATA_UPPER

params['per_success_percentage'] = PER_SUCCESS_PERCENTAGE
params['per_packet_count'] = PER_PACKET_COUNT

params['time_difference_max'] = TIME_DIFFERENCE_MAX

params['boost_overvoltage'] = BOOST_OVERVOLTAGE
params['boost_ratedvoltage'] = BOOST_RATEDVOLTAGE
params['boost_voltage_lower'] = BOOST_VOLTAGE_LOWER
params['boost_voltage_upper'] = BOOST_VOLTAGE_UPPER

#========================================================================================
#========================================================================================

testList = flattenList(testList)
testOrder = createTestOrder(testList)

bleTestList = flattenList(bleTestList)
testOrderBLE = createTestOrder(bleTestList)

#========================================================================================
# BLE COMMANDS
#========================================================================================
#Get Commands
BT_GET_ACCEL_PART_ID = "\x01\xF2\x01"
BT_GET_BATTERY_VOLTAGE = "\x01\xF2\x02"
BT_GET_VIBE_MAGNITUDE = "\x01\xF2\x07"
BT_GET_VIBE_CAL_VALUES = "\x01\xF2\x09"
BT_GET_AVG_RSSI = "\x01\xF2\x0F"
BT_GET_PER_TOTAL_PACKETS = "\x01\xF2\x10"
BT_GET_PER_TOTAL_ERRORS = "\x01\xF2\x11"
BT_GET_HAND_POSITIONS = "\x01\xF2\x12"
BT_GET_SHIP_POSITIONS = "\x01\xF2\x14"
BT_GET_BOOST_VOLTAGE = "\x01\xF2\x15"

#Set Commands
BT_SET_VIBE_CAL = "\x02\xF2\x09"
BT_SET_SHIP_POSITION = "\x02\xF2\x14"
