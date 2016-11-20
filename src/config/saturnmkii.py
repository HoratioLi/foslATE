#!/usr/bin/env python
"""
SaturnMKII Configuration File
Created: 2016 Jan 08
Author: James Quen

Description:
Configuration file for the SaturnMKII project.
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
MINIOR = "0"                # Minior version
INTERNAL = "0"              # Internal version - used for development.
RELEASE_TYPE = "dev"        # Can be either prod or dev - prod indicates that it is used on the production floor.  dev indicates it's used for development.
STATION_SOFTWARE_VERSION = STATION + "." + PRODUCT + "." + MAJOR + "." + MINIOR + "." + INTERNAL + "." + RELEASE_TYPE

#===============================================================================
# DEVICE FIRMWARE VERSION
#===============================================================================
FW_VERSION="SV0.1.5r.prod"

#===============================================================================
# MANUFACTURER INFORMATION
#===============================================================================
MANUFACTURER_NAME='VS'
TEST_LOCATION='Korea'

#===============================================================================
# DEVICE PHYSICAL INFORMATION
#===============================================================================
MECHANICAL_REVISION = "1.0"
PCB_REVISION = ""                   # *** TODO: fill this in ****
PCBA_REVISION = ""                  # *** TODO: fill this in ****
DEVICE_COLOR = None                 # Needs to come from packaging serial number
MODEL_NUMBER = "SH0AZB"                  
LED_COLOR = "WHITE"  

colorMapApollo = {
            'A':'SILVER', 
            'B':'JET', 
            'C':'GREEN',
            'D':'PINK',
            'E':'PURE',
            'F':'COCA-COLA', 
            'G':'TOPAZ', 
            'H':'CHAMPAGNE', 
            'J':'STORM',
            'K':'CORAL',
            'M':'WINE',
            'L':'SEA GLASS',
            }

MCU="nRF51822"

#===============================================================================
# SERIAL NUMBER SCHEME
#===============================================================================
ATE_ID = 'SV'              
SERIAL_NUM_PREFIX = 'S' 

if not MFG_DB_STAGING:        
      MATCHSTR_INTERNAL_REGEX = 'V.ZZ[^BOSI]{5}'        
      MATCHSTR_REGEX = 'V.[^Z]Z[^BOSI]{5}'
else:
      MATCHSTR_INTERNAL_REGEX = 'V.ZZ.{5}'     
      MATCHSTR_REGEX = 'V.[^Z]Z.{5}' 

#========================================================================================
# TEST LIMITS
#========================================================================================
MCU_CURRENT_LOWER = 0.0028          # equals 2.8 milliamps
MCU_CURRENT_UPPER = 0.0035          # equals 3.5 milliamps
IDLE_CURRENT_LOWER  = 0.000003      # equals 3 microamps
IDLE_CURRENT_UPPER  = 0.000006      # equals 6 microamps - raised to account for watchdog and 32khz clock
LED_CURRENT_LOWER  = 0.0045         # equals 4.5 milliamps
LED_CURRENT_UPPER  = 0.0067         # equals 6.7 milliamps
LOAD_CURRENT_LOWER  = 0.0020        # equals 2.0 milliamps
LOAD_CURRENT_UPPER  = 0.0025        # equals 2.5 milliamps
ACCEL_CURRENT_LOWER = 0.000003      # equals 3 microamps
ACCEL_CURRENT_UPPER = 0.000010      # equals 10 microamps
DEEP_SLEEP_CURRENT_LOWER  = 0.0000002     # equals 0.2 microamps
DEEP_SLEEP_CURRENT_UPPER  = 0.0000007     # equals 0.7 microamps
Z_DATA_THRESHOLD_LOWER = 435        # accelerometer reading
Z_DATA_THRESHOLD_UPPER = 600        # accelerometer reading
RSSI_LOWER = -75
RSSI_UPPER = -30
OPER_CURR_THRESH_LOWER = 0.000003     # equals 3 microamps
OPER_CURR_THRESH_UPPER = 0.000007     # equals 7 microamps
BATT_BASE_VOLTAGE_THRESH_LOWER = 3000     # equals 3000 mV
BATT_BASE_VOLTAGE_THRESH_UPPER = 3300     # equals 3300 mV
BATT_LOAD_VOLTAGE_THRESH_LOWER = 2900     # equals 2900 mV
BATT_LOAD_VOLTAGE_THRESH_UPPER = 3300     # equals 3300 mV    
SERIAL_BAUDRATE = 38400
NUM_LED_TESTS = 6 

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
params['load_current_lower'] = LOAD_CURRENT_LOWER
params['load_current_upper'] = LOAD_CURRENT_UPPER  
params['accel_current_lower'] = ACCEL_CURRENT_LOWER
params['accel_current_upper'] = ACCEL_CURRENT_UPPER  
params['deep_sleep_current_lower'] = DEEP_SLEEP_CURRENT_LOWER
params['deep_sleep_current_upper'] = DEEP_SLEEP_CURRENT_UPPER 
params['z_data_threshold_lower'] = Z_DATA_THRESHOLD_LOWER
params['z_data_threshold_upper'] = Z_DATA_THRESHOLD_UPPER   
params['oper_curr_thresh_upper'] = OPER_CURR_THRESH_UPPER
params['oper_curr_thresh_lower'] = OPER_CURR_THRESH_LOWER
params['batt_base_voltage_lower'] = BATT_BASE_VOLTAGE_THRESH_LOWER
params['batt_base_voltage_upper'] = BATT_BASE_VOLTAGE_THRESH_UPPER
params['batt_load_voltage_lower'] = BATT_LOAD_VOLTAGE_THRESH_LOWER
params['batt_load_voltage_upper'] = BATT_LOAD_VOLTAGE_THRESH_UPPER    
params['rssi_lower'] = RSSI_LOWER
params['rssi_upper'] = RSSI_UPPER
params['baud_rate'] = SERIAL_BAUDRATE 

#========================================================================================
# ATE 1 TESTS
#========================================================================================
if STATION_ID == 1:
      testList = [
            "Electrical Current Test",
            "Get Mac Address Test",                   
            "Idle Mode Test",
            ledTestList,
            "Load Test",
            "BT DTM Test",
            "Dummy Test",
            "Accelerometer Orientation Test",
            "Accelerometer Current Test",
      ]
         
      bleTestList = [
            "Get RSSI Test",
      ]

#========================================================================================
# ATE 2 TESTS
#========================================================================================
elif STATION_ID == 2:
      testList = [
            "Operating Current Test",
      ]                 

      bleTestList = [
            "Get RSSI Test",
            "Accelerometer BT Self Test",
      ]

#========================================================================================
# ATE 3 TESTS
#========================================================================================
elif STATION_ID == 3:
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