
#===============================================================================
# Local constants
#===============================================================================
'''
This file contains local constants to put the test code into a different state.

These will be updated by installSetupATEfiles, setupATEfiles, updateATEfiles.
'''

from ate_settings import *

#=========================
# System control flags
#=========================

DEBUG_MODE = False			# Set to True for more verbose output and pauses between tests
VERBOSE_MODE = True			# Set to True for more output

MFG_DB_STAGING = False		# Write to staging database if True, write to production if False
INTERNET_REQUIRED = False	# Require the internet to run tests	
DATABASE_ACCESS_REQUIRED = True   # Require the database access to run tests (this is not currently used)

GET_IEEE_FROM_SERIAL_INTERNAL = True  # If this is set to true, Station 2 will use the internal serial number to get the IEEE address, else it will use the packaging serial
SCAN_DEVICES_FOR_IEEE = False		  # If IEEE lookup from database fails, scan for device with lowest rssi 
UPDATE_INTERNAL_SERIALS_IN_DB = True  # Overwrite internal serial numbers in database with most recent version 
MEASURE_PI_VOLTAGE = False			  # Measure voltage from the Raspberry Pi before taking current measurements
INVERT_AGILENT_READINGS = False		  # If Agilent is set up in alternate configuration, set this flag to true to invert the measurements back to positive

CLI_MODE = False 					# Run station tests from command line process to isolate memory leaks
STOP_AFTER_FAIL = True				# Ends the tests after any one fails

LIMITED_PIN_SET = True				# True for Aquila, later revs, SaturnMKII
