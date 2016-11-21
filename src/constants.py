#!/usr/bin/env python
'''
Created on 2013-06-11

@author: Trung Huynh, Rachel Kalmar
'''

import os, sys

#===============================================================================
# GUI PARAMETERS
#===============================================================================

# Define status label colors
INITIATED_COLOR = 'gray'
STATUS_IN_PROGRESS_COLOR = 'yellow'
STATUS_OK_COLOR = 'green'
STATUS_ERROR_COLOR = 'red'

#===============================================================================
# FILE PATHS
#===============================================================================

PATH_TO_LOGS = '/home/pi/misfit/Production/src/'
STATUS_FILE = '/home/pi/misfit/Production/src/prev_test_data/status.txt'
BATTERY_PASSED_FILE = '/home/pi/misfit/Production/src/prev_test_data/battery_passed.txt'
JSON_FILE = '/home/pi/misfit/Production/src/prev_test_data/test_json'
IMAGE_FILE_PATH = '/home/pi/misfit/Production/src/view/images/batteryPlot.png'

DELIMITER = '_'

#===============================================================================
# OTHER
#===============================================================================

# True if the code is being run on a Raspberry Pi
IS_RUNNING_ON_PI = os.path.isdir("/home/pi")

#===============================================================================
# ************
# OVERWRITE CONSTANTS WITH THOSE CONTAINED IN "local_constants.py"
# ************
#===============================================================================

from ate_settings import *
from local_constants import *

#print "STAGING DB = " + str(MFG_DB_STAGING)

if DEVICE_TYPE == "Silvretta":
    from config.silvretta import *
elif DEVICE_TYPE == "BMW":
    from config.bmw import *
elif DEVICE_TYPE == "Pluto":
    from config.pluto import *
elif DEVICE_TYPE == "Aquila":
    from config.aquila import *
elif DEVICE_TYPE == "SaturnMKII":
    from config.saturnmkii import *
elif DEVICE_TYPE == "SAM":
    from config.sam import *

#===============================================================================
# LOCATION CONFIGURATION
#===============================================================================
if DEVICE_TYPE == 'Venus':
    MANUFACTURER_NAME='JB'
    TEST_LOCATION='China'

elif DEVICE_TYPE == 'Apollo':
    MANUFACTURER_NAME='VS'
    TEST_LOCATION='Korea'
    
#===============================================================================
# TIME ZONE CONFIGURATION
#===============================================================================
if TEST_LOCATION == 'China' or TEST_LOCATION == 'Korea':
    TIMEZONE = 'Asia/Shanghai'
elif TEST_LOCATION == 'California':
    TIMEZONE = 'America/Los_Angeles'
    
#===============================================================================
# NETWORK CONFIGURATION
#===============================================================================
INTERNET_TEST_URL = "http://www.baidu.com/"
if MFG_DB_STAGING:
    print "\nPosting to staging database.\n"
    BASE_URL = "https://mdapius.int.misfit.com/md/"    
    BASE_URL_DOMAIN_NAME = "https://md.api.int.misfitwearables.com/md/"             # Currently unused
    BASE_URL_DOMAIN_NAME_PING = "https://md.api.int.misfitwearables.com/md/ping"    # Currently unused  
elif TEST_LOCATION == 'China':
    print "\nPosting to China database.\n"
    BASE_URL = "https://120.25.135.158/md/"     # IP address to load-balancer
    # BASE_URL = "https://120.24.74.177/md/"    # Direct IP address to server
    BASE_URL_DOMAIN_NAME = "https://md.api.misfitwearables.com/md/"             # Currently unused
    BASE_URL_DOMAIN_NAME_PING = "https://md.api.misfitwearables.com/md/ping"    # Currently unused
else:
    print "\nPosting to US database.\n"
    BASE_URL = "https://54.163.250.147/md/"    
    BASE_URL_DOMAIN_NAME = "https://md.api.misfitwearables.com/md/"             # Currently unused
    BASE_URL_DOMAIN_NAME_PING = "https://md.api.misfitwearables.com/md/ping"    # Currently unused

#=========================
# ATE_ID
#=========================
if DEVICE_TYPE == 'Venus':
    ATE_ID = 'FL'
    SERIAL_NUM_PREFIX = 'F'
elif DEVICE_TYPE == 'Apollo':
    ATE_ID = 'SH'
    SERIAL_NUM_PREFIX = 'S' 

#===============================================================================
# ATE SCRIPT VERSION (deprecated; github commit hash now stored elsewhere)
#===============================================================================

if DEVICE_TYPE == 'Venus':
    SCRIPT_VERSION = "venus_R1.0" 
elif DEVICE_TYPE == 'Apollo':
    SCRIPT_VERSION = "apollo_R1.0"

#===============================================================================
# STATION SOFTWARE VERSION
#===============================================================================
SCRIPT_VERSION = STATION_SOFTWARE_VERSION
print "Software version is " + STATION_SOFTWARE_VERSION

#=========================
# PHYSICALS
#=========================

if DEVICE_TYPE == 'Venus':
    MECHANICAL_REVISION = "1.0"
    PCB_REVISION = "02-00037-000 3"
    PCBA_REVISION = "06-00019-000 9"
    DEVICE_COLOR = None                 # Needs to come from packaging serial number
    MODEL_NUMBER = "F0"
    LED_COLOR = "RED"
elif DEVICE_TYPE == 'Apollo':
    MECHANICAL_REVISION = "1.0"
    PCB_REVISION = "02-00016-000 PR1"
    PCBA_REVISION = "06-00015-000 PR1"
    DEVICE_COLOR = None                 # Needs to come from packaging serial number
    MODEL_NUMBER = "SH0AZ"
    LED_COLOR = "WHITE"    

# Colormaps for serial number index
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


colorMapVenus = {
            'A':'ONYX',
            'B':'FROST', 
            'C':'COCA-COLA',
            'D':'REEF', 
            'E':'FUSCHIA', 
            'F':'ZEST',
            'G':'REEF',
            }   

# Checks for serial number format
# TODO: Exclude BOI from 2nd char here too
if MANUFACTURER_NAME == 'JB':
    if (DEVICE_TYPE == 'Venus' or DEVICE_TYPE == 'Apollo'):
        if not MFG_DB_STAGING:        
            MATCHSTR_INTERNAL_REGEX = 'Z.ZZ[^BOI]{5}'        
            if STATION_INDEX == -2:
                MATCHSTR_REGEX = 'AZZZ[^BOI]{5}'
                # MATCHSTR_REGEX = '*'
            else:
                MATCHSTR_REGEX = '[^Z].[^Z]Z[^BOI]{5}'
        else:
            MATCHSTR_INTERNAL_REGEX = 'Z.ZZ.{5}' 
            MATCHSTR_REGEX = '[^Z].[^Z]Z{5}'


#=========================
# TEST PARAMETERS
#=========================

# DEFAULTS 
NUM_READINGS = 1                # How many readings to take for each measurement
NUM_READINGS_BASELINE = 100     # How many readings to take for purpose of estimating baseline (for operating current test)
BASELINE_WINDOW_SIZE = 4        # Sliding window size for estimating baseline
DEFAULT_CURRENT_RANGE = 0.1     # 100 mA
MAX_INVALID_RSSI_COUNT = 10
SERIAL_TIMEOUT = 0.1
BUTTON_TOGGLE_TIME = 0.1      # Duration of the GPIO button pin toggle 

PI_VOLTAGE_LOWER = 2.0          
PI_VOLTAGE_UPPER = 5.0

# VENUS
VENUS_MCU_CURRENT_LOWER = 0.0038          # equals 3.8 milliamps
VENUS_MCU_CURRENT_UPPER = 0.0049          # equals 4.9 milliamps
VENUS_IDLE_CURRENT_LOWER  = 0.000003      # equals 3 microamps
VENUS_IDLE_CURRENT_UPPER  = 0.000006      # equals 6 microamps - raised to account for watchdog and 32khz clock
VENUS_LED_CURRENT_LOWER  = 0.0085         # equals 8.5 milliamps
VENUS_LED_CURRENT_UPPER  = 0.0112         # equals 11.2 milliamps
VENUS_LOAD_CURRENT_LOWER  = 0.0050        # equals 5.0 milliamps
VENUS_LOAD_CURRENT_UPPER  = 0.0062        # equals 6.2 milliamps
VENUS_ACCEL_CURRENT_LOWER = 0.000013      # equals 13 microamps
VENUS_ACCEL_CURRENT_UPPER = 0.000019      # equals 19 microamps
VENUS_DEEP_SLEEP_CURRENT_LOWER  = 0.0000002     # equals 0.1 microamps
VENUS_DEEP_SLEEP_CURRENT_UPPER  = 0.0000007     # equals 1.0 microamps
VENUS_Z_DATA_THRESHOLD_LOWER = 307        # accelerometer reading
VENUS_Z_DATA_THRESHOLD_UPPER = 475        # accelerometer reading
VENUS_RSSI_LOWER = -75
VENUS_RSSI_UPPER = -30
VENUS_OPER_CURR_THRESH_LOWER = 0.000006     # equals 6 microamps
VENUS_OPER_CURR_THRESH_UPPER = 0.000018     # equals 18 microamps
VENUS_BATT_BASE_VOLTAGE_THRESH_LOWER = 3000     # equals 3000 mV
VENUS_BATT_BASE_VOLTAGE_THRESH_UPPER = 3300     # equals 3300 mV
VENUS_BATT_LOAD_VOLTAGE_THRESH_LOWER = 2900     # equals 2900 mV
VENUS_BATT_LOAD_VOLTAGE_THRESH_UPPER = 3300     # equals 3300 mV    
VENUS_SERIAL_BAUDRATE = 38400

# APOLLO
APOLLO_MCU_CURRENT_LOWER = 0.0028          # equals 2.8 milliamps
APOLLO_MCU_CURRENT_UPPER = 0.0042          # equals 4.2 milliamps
APOLLO_IDLE_CURRENT_LOWER  = 0.000003      # equals 3.0 microamps
APOLLO_IDLE_CURRENT_UPPER  = 0.000006      # equals 6.0 microamps
APOLLO_LED_CURRENT_LOWER  = 0.0043         # equals 4.3 milliamps
APOLLO_LED_CURRENT_UPPER  = 0.0060         # equals 6.0 milliamps
APOLLO_LOAD_CURRENT_LOWER  = 0.0053        # equals 5.3 milliamps
APOLLO_LOAD_CURRENT_UPPER  = 0.0063        # equals 6.3 milliamps
APOLLO_ACCEL_CURRENT_LOWER = 0.000021      # equals 21 microamps
APOLLO_ACCEL_CURRENT_UPPER = 0.000027      # equals 27 microamps 
APOLLO_DEEP_SLEEP_CURRENT_LOWER  = 0.0000001     # equals 0.1 microamps
APOLLO_DEEP_SLEEP_CURRENT_UPPER  = 0.0000010     # equals 1.0 microamps
APOLLO_Z_DATA_THRESHOLD_LOWER = 402           # accelerometer reading
APOLLO_Z_DATA_THRESHOLD_UPPER = 622           # accelerometer reading
APOLLO_RSSI_LOWER = -75
APOLLO_RSSI_UPPER = -30
APOLLO_OPER_CURR_THRESH_LOWER = 0.0000163   # equals 17 microamps
APOLLO_OPER_CURR_THRESH_UPPER = 0.0000263   # equals 27 microamps
APOLLO_BATT_BASE_VOLTAGE_THRESH_LOWER = 2000        # equals 2000 mV
APOLLO_BATT_BASE_VOLTAGE_THRESH_UPPER = 3500        # equals 3500 mV
APOLLO_BATT_LOAD_VOLTAGE_THRESH_LOWER = 2000        # equals 2000 mV
APOLLO_BATT_LOAD_VOLTAGE_THRESH_UPPER = 3500        # equals 3500 mV    
# TODO: We want an expanded threshold for fw 28, this is a quick & dirty fix. Need to make more robust.
APOLLO_OPER_CURR_THRESH_UPPER_28R = 0.000070    # equals 70 microamps
APOLLO_SERIAL_BAUDRATE = 9600

