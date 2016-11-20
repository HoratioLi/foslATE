#!/usr/bin/env python
"""
BMW Configuration File
Created: 2015 Nov 19
Author: James Quen

Description:
Configuration file for the BMW project.
"""

from common import *

#===============================================================================
# STATION SOFTWARE VERSION
#===============================================================================
#Version scheme is defined as
#<station_type>.<product>.<major>.<minor>.<internal_rev>.<prod | dev>

STATION = "ATE"             # Can be either ATE or RMA
PRODUCT = DEVICE_TYPE       # The product type
MAJOR = "1"                 # Major version
MINIOR = "9"                # Minior version
INTERNAL = "0"              # Internal version - used for development.
RELEASE_TYPE = "prod"        # Can be either prod or dev - prod indicates that it is used on the production floor.  dev indicates it's used for development.
STATION_SOFTWARE_VERSION = STATION + "." + PRODUCT + "." + MAJOR + "." + MINIOR + "." + INTERNAL + "." + RELEASE_TYPE

#===============================================================================
# DEVICE FIRMWARE VERSION
#===============================================================================
FW_VERSION="B00.0.37r.prod"

#===============================================================================
# MANUFACTURER INFORMATION
#===============================================================================
MANUFACTURER_NAME='GT'
TEST_LOCATION='China'

#===============================================================================
# DEVICE PHYSICAL INFORMATION
#===============================================================================
MECHANICAL_REVISION = "1.0"
PCB_REVISION = ""                   # *** TODO: fill this in ****
PCBA_REVISION = ""                  # *** TODO: fill this in ****
DEVICE_COLOR = None                 # Needs to come from packaging serial number
MODEL_NUMBER = "BM0"                  
LED_COLOR = "RGB"

colorMapBMW={
            'R':'ROSE GOLD',
            'G':'CARBON BLACK'
            }

MCU="Ambiq"

#===============================================================================
# SERIAL NUMBER SCHEME
#===============================================================================
ATE_ID = 'B0'              
SERIAL_NUM_PREFIX = 'B' 

if not MFG_DB_STAGING:
      MATCHSTR_INTERNAL_REGEX = '0.ZZ[^BOSI]{5}'        
      MATCHSTR_REGEX = '0.[^Z]Z[^BOSI]{5}'
else:
      MATCHSTR_INTERNAL_REGEX = '0.ZZ.{5}'        
      MATCHSTR_REGEX = '0.[^Z]Z.{5}' 

#========================================================================================
# TEST LIMITS
#========================================================================================
MCU_CURRENT_LOWER = 0.0011                # equals 1.1 milliamps
MCU_CURRENT_UPPER = 0.002                 # equals 2 milliamps
IDLE_CURRENT_LOWER  = 0.0000006           # equals 0.6 microamps
IDLE_CURRENT_UPPER  = 0.000003            # equals 7 microamps
LED_CURRENT_LOWER  = 0.006                # equals 6 milliamps
LED_CURRENT_UPPER  = 0.015                # equals 15 milliamps
ACCEL_CURRENT_LOWER = 0.000009            # equals 9 microamps
ACCEL_CURRENT_UPPER = 0.000014            # equals 14 microamps
Z_DATA_THRESHOLD_LOWER = -600             # accelerometer reading
Z_DATA_THRESHOLD_UPPER = -300             # accelerometer reading
RSSI_LOWER = -70                          # -70 dB - arbitrarily chose based on ATE 1 tests. TODO: need histogram study to get values
RSSI_UPPER = -30                          # -30 dB - Need to update test to use specific values for this
OPER_CURR_THRESH_LOWER = 0.000005         # equals 5 microamps - remove?
OPER_CURR_THRESH_UPPER = 0.000015         # equals 15 microamps - remove?
 
SERIAL_BAUDRATE = 38400                   # the baudrate used for SWO communication
VIBE_CURRENT_LOWER = 0.0005                # equals 0.5 milliamps
VIBE_CURRENT_UPPER = 0.0015                # equals 1.5 milliamps
VIBE_VARIANCE_LOWER = 0                   # can possibly remove since magnitude is the important number
VIBE_VARIANCE_UPPER = 100                 # can possibly remove since magnitude is the important number
VIBE_MAGNITUDE_LOWER = 8                  # equals a magnitude of 8
VIBE_MAGNITUDE_UPPER = 11                 # equals a magnitude of 11
BT_VIBE_FREQUENCY_LOWER = 230.0           # equals 230 hz
BT_VIBE_FREQUENCY_UPPER = 280.0           # equals 280 hz
CRYSTAL_DURATION_LOWER = 0.150            # equals 150 milliseconds
CRYSTAL_DURATION_UPPER = 0.250            # equals 250 milliseconds

STREAMED_X_DATA_LOWER=-230                 # Streamed x data lower
STREAMED_X_DATA_UPPER=230                  # Streamed x data upper
STREAMED_Y_DATA_LOWER=-75                 # Streamed y data lower
STREAMED_Y_DATA_UPPER=75                  # Streamed y data upper
STREAMED_Z_DATA_LOWER=400                 # Streamed z data lower
STREAMED_Z_DATA_UPPER=700                 # Streamed z data upper

ACCEL_STREAMED_DATA_LOWER=[STREAMED_X_DATA_LOWER, STREAMED_Y_DATA_LOWER, STREAMED_Z_DATA_LOWER]
ACCEL_STREAMED_DATA_UPPER=[STREAMED_X_DATA_UPPER, STREAMED_Y_DATA_UPPER, STREAMED_Z_DATA_UPPER]
NUM_LED_TESTS = 1 

#========================================================================================
# PARAMETER SETUP
#========================================================================================
NUM_READINGS_BASELINE = 100     # How many readings to take for purpose of estimating baseline (for operating current test)
BASELINE_WINDOW_SIZE = 4        # Sliding window size for estimating baseline

ledTestList = []
for ledIndex in range(1, NUM_LED_TESTS+1):
      ledTestList.append("LED Test %s" % ledIndex)

testList = []
bleTestList = []

PROGRAM_DEVICE = True

if STATION_ID == 1:
      params['programming_done'] = False
params['num_readings_baseline'] = NUM_READINGS_BASELINE
params['baseline_window_size'] = BASELINE_WINDOW_SIZE
params['mcu_current_lower'] = MCU_CURRENT_LOWER
params['mcu_current_upper'] = MCU_CURRENT_UPPER
params['idle_current_lower'] = IDLE_CURRENT_LOWER
params['idle_current_upper'] = IDLE_CURRENT_UPPER  
params['led_current_lower'] = LED_CURRENT_LOWER
params['led_current_upper'] = LED_CURRENT_UPPER
params['accel_current_lower'] = ACCEL_CURRENT_LOWER
params['accel_current_upper'] = ACCEL_CURRENT_UPPER  
params['z_data_threshold_lower'] = Z_DATA_THRESHOLD_LOWER
params['z_data_threshold_upper'] = Z_DATA_THRESHOLD_UPPER   
params['oper_curr_thresh_upper'] = OPER_CURR_THRESH_UPPER
params['oper_curr_thresh_lower'] = OPER_CURR_THRESH_LOWER 
params['rssi_lower'] = RSSI_LOWER
params['rssi_upper'] = RSSI_UPPER
params['baud_rate'] = SERIAL_BAUDRATE 
params['vibe_current_lower'] = VIBE_CURRENT_LOWER
params['vibe_current_upper'] = VIBE_CURRENT_UPPER
params['vibe_variance_lower'] = VIBE_VARIANCE_LOWER
params['vibe_variance_upper'] = VIBE_VARIANCE_UPPER
params['vibe_magnitude_lower'] = VIBE_MAGNITUDE_LOWER
params['vibe_magnitude_upper'] = VIBE_MAGNITUDE_UPPER
params['vibe_bt_frequency_lower'] = BT_VIBE_FREQUENCY_LOWER
params['vibe_bt_frequency_upper'] = BT_VIBE_FREQUENCY_UPPER 
params['crystal_duration_lower'] = CRYSTAL_DURATION_LOWER
params['crystal_duration_upper'] = CRYSTAL_DURATION_UPPER  
params['accel_streamed_data_lower'] = ACCEL_STREAMED_DATA_LOWER
params['accel_streamed_data_upper'] = ACCEL_STREAMED_DATA_UPPER

#========================================================================================
# ATE 1 TESTS
#========================================================================================
if STATION_ID == 1:
      testList = [
            "Electrical Current Test",
            "Get Mac Address Test", 
            "Crystal Test",
            "Accelerometer Orientation Test",
            "Accelerometer Current Test",
            ledTestList,            
            "Idle Mode Test",
      ]

      bleTestList = [
            "Get RSSI Test",
      ]

#========================================================================================
# ATE 1.5 TESTS
#========================================================================================
if STATION_ID == 1.5:
      bleTestList = [
            "Get RSSI Test",         
            "Accelerometer BT Self Test", 
            "Accelerometer Streaming Test",
            "Vibe BT Current Test",
            "Vibe BT Magnitude Test"
      ]
#========================================================================================
# ATE 2 TESTS
#========================================================================================
elif STATION_ID == 2:
      bleTestList = [
            "Get RSSI Test",    
            "Accelerometer BT Self Test",
            "Vibe BT Test", 
            #"Vibe BT Current Test",
            "Vibe BT Magnitude Test"            
            ]      

testList = flattenList(testList)
testOrder = createTestOrder(testList)

bleTestList = flattenList(bleTestList)
testOrderBLE = createTestOrder(bleTestList)