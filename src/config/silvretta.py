#!/usr/bin/env python
"""
Silvretta Configuration File
Created: 2015 Nov 10
Author: James Quen

Description:
Configuration file for the Silvretta project.
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
MINIOR = "3"                # Minior version
INTERNAL = "0"              # Internal version - used for development.
RELEASE_TYPE = "prod"        # Can be either prod or dev - prod indicates that it is used on the production floor.  dev indicates it's used for development.
STATION_SOFTWARE_VERSION = STATION + "." + PRODUCT + "." + MAJOR + "." + MINIOR + "." + INTERNAL + "." + RELEASE_TYPE

#===============================================================================
# DEVICE FIRMWARE VERSION
#===============================================================================
FW_VERSION="C11.0.27r.prod"

#===============================================================================
# MANUFACTURER INFORMATION
#===============================================================================
MANUFACTURER_NAME='VS'
TEST_LOCATION='Korea'

#===============================================================================
# DEVICE PHYSICAL INFORMATION
#===============================================================================
MECHANICAL_REVISION="1.0"
PCB_REVISION=""                 
PCBA_REVISION=""                
DEVICE_COLOR=None                 
MODEL_NUMBER="IWC-C1"                  
LED_COLOR="WHITE"    

colorMapSilvretta={'Z':'NO COLOR'}

MCU="Ambiq"

#===============================================================================
# SERIAL NUMBER SCHEME
#===============================================================================
ATE_ID='C1'              
SERIAL_NUM_PREFIX='C' 

if not MFG_DB_STAGING:        
      MATCHSTR_INTERNAL_REGEX='1.ZZ[^BOSI]{5}'        
      MATCHSTR_REGEX='1.ZZ[^BOSI]{5}'
else:
      MATCHSTR_INTERNAL_REGEX='1.ZZ.{5}'     
      MATCHSTR_REGEX='1.ZZ.{5}'

#========================================================================================
# TEST LIMITS
#========================================================================================
MCU_CURRENT_LOWER = 0.0011                # equals 1.1 milliamps
MCU_CURRENT_UPPER = 0.002                 # equals 2 milliamps
IDLE_CURRENT_LOWER  = 0.0000006           # equals 0.6 microamps
IDLE_CURRENT_UPPER  = 0.000003            # equals 3 microamps
LED_CURRENT_LOWER  = 0.002                # equals 2 milliamps
LED_CURRENT_UPPER  = 0.003                # equals 3 milliamps
ACCEL_CURRENT_LOWER = 0.000010            # equals 10 microamps
ACCEL_CURRENT_UPPER = 0.000024            # equals 24 microamps
Z_DATA_THRESHOLD_LOWER = 500              # accelerometer reading
Z_DATA_THRESHOLD_UPPER = 700              # accelerometer reading
RSSI_LOWER = -70                          # -70 dB - arbitrarily chose based on ATE 1 tests. TODO: need histogram study to get values
RSSI_UPPER = -30                          # -30 dB - Need to update test to use specific values for this
OPER_CURR_THRESH_LOWER = 0.000007         # equals 7 microamps
OPER_CURR_THRESH_UPPER = 0.000011         # equals 11 microamps 
SERIAL_BAUDRATE = 38400                   # the baudrate used for SWO communication
CRYSTAL_DURATION_LOWER = 0.150            # equals 150 milliseconds
CRYSTAL_DURATION_UPPER = 0.250            # equals 250 milliseconds
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
params['crystal_duration_lower'] = CRYSTAL_DURATION_LOWER
params['crystal_duration_upper'] = CRYSTAL_DURATION_UPPER  

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
            "Idle Mode Test"
      ]

      bleTestList = [
            "Get RSSI Test",
            "Write Serial Number Test",
            "Read Serial Number Test"
      ]

#========================================================================================
# ATE 2 TESTS
#========================================================================================
elif STATION_ID == 2:
      testList = [
            "Operating Current Test"
      ]
      
      bleTestList = [
            "Get RSSI Test",
            "Read Serial Number Test",            
            "Accelerometer BT Self Test",         
            "Reset via BT",               
      ]      

testList = flattenList(testList)
testOrder = createTestOrder(testList)

bleTestList = flattenList(bleTestList)
testOrderBLE = createTestOrder(bleTestList)