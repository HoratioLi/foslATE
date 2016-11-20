#!/usr/bin/env python
"""
Pluo Configuration File
Created: 2016 Jan 06
Author: James Quen

Description:
Configuration file for the Pluto project.
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
MINIOR = "7"                # Minior version
INTERNAL = "4"              # Internal version - used for development.
RELEASE_TYPE = "dev"        # Can be either prod or dev - prod indicates that it is used on the production floor.  dev indicates it's used for development.
STATION_SOFTWARE_VERSION = STATION + "." + PRODUCT + "." + MAJOR + "." + MINIOR + "." + INTERNAL + "." + RELEASE_TYPE

#===============================================================================
# DEVICE FIRMWARE VERSION
#===============================================================================
FW_VERSION="S21.0.22r.ship_mode"

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

MCU="Ambiq"

#===============================================================================
# SERIAL NUMBER SCHEME
#===============================================================================
ATE_ID = 'S2'              
SERIAL_NUM_PREFIX = 'S'  

if not MFG_DB_STAGING:
      MATCHSTR_INTERNAL_REGEX = '2.ZZ[^BOSI]{5}'        
      MATCHSTR_REGEX = '2.[^Z]Z[^BOSI]{5}'
else:
      MATCHSTR_INTERNAL_REGEX = '2.ZZ.{5}'        
      MATCHSTR_REGEX = '2.[^Z]Z.{5}'   

#========================================================================================
# TEST LIMITS
#========================================================================================
MCU_CURRENT_LOWER = 0.0011                # equals 1.1 milliamps
MCU_CURRENT_UPPER = 0.002                 # equals 2 milliamps
IDLE_CURRENT_LOWER  = 0.0000006            # equals 0.6 microamps
IDLE_CURRENT_UPPER  = 0.000007            # equals 7 microamps - raised to account for watchdog and 32khz clock
LED_CURRENT_LOWER  = 0.0015               # equals 1.5 milliamps - remove?
LED_CURRENT_UPPER  = 0.0067               # equals 6.7 milliamps - remove?
LOAD_CURRENT_LOWER  = 0.0020              # equals 2.0 milliamps - not implemented yet. remove?
LOAD_CURRENT_UPPER  = 0.0025              # equals 2.5 milliamps - not implemented yet. remove?
ACCEL_CURRENT_LOWER = 0.000010            # equals 10 microamps
ACCEL_CURRENT_UPPER = 0.000024            # equals 24 microamps
DEEP_SLEEP_CURRENT_LOWER  = 0.0000002     # equals 0.2 microamps - remove?
DEEP_SLEEP_CURRENT_UPPER  = 0.0000007     # equals 0.7 microamps - remove?
Z_DATA_THRESHOLD_LOWER = 500              # accelerometer reading
Z_DATA_THRESHOLD_UPPER = 700              # accelerometer reading
#TODO
RSSI_LOWER = -70                    # -70 dB - arbitrarily chose based on ATE 1 tests. TODO: need histogram study to get values
RSSI_UPPER = -30                    # -30 dB - Need to update test to use specific values for this
#TODO
RSSI_LOWER_ATE_2 = -60                    # -60 dB - visually chose value based on histogram of ~130 ATE 2 tests.
RSSI_UPPER_ATE_2 = -30                    # -30 dB
OPER_CURR_THRESH_LOWER = 0.000003         # equals 3 microamps - remove?
OPER_CURR_THRESH_UPPER = 0.000007         # equals 7 microamps - remove?
BATT_BASE_VOLTAGE_THRESH_LOWER = 2750     # equals 2750 mV - This voltage is used to screen for bad batteries.  Value needs to be revisited based on histogram after first 10k.
BATT_BASE_LOAD_VOLTAGE_DIFFERENCE = 100   # equals 100 mV - This is the limit used to determine the status of a battery. A difference of anything greater than 100 mV indicates a bad battery.
BATT_BASE_VOLTAGE_THRESH_UPPER = 3300     # equals 3300 mV - Will be used with new ship_mode FW - 
BATT_LOAD_VOLTAGE_THRESH_LOWER = 2900     # equals 2900 mV - Will be used with new ship_mode FW
BATT_LOAD_VOLTAGE_THRESH_UPPER = 3300     # equals 3300 mV - Will be used with new ship_mode FW   
SERIAL_BAUDRATE = 38400                   # the baudrate used for SWO communication
VIBE_CURRENT_LOWER = 0.003                # equals 3 milliamps
VIBE_CURRENT_UPPER = 0.004                # equals 4 milliamps
VIBE_VARIANCE_LOWER = 0                   # can possibly remove since magnitude is the important number
VIBE_VARIANCE_UPPER = 100                 # can possibly remove since magnitude is the important number
VIBE_MAGNITUDE_LOWER = 8                  # equals a magnitude of 8
VIBE_MAGNITUDE_UPPER = 11                 # equals a magnitude of 11
AUDIO_CURRENT_LOWER = 0.004               # equals 4 milliamps
AUDIO_CURRENT_UPPER = 0.005               # equals 5 milliamps
AUDIO_FREQUENCY_LOWER = 0
AUDIO_FREQUENCY_UPPER = 1000
AUDIO_MAGNITUDE_LOWER = 0
AUDIO_MAGNITUDE_UPPER = 200
CAPTOUCH_CURRENT_LOWER = 0.000005         # equals 5 microamps
CAPTOUCH_CURRENT_UPPER = 0.000016         # equals 16 microamps
POGO_MAX_RESISTANCE = 6                   # equals 6 ohms
CAPTOUCH_CAPACITANCE_LOWER = 19           # equals 19 pF
CAPTOUCH_CAPACITANCE_UPPER = 23           # equals 23 pF
LOW_LED_CURRENT_LOWER = 0.001             # equals 1 milliamps
LOW_LED_CURRENT_UPPER = 0.003             # equals 3 milliamps
HIGH_LED_CURRENT_LOWER = 0.015            # equals 15 milliamps
HIGH_LED_CURRENT_UPPER = 0.020            # equals 20 milliamps
HIBERNATION_CURRENT_LOWER  = 0.000002     # equals 2 microamps
HIBERNATION_CURRENT_UPPER  = 0.000004     # equals 4 microamps
BT_CAPTOUCH_CAPACITANCE_LOWER = 45        # equals 45 pF
BT_CAPTOUCH_CAPACITANCE_UPPER = 76        # equals 76 pF
BT_VIBE_FREQUENCY_LOWER = 230.0           # equals 230 hz
BT_VIBE_FREQUENCY_UPPER = 280.0           # equals 280 hz

CRYSTAL_DURATION_LOWER = 0.150            # equals 150 milliseconds
CRYSTAL_DURATION_UPPER = 0.250            # equals 250 milliseconds

CAPTOUCH_MOD_COMP_IDAC_LOWER = 22         # lower mod/comp idac value
CAPTOUCH_MOD_COMP_IDAC_UPPER = 40         # upper mod/comp idac value

NUM_LED_TESTS = 2

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
params['batt_base_load_voltage_difference_limit'] = BATT_BASE_LOAD_VOLTAGE_DIFFERENCE
params['batt_base_voltage_upper'] = BATT_BASE_VOLTAGE_THRESH_UPPER
params['batt_load_voltage_lower'] = BATT_LOAD_VOLTAGE_THRESH_LOWER
params['batt_load_voltage_upper'] = BATT_LOAD_VOLTAGE_THRESH_UPPER    
params['rssi_lower'] = RSSI_LOWER
params['rssi_upper'] = RSSI_UPPER
params['baud_rate'] = SERIAL_BAUDRATE 
params['vibe_current_lower'] = VIBE_CURRENT_LOWER
params['vibe_current_upper'] = VIBE_CURRENT_UPPER
params['vibe_variance_lower'] = VIBE_VARIANCE_LOWER
params['vibe_variance_upper'] = VIBE_VARIANCE_UPPER
params['vibe_magnitude_lower'] = VIBE_MAGNITUDE_LOWER
params['vibe_magnitude_upper'] = VIBE_MAGNITUDE_UPPER
params['audio_current_lower'] = AUDIO_CURRENT_LOWER
params['audio_current_upper'] = AUDIO_CURRENT_UPPER
params['audio_frequency_lower'] = AUDIO_FREQUENCY_LOWER
params['audio_frequency_upper'] = AUDIO_FREQUENCY_UPPER
params['audio_magnitude_lower'] = AUDIO_MAGNITUDE_LOWER
params['audio_magnitude_upper'] = AUDIO_MAGNITUDE_UPPER
params['captouch_current_lower'] = CAPTOUCH_CURRENT_LOWER
params['captouch_current_upper'] = CAPTOUCH_CURRENT_UPPER
params['pogoMaxResistance'] = POGO_MAX_RESISTANCE
params['captouch_capacitance_lower'] = CAPTOUCH_CAPACITANCE_LOWER
params['captouch_capacitance_upper'] = CAPTOUCH_CAPACITANCE_UPPER  
params['led_low_current_lower'] = LOW_LED_CURRENT_LOWER
params['led_low_current_upper'] = LOW_LED_CURRENT_UPPER  
params['led_high_current_lower'] = HIGH_LED_CURRENT_LOWER
params['led_high_current_upper'] = HIGH_LED_CURRENT_UPPER
params['hibernation_current_lower'] = HIBERNATION_CURRENT_LOWER
params['hibernation_current_upper'] = HIBERNATION_CURRENT_UPPER
params['captouch_bt_capacitance_lower'] = BT_CAPTOUCH_CAPACITANCE_LOWER
params['captouch_bt_capacitance_upper'] = BT_CAPTOUCH_CAPACITANCE_UPPER
params['vibe_bt_frequency_lower'] = BT_VIBE_FREQUENCY_LOWER
params['vibe_bt_frequency_upper'] = BT_VIBE_FREQUENCY_UPPER 
params['crystal_duration_lower'] = CRYSTAL_DURATION_LOWER
params['crystal_duration_upper'] = CRYSTAL_DURATION_UPPER  
params['captouch_mod_comp_idac_lower'] = CAPTOUCH_MOD_COMP_IDAC_LOWER
params['captouch_mod_comp_idac_upper'] = CAPTOUCH_MOD_COMP_IDAC_UPPER

#========================================================================================
# ATE 1 TESTS
#========================================================================================
if STATION_ID == 1:
      testList = [
            "Electrical Current Test",
            "Vibe Test",
            "Get Mac Address Test", 
            "Captouch Programming",
            "Captouch Test",
            "LED Self Test",
            "Mag Self Test",
            "Accelerometer Orientation Test",
            "Accelerometer Current Test",
            ledTestList,      
            "Crystal Test",           
            "Idle Mode Test",
            "Vibe Current Test",
            "Audio Test",
            "Audio Current Test",
            "Captouch Current Test",
      ]

      bleTestList = [
            "Get RSSI Test",
      ]

#========================================================================================
# ATE 2 TESTS
#========================================================================================
elif STATION_ID == 2:
      bleTestList = [
            "Get RSSI Test",
            "Captouch BT Test",
            "Battery BT Test",
            "Vibe BT Test",
            "Vibe BT Magnitude Test",
            "Mag BT Self Test",                 
            "Accelerometer BT Self Test",
            "LED BT Self Test"
      ]  

testList = flattenList(testList)
testOrder = createTestOrder(testList)

bleTestList = flattenList(bleTestList)
testOrderBLE = createTestOrder(bleTestList)