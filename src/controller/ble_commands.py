#!/usr/bin/env python
'''
Created on 2014-07-07

@author: Rachel Kalmar
'''

from pyblehci import BLEBuilder
from pyblehci import BLEParser
from constants import *
from pprint import pprint
from model.bleDevice import *

import collections
import serial
import helper.utils as util
import helper.MDapi as MDapi
import time
import binascii
import datetime
import sys
import struct

#==========================
# STATE MANAGEMENT
#==========================

def resetDongle(bleController):
    print(bleController.print_output(bleController.ble_builder.send("fe80", reset_type='\x01')))

def initializeDongle(bleController):
    print(bleController.print_output(bleController.ble_builder.send("fe00", max_scan_rsps='\x59')))

def scanForDeviceNoLink(bleController):
    retry_count = 0
    bleController.scan_done = False

    print "\nScanning for devices...\n"
    while retry_count < MAX_NUM_RETRIES_BT and bleController.scan_done == False:

        # Scan for devices
        print(bleController.print_output(bleController.ble_builder.send("fe04", mode="\x03")))
        time.sleep(4)    
    
        # Stop scan        
        print(bleController.print_output(bleController.ble_builder.send("fe05")))

    bleController.scan_done = False    

def scanForDevice(bleController):
    retry_count = 0
    timeout = False
    bleController.scan_done = False

    print "\nScanning for devices...\n"
    while retry_count < MAX_NUM_RETRIES_BT and bleController.scan_done == False:

        # Scan for devices
        print(bleController.print_output(bleController.ble_builder.send("fe04", mode="\x03")))
        time.sleep(4)    
    
        # Stop scan        
        print(bleController.print_output(bleController.ble_builder.send("fe05")))

        # Wait for link
        startTime = util.resetTimer()
        while not bleController.scan_done:
            time.sleep(0.1)
            if util.getTimePassed(startTime) > BT_TIMEOUT:          
                retry_count = retry_count + 1
                if retry_count == MAX_NUM_RETRIES_BT:
                    timeout = True
                    print "\nError: timeout while scanning for devices...\n"
                    break
            pass
        pass

    bleController.scan_done = False    
    return timeout

def scanForDeviceWithRSSIandSerial(serial_number):
    # Instantiate BLE device, BLE controller
    bleDevice = BLEdevice(serial_number = serial_number, 
                        serial_number_internal = None,
                        serial_number_smt = None,
                        ieee = None, 
                        ieeeString = None,
                        rssi = 0)
    bleController = BLEcontroller(bleDevice = bleDevice)

    print "Starting serial communications"
    bleController.startSerialCommunications()

    # Initialize dongle
    initializeDongle(bleController)
    print "Dongle initalized"

    time.sleep(1)

    bleController.scan_by_serial_with_RSSI = True

    discover_saturn_count = 0 #rename this TODO JEE
    ieee_catch = [" ", " "]
    while discover_saturn_count < 3:
        for i in range(0, 2):
            scanForDeviceNoLink(bleController)

            ieee_catch[i] = bleController.device.ieee_string

        if (ieee_catch[0] != ieee_catch[1]):
            print "No matching shines with (max RSSIs, & default serial)."
            if discover_saturn_count == 2:
                print "No matches.  FAIL TEST."
                # Reset controller
                # print "\nResetting dongle"          # We should remove this TODO JEE
                # resetDongle(bleController)
            else:
                print "Trying again."
                discover_saturn_count += 1
        else:
            # we are done.  break from loop
            print "IEEE match!"
            discover_saturn_count = 4

    bleController.scan_done = True   

    # print "\nResetting dongle"
    # resetDongle(bleController)              # We should remove this TODO JEE

    # Need to close controller at end, before creating new ones
    bleController.stopSerialCommunications()
    print "Stopping serial communications\n"

    return bleController.device.ieee_string  # if this fails we should stop the test TODO JEE

def scanForDeviceWithSerial(serial_number):

    # Instantiate BLE device, BLE controller
    bleDevice = BLEdevice(serial_number = serial_number, 
                        serial_number_internal = None,
                        serial_number_smt = None,
                        ieee = None, 
                        ieeeString = None,
                        rssi = 0)
    bleController = BLEcontroller(bleDevice = bleDevice)

    print "Starting serial communications"
    bleController.startSerialCommunications()

    # Initialize dongle
    initializeDongle(bleController)
    print "Dongle initalized"

    bleController.scan_by_serial = True
    scanForDevice(bleController)

    # Reset the controller if we didn't find the IEEE
    if not bleController.scan_done:
        # Reset controller
        print "\nResetting dongle"
        resetDongle(bleController)

    # Need to close controller at end, before creating new ones
    bleController.stopSerialCommunications()
    print "Stopping serial communications\n"

    return bleController.device.ieee_string

def connectToDevice(bleController):
    retry_count = 0
    timeout = False
    bleController.link_established = False
    if DEVICE_TYPE == 'Venus' or DEVICE_TYPE == 'Aquila' or DEVICE_TYPE == 'SaturnMKII':
        addr_type_peer = '\x01'
    elif DEVICE_TYPE == 'Apollo' or DEVICE_TYPE == 'Pluto' or DEVICE_TYPE == 'BMW' or DEVICE_TYPE == 'Silvretta' or DEVICE_TYPE == 'SAM' or DEVICE_TYPE == 'SAM':
        addr_type_peer = '\x00'
    while retry_count < MAX_NUM_RETRIES_BT and bleController.link_established == False:
        # Open connection to device
        print(bleController.print_output(bleController.ble_builder.send("fe09", 
                                        high_duty_cycle = '\x00',       
                                        addr_type_peer = addr_type_peer,                                       
                                        peer_addr=bleController.device.ieee_address)))
        # Wait for link
        startTime = util.resetTimer()
        while not bleController.link_established:
            time.sleep(0.1)
            if util.getTimePassed(startTime) > BT_TIMEOUT:          
                retry_count = retry_count + 1
                if retry_count == MAX_NUM_RETRIES_BT:
                    timeout = True
                    print "\nError: timeout while connecting to Shine...\n"
                    break
            pass
        pass

    return timeout

def setupCharacteristics(bleController):

    bleController.serial_done = False
    print "Enabling notifications for data characteristic"
    if DEVICE_TYPE == 'Venus' or DEVICE_TYPE == 'Aquila' or DEVICE_TYPE == 'SaturnMKII':
        sendBTCommandWRetry(bleController, "serial_done", "fd92", handle="\x0C\x00", value="\x01\x00") # Softdevice 7
        bleController.serial_done = False

        # sendBTCommandWRetry(bleController, "serial_done", "fd92", handle="\x0B\x00", value="\x01\x00") # Softdevice 6
        # bleController.serial_done = False

        sendBTCommandWRetry(bleController, "serial_done", "fd92", handle="\x0F\x00", value="\x01\x00")
        bleController.serial_done = False

        sendBTCommandWRetry(bleController, "serial_done", "fd92", handle="\x12\x00", value="\x01\x00")
        bleController.serial_done = False

        sendBTCommandWRetry(bleController, "serial_done", "fd92", handle="\x15\x00", value="\x01\x00")
        bleController.serial_done = False

    elif DEVICE_TYPE == 'Apollo' or DEVICE_TYPE == 'Pluto' or DEVICE_TYPE == 'BMW' or DEVICE_TYPE == 'Silvretta' or DEVICE_TYPE == 'SAM':
        sendBTCommandWRetry(bleController, "serial_done", "fd92", handle="\x03\x02", value="\x01\x00")
        bleController.serial_done = False

        sendBTCommandWRetry(bleController, "serial_done", "fd92", handle="\x06\x02", value="\x01\x00")
        bleController.serial_done = False

        sendBTCommandWRetry(bleController, "serial_done", "fd92", handle="\x09\x02", value="\x01\x00")
        bleController.serial_done = False

    return None

# def getLinkInterval(bleController):
#     bleController.param_retrieved = False
#     print "Retrieving minimum link interval"
#     print(bleController.print_output(bleController.ble_builder.send("fe31", param_id="\x15")))
#     timeout = False
#     return (timeout, bleController.param_retrieved)

def updateLinkInterval(bleController):
    bleController.param_updated_read = False
    bleController.str_read_type = 'param_updated'
    print "Updating link interval"
    timeout = sendBTCommandWRetry(bleController, "param_updated_read", "fd92", handle="\x02\x02", value="\x02\x09\x0A\x00\x12\x00\x00\x00\x48\x00")
    #print(bleController.print_output(bleController.ble_builder.send("fe11", handle="\x00\x00", interval_min="\x0A\x00", interval_max="\x12\x00", conn_timeout="\x48\x00")))
    #timeout = False
    return (timeout)

def readRSSI(bleController):
    bleController.is_rssi_retrieved = False
    timeout = sendBTCommandWRetry(bleController, "is_rssi_retrieved", "1405", handle="\x00\x00", value=None)    
    return (timeout, bleController.device.getRSSI())

def writeSN(bleController, serial_number):
    print "Serial number passed in to writeSN: %s" % serial_number
    bleController.serial_done = False
    bleController.sn_write_failed = False
    if DEVICE_TYPE == 'Venus' or DEVICE_TYPE == 'Aquila' or DEVICE_TYPE == 'SaturnMKII':
        timeout = sendBTCommandWRetry(bleController, "serial_done", "fd92", handle="\x0B\x00", value="\x02\x07\x01" + serial_number + "\x00")   # Softdevice 7
        # timeout = sendBTCommandWRetry(bleController, "serial_done", "fd92", handle="\x0E\x00", value="\x02\x07\x01" + serial_number + "\x00") # Softdevice 6
    elif DEVICE_TYPE == 'Apollo' or DEVICE_TYPE == 'Pluto' or DEVICE_TYPE == 'BMW' or DEVICE_TYPE == 'Silvretta' or DEVICE_TYPE == 'SAM':
        timeout = sendBTCommandWRetry(bleController, "serial_done", "fd92", handle="\x02\x02", value="\x02\x07\x01" + serial_number + "\x00")
    if bleController.sn_write_failed == True:
        print "Serial number write failed."
    bleController.device.setSerialNumber(serial_number)
    print "Serial number of device now is: %s" % bleController.device.getSerialNumber()
    return (timeout, bleController.sn_write_failed)

def readSN(bleController):
    bleController.serial_received = False
    bleController.str_read_type = 'serial_num'        
    if DEVICE_TYPE == 'Venus' or DEVICE_TYPE == 'Aquila' or DEVICE_TYPE == 'SaturnMKII':
        timeout = sendBTCommandWRetry(bleController, "serial_received", "fd8a", handle="\x1A\x00", value=None)   # Softdevice 7
        # timeout = sendBTCommandWRetry(bleController, "serial_received", "fd8a", handle="\x1D\x00", value=None) # Softdevice 6
    elif DEVICE_TYPE == 'Apollo':
        timeout = sendBTCommandWRetry(bleController, "serial_received", "fd8a", handle="\x34\x00", value=None)
    elif DEVICE_TYPE == 'Pluto' or DEVICE_TYPE == 'BMW' or DEVICE_TYPE == 'Silvretta' or DEVICE_TYPE == 'SAM':
        timeout = sendBTCommandWRetry(bleController, "serial_received", "fd8a", handle="\x38\x00", value=None)
    bleController.str_read_type = None    
    print "Read serial number is: %s" % bleController.device.getSerialNumber()        
    return (timeout, bleController.device.getSerialNumber())

def getFirmwareRevision(bleController):
    bleController.fw_rev_read = False
    bleController.str_read_type = 'firmware'    
    if DEVICE_TYPE == 'Venus' or DEVICE_TYPE == 'Aquila' or DEVICE_TYPE == 'SaturnMKII':
        timeout = sendBTCommandWRetry(bleController, "fw_rev_read", "fd8a", handle="\x1E\x00", value=None)
    elif DEVICE_TYPE == 'Apollo':
        timeout = sendBTCommandWRetry(bleController, "fw_rev_read", "fd8a", handle="\x36\x00", value=None)
    elif DEVICE_TYPE == 'Pluto' or DEVICE_TYPE == 'BMW' or DEVICE_TYPE == 'Silvretta' or DEVICE_TYPE == 'SAM' or DEVICE_TYPE == 'SAM':
        timeout = sendBTCommandWRetry(bleController, "fw_rev_read", "fd8a", handle="\x3A\x00", value=None)
    bleController.str_read_type = None
    print "Read FW revision: %s" % bleController.device.getFWrev()
    return (timeout, bleController.device.fw_rev)

def getAccelerometerStreaming(bleController):
    bleController.serial_done = False
    bleController.str_read_type = 'accel_z_value'

    # Start streaming accelerometer data    
    print "Streaming accelerometer data"
    if DEVICE_TYPE == 'Apollo' or DEVICE_TYPE == 'Pluto' or DEVICE_TYPE == 'BMW' or DEVICE_TYPE == 'Silvretta' or DEVICE_TYPE == 'SAM':
        # timeout = sendBTCommandWRetry(bleController, "zData1", "fd92", handle="\x05\x02", value="\x01\x01\x80\x00\x00\x00\x00\x00\x00\x00\x00")
        bleController.accel_value_read = False
        timeout = sendBTCommandWRetry(bleController, "accel_value_read", "fd92", handle="\x05\x02", value="\x01\x01\x80\x00\x00\x00\x00\x00\x00\x00\x00")

    # Abort streaming
    bleController.serial_done = False
    if DEVICE_TYPE == 'Apollo' or DEVICE_TYPE == 'Pluto' or DEVICE_TYPE == 'BMW' or DEVICE_TYPE == 'Silvretta' or DEVICE_TYPE == 'SAM':
        timeout = sendBTCommandWRetry(bleController, "serial_done", "fd92", handle="\x05\x02", value="\x07\x01\x80")
    bleController.serial_done = False
    return (timeout, bleController.zData1, bleController.zData2, bleController.zData3, bleController.xData1, bleController.xData2, bleController.xData3, bleController.yData1, bleController.yData2, bleController.yData3)

def sendEmptyPacket(bleController):
    print "Sending empty packet"
    print(bleController.print_output(bleController.ble_builder.send("fd92", handle="\x05\x02", value="\xFF\x00\x00")))

def getAccelerometerValue(bleController):
    bleController.accel_value_read = False
    bleController.str_read_type = 'accel_value'    
    if DEVICE_TYPE == 'Venus' or DEVICE_TYPE == 'Aquila' or DEVICE_TYPE == 'SaturnMKII':
        timeout = sendBTCommandWRetry(bleController, "accel_value_read", "fd92", handle="\x0B\x00", value="\x01\xF2\x01")
    elif DEVICE_TYPE == 'Apollo' or DEVICE_TYPE == 'Pluto' or DEVICE_TYPE == 'BMW' or DEVICE_TYPE == 'Silvretta' or DEVICE_TYPE == 'SAM':
        timeout = sendBTCommandWRetry(bleController, "accel_value_read", "fd92", handle="\x02\x02", value="\x01\xF2\x01")
    bleController.str_read_type = None
    print "Read Accelerometer Value: %s" % bleController.device.getAccelValue()
    return (timeout, bleController.device.accel_value)

def getAverageRSSI(bleController):
    bleController.average_rssi_read = False
    bleController.str_read_type = 'average_rssi'    
    timeout = sendBTCommandWRetry(bleController, "average_rssi_read", "fd92", handle="\x02\x02", value="\x01\xF2\x0F")
    bleController.str_read_type = None
    print "Read Average RSSI: %s" % bleController.device.getAverageRSSI()
    return (timeout, bleController.device.average_rssi)

def clearPacketMonitor(bleController):
    """
    This function will clear the BLE packet monitor so that 
    the Packet Error Rate test could be run.
    """
    print "Clearing the BLE packet monitor"
    print(bleController.print_output(bleController.ble_builder.send("fd92", handle="\x02\x02", value="\x01\xF2\x10")))

def getPacketCountTotal(bleController):
    bleController.packet_count_total_read = False
    bleController.str_read_type = 'packet_count_total'    
    timeout = sendBTCommandWRetry(bleController, "packet_count_total_read", "fd92", handle="\x02\x02", value="\x01\xF2\x10")
    bleController.str_read_type = None

    print "Total Packets Received: %s" % bleController.device.getTotalPacketsReceived()
    print "Total Good Packets: %s" % bleController.device.getTotalGoodPackets()

    monitorData = {}
    monitorData['total_packets_received'] = bleController.device.getTotalPacketsReceived()
    monitorData['total_good_packets'] = bleController.device.getTotalGoodPackets()

    return (timeout, monitorData)

def getPacketCountTotalErrors(bleController):
    bleController.packet_count_total_errors_read = False
    bleController.str_read_type = 'packet_count_total_errors'    
    timeout = sendBTCommandWRetry(bleController, "packet_count_total_errors_read", "fd92", handle="\x02\x02", value="\x01\xF2\x11")
    bleController.str_read_type = None

    print "Total CRC Errors: %s" % bleController.device.getTotalCrcErrors()
    print "Total Length Errors: %s" % bleController.device.getTotalLenErrors()
    print "Total Mic Errors: %s" % bleController.device.getTotalMicErrors()
    print "Total Nesn Errors: %s" % bleController.device.getTotalNesnErrors()
    print "Total Sn Errors: %s" % bleController.device.getTotalSnErrors()
    print "Total Sync Errors: %s" % bleController.device.getTotalSyncErrors()
    print "Total Type Errors: %s" % bleController.device.getTotalTypeErrors()
    print "Total Overflow Errors: %s" % bleController.device.getTotalOverflowErrors()

    monitorData = {}
    monitorData['total_crc_errors'] = bleController.device.getTotalCrcErrors()
    monitorData['total_len_errors'] = bleController.device.getTotalLenErrors()
    monitorData['total_mic_errors'] = bleController.device.getTotalMicErrors()
    monitorData['total_nesn_errors'] = bleController.device.getTotalNesnErrors()  
    monitorData['total_sn_errors'] = bleController.device.getTotalSnErrors()
    monitorData['total_sync_errors'] = bleController.device.getTotalSyncErrors()
    monitorData['total_type_errors'] = bleController.device.getTotalTypeErrors()
    monitorData['total_overflow_errors'] = bleController.device.getTotalOverflowErrors()

    return (timeout, monitorData)

def performMagSelfTest(bleController):
    bleController.mag_self_test_read = False
    bleController.str_read_type = 'mag_self_test'    
    if DEVICE_TYPE == 'Pluto' or DEVICE_TYPE == 'BMW' or DEVICE_TYPE == 'Silvretta' or DEVICE_TYPE == 'SAM':
        timeout = sendBTCommandWRetry(bleController, "mag_self_test_read", "fd92", handle="\x02\x02", value="\x01\xF2\x05")
    bleController.str_read_type = None
    print "Read Mag self test result: %s" % bleController.device.getMagResult()
    return (timeout, bleController.device.mag_self_test)

def performLedSelfTest(bleController):
    bleController.led_self_test_read = False
    bleController.str_read_type = 'led_self_test'    
    if DEVICE_TYPE == 'Pluto' or DEVICE_TYPE == 'BMW' or DEVICE_TYPE == 'Silvretta' or DEVICE_TYPE == 'SAM':
        timeout = sendBTCommandWRetry(bleController, "led_self_test_read", "fd92", handle="\x02\x02", value="\x01\xF2\x04")
    bleController.str_read_type = None
    print "Read Open LEDs: %s" % bleController.device.getOpenLeds()
    return (timeout, bleController.device.open_leds)

def getBatteryValue(bleController):
    bleController.battery_value_read = False
    bleController.str_read_type = 'battery_value'        
    if DEVICE_TYPE == 'Venus' or DEVICE_TYPE == 'Aquila' or DEVICE_TYPE == 'SaturnMKII':
        timeout = sendBTCommandWRetry(bleController, "battery_value_read", "fd92", handle="\x0B\x00", value="\x01\xF2\x02")
    elif DEVICE_TYPE == 'Apollo' or DEVICE_TYPE == 'Pluto' or DEVICE_TYPE == 'BMW' or DEVICE_TYPE == 'Silvretta' or DEVICE_TYPE == 'SAM':
        timeout = sendBTCommandWRetry(bleController, "battery_value_read", "fd92", handle="\x02\x02", value="\x01\xF2\x02")
    bleController.str_read_type = None
    print "Read Battery Base Value: %s" % bleController.device.getBatteryBaseValue()
    print "Read Battery Load Value: %s" % bleController.device.getBatteryLoadValue()    
    return (timeout, bleController.device.battery_base_value, bleController.device.battery_load_value)

def getBoostVoltage(bleController):
    bleController.boost_value_read = False
    bleController.str_read_type = 'boost_value'        
    timeout = sendBTCommandWRetry(bleController, "boost_value_read", "fd92", handle="\x02\x02", value=BT_GET_BOOST_VOLTAGE)
    bleController.str_read_type = None

    print "No Load Voltage: %s" % bleController.device.no_load_voltage
    print "Load Voltage: %s" % bleController.device.load_voltage
    print "Boost Voltage: %s" %  bleController.device.boost_voltage 

    return (timeout, bleController.device.no_load_voltage, bleController.device.load_voltage, bleController.device.boost_voltage)

def getCaptouchValue(bleController):
    bleController.captouch_value_read = False
    bleController.str_read_type = 'captouch_value'        
    if DEVICE_TYPE == 'Pluto' or DEVICE_TYPE == 'BMW' or DEVICE_TYPE == 'Silvretta' or DEVICE_TYPE == 'SAM':
        timeout = sendBTCommandWRetry(bleController, "captouch_value_read", "fd92", handle="\x02\x02", value="\x01\xF2\x03")
    bleController.str_read_type = None
    print "Captouch Value: %s" % bleController.device.getCaptouchValue() 
    return (timeout, bleController.device.captouch_value)

def performCaptouchCalibration(bleController):
    bleController.captouch_calibration_read = False
    bleController.str_read_type = 'captouch_calibration'  
    print "Performing captouch calibration"      
    if DEVICE_TYPE == 'Pluto':
        timeout = sendBTCommandWRetry(bleController, "captouch_calibration_read", "fd92", handle="\x02\x02", value="\x01\xF2\x06")
    bleController.str_read_type = None
    print "Captouch MOD_IDAC: %s" % bleController.device.getCaptouchModIdacResult()
    print "Captouch COMP_IDAC: %s" % bleController.device.getCaptouchCompIdacResult() 
    return (timeout, bleController.device.captouch_mod_idac, bleController.device.captouch_comp_idac)

def getVibeValue(bleController):
    bleController.vibe_value_read = False
    bleController.str_read_type = 'vibe_value'        
    if DEVICE_TYPE == 'Pluto' or DEVICE_TYPE == 'BMW' or DEVICE_TYPE == 'Silvretta' or DEVICE_TYPE == 'SAM':
        timeout = sendBTCommandWRetry(bleController, "vibe_value_read", "fd92", handle="\x02\x02", value="\x01\x0F\x02")
    bleController.str_read_type = None
    print "Vibe Value: %s" % bleController.device.getVibeValue() 
    return (timeout, bleController.device.vibe_value)

def getVibeMagnitude(bleController):
    bleController.vibe_magnitude_read = False
    bleController.str_read_type = 'vibe_magnitude'
    if DEVICE_TYPE == 'BMW' or DEVICE_TYPE == 'Pluto'or DEVICE_TYPE == 'SAM':
        timeout = sendBTCommandWRetry(bleController, "vibe_magnitude_read", "fd92", handle="\x02\x02", value="\x01\xF2\x07")
    bleController.str_read_type = None
    print "Vibe Magnitude: %s" % bleController.device.getVibeMagnitude() 
    return (timeout, bleController.device.vibe_magnitude)

def setHandShipPositions(bleController):
    print "Setting hand positions"
    positions = bleController.hand_positions
    print(bleController.print_output(bleController.ble_builder.send("fd92", handle="\x02\x02", value=BT_SET_SHIP_POSITION+positions)))

def getHandPositions(bleController):
    print "Getting hand positions"
    bleController.hand_postion_read = False
    bleController.str_read_type = 'hand_postion'
    timeout = sendBTCommandWRetry(bleController, "hand_postion_read", "fd92", handle="\x02\x02", value="\x01\xF2\x12")
    bleController.str_read_type = None
    print "Current hand positions: %s" % bleController.device.getCurrentHandPositions() 
    return (timeout, bleController.device.current_hand_positions)


def performVibeCalibration(bleController):
    print "Sending vibe calibration command"
    print(bleController.print_output(bleController.ble_builder.send("fd92", handle="\x02\x02", value="\x02\x0F\x01")))


def drvVibeCalibration(bleController, overdrive, rated):
    """
    This function is used in SAM to calibrate the vibe using rated and over voltage values.
    """
    print "Calibrating Vibe with rated voltage of %s mV and over voltage of %s mV." % (bleController.vibe_rated_voltage, bleController.vibe_over_voltage)

    bleController.vibe_calibration_read = False
    bleController.str_read_type = 'vibe_calibration'
    # ratedVoltage and overVoltage are passed in as the bleController member variables.
    # ratedVoltage must come first.

    timeout = sendBTCommandWRetry(bleController, "vibe_calibration_read", "fd92", handle="\x02\x02", value=''.join([BT_SET_VIBE_CAL, overdrive, rated]))
    bleController.str_read_type = None
    #if vibe_calibration is 1, pass, else, fail.
    return (timeout, bleController.device.vibe_calibration_result)


##########################################################################
def drvVibeCalibration1(bleController):
    """
    This function is used in SAM to calibrate the vibe using rated and over voltage values.
    Used for data collection, remove later.
    """

    bleController.vibe_calibration_read = False
    bleController.str_read_type = 'vibe_calibration'
    # ratedVoltage and overVoltage are passed in as the bleController member variables.
    # ratedVoltage must come first.

    timeout = sendBTCommandWRetry(bleController, "vibe_calibration_read", "fd92", handle="\x02\x02", value=VIBE_CAL_200_200)
    bleController.str_read_type = None
    #if vibe_calibration is 1, pass, else, fail.
    return (timeout, bleController.device.vibe_calibration_result)

def drvVibeCalibration2(bleController):
    """
    This function is used in SAM to calibrate the vibe using rated and over voltage values.
    Used for data collection, remove later.
    """

    bleController.vibe_calibration_read = False
    bleController.str_read_type = 'vibe_calibration'
    # ratedVoltage and overVoltage are passed in as the bleController member variables.
    # ratedVoltage must come first.

    timeout = sendBTCommandWRetry(bleController, "vibe_calibration_read", "fd92", handle="\x02\x02", value=VIBE_CAL_400_400)
    bleController.str_read_type = None
    #if vibe_calibration is 1, pass, else, fail.
    return (timeout, bleController.device.vibe_calibration_result)

def drvVibeCalibration3(bleController):
    """
    This function is used in SAM to calibrate the vibe using rated and over voltage values.
    Used for data collection, remove later.
    """

    bleController.vibe_calibration_read = False
    bleController.str_read_type = 'vibe_calibration'
    # ratedVoltage and overVoltage are passed in as the bleController member variables.
    # ratedVoltage must come first.

    timeout = sendBTCommandWRetry(bleController, "vibe_calibration_read", "fd92", handle="\x02\x02", value=VIBE_CAL_600_600)
    bleController.str_read_type = None
    #if vibe_calibration is 1, pass, else, fail.
    return (timeout, bleController.device.vibe_calibration_result)

def drvVibeCalibration4(bleController):
    """
    This function is used in SAM to calibrate the vibe using rated and over voltage values.
    Used for data collection, remove later.
    """

    bleController.vibe_calibration_read = False
    bleController.str_read_type = 'vibe_calibration'
    # ratedVoltage and overVoltage are passed in as the bleController member variables.
    # ratedVoltage must come first.

    timeout = sendBTCommandWRetry(bleController, "vibe_calibration_read", "fd92", handle="\x02\x02", value=VIBE_CAL_800_800)
    bleController.str_read_type = None
    #if vibe_calibration is 1, pass, else, fail.
    return (timeout, bleController.device.vibe_calibration_result)

def drvVibeCalibration5(bleController):
    """
    This function is used in SAM to calibrate the vibe using rated and over voltage values.
    Used for data collection, remove later.
    """

    bleController.vibe_calibration_read = False
    bleController.str_read_type = 'vibe_calibration'
    # ratedVoltage and overVoltage are passed in as the bleController member variables.
    # ratedVoltage must come first.

    timeout = sendBTCommandWRetry(bleController, "vibe_calibration_read", "fd92", handle="\x02\x02", value=VIBE_CAL_1000_1000)
    bleController.str_read_type = None
    #if vibe_calibration is 1, pass, else, fail.
    return (timeout, bleController.device.vibe_calibration_result)

def drvVibeCalibration6(bleController):
    """
    This function is used in SAM to calibrate the vibe using rated and over voltage values.
    Used for data collection, remove later.
    """

    bleController.vibe_calibration_read = False
    bleController.str_read_type = 'vibe_calibration'
    # ratedVoltage and overVoltage are passed in as the bleController member variables.
    # ratedVoltage must come first.

    timeout = sendBTCommandWRetry(bleController, "vibe_calibration_read", "fd92", handle="\x02\x02", value=VIBE_CAL_1200_1200)
    bleController.str_read_type = None
    #if vibe_calibration is 1, pass, else, fail.
    return (timeout, bleController.device.vibe_calibration_result)

def drvVibeCalibration7(bleController):
    """
    This function is used in SAM to calibrate the vibe using rated and over voltage values.
    Used for data collection, remove later.
    """

    bleController.vibe_calibration_read = False
    bleController.str_read_type = 'vibe_calibration'
    # ratedVoltage and overVoltage are passed in as the bleController member variables.
    # ratedVoltage must come first.

    timeout = sendBTCommandWRetry(bleController, "vibe_calibration_read", "fd92", handle="\x02\x02", value=VIBE_CAL_1200_600)
    bleController.str_read_type = None
    #if vibe_calibration is 1, pass, else, fail.
    return (timeout, bleController.device.vibe_calibration_result)

def drvVibeCalibration8(bleController):
    """
    This function is used in SAM to calibrate the vibe using rated and over voltage values.
    Used for data collection, remove later.
    """

    bleController.vibe_calibration_read = False
    bleController.str_read_type = 'vibe_calibration'
    # ratedVoltage and overVoltage are passed in as the bleController member variables.
    # ratedVoltage must come first.

    timeout = sendBTCommandWRetry(bleController, "vibe_calibration_read", "fd92", handle="\x02\x02", value=VIBE_CAL_900_600)
    bleController.str_read_type = None
    #if vibe_calibration is 1, pass, else, fail.
    return (timeout, bleController.device.vibe_calibration_result)   
##########################################################################

def resetViaBT(bleController):
    bleController.reset_done = True    
    print "Resetting DUT..."  
    if DEVICE_TYPE == 'Venus' or DEVICE_TYPE == 'Aquila' or DEVICE_TYPE == 'SaturnMKII':
        print(bleController.print_output(bleController.ble_builder.send("fd92", handle="\x0B\x00", value="\x02\xF1\x02")))        
        timeout = False   
        # timeout = sendBTCommandWRetry(bleController, "reset_done", "fd92", handle="\x0B\x00", value="\x02\xF1\x02")
    elif DEVICE_TYPE == 'Apollo' or DEVICE_TYPE == 'Pluto' or DEVICE_TYPE == 'BMW' or DEVICE_TYPE == 'Silvretta' or DEVICE_TYPE == 'SAM':
        print(bleController.print_output(bleController.ble_builder.send("fd92", handle="\x02\x02", value="\x02\xF1\x0A")))                
        timeout = False
    return (timeout, bleController.reset_done)

def stopLedAnimation(bleController):
    print "Stopping LED Animation"
    # This command is sent without requiring a response from the device.  This was changed from using sendBTCommandWRetry() because it wasn't working. Need to understand why.
    if DEVICE_TYPE == "BMW":
        print(bleController.print_output(bleController.ble_builder.send("fd92", handle="\x02\x02", value="\x01\xF2\x08")))
    else:
        print(bleController.print_output(bleController.ble_builder.send("fd92", handle="\x02\x02", value="\x02\xF1\x07")))

def playSound(bleController, frequency):
    bleController.reset_done = True    
    print "Playing sound at " + str(frequency) + " hz"  
    # command 0x020F04 FFFFFFFF MM DDDD

    frequency = str(struct.pack('<Q', frequency))
    if DEVICE_TYPE == 'Pluto' or DEVICE_TYPE == 'BMW' or DEVICE_TYPE == 'Silvretta' or DEVICE_TYPE == 'SAM':
        print(bleController.print_output(bleController.ble_builder.send("fd92", handle="\x02\x02", value="\x04\x0F\x02\x88\x13\x00\x00\x02\xd0\x07")))                
        timeout = False
    return (timeout, bleController.reset_done)

def vibeAtFrequency(bleController):

    print "Vibing at 250 hz"  
    # command 0x020F04 FFFFFFFF MM DDDD

    if DEVICE_TYPE == 'Pluto' or DEVICE_TYPE == 'BMW' or DEVICE_TYPE == 'Silvretta' or DEVICE_TYPE == 'SAM':
        print(bleController.print_output(bleController.ble_builder.send("fd92", handle="\x02\x02", value="\x02\x0F\x04\xC4\x09\x00\x00\x01\x00\x00")))                
        
def stopVibe(bleController):

    print "Stopping vibe"  

    if DEVICE_TYPE == 'Pluto' or DEVICE_TYPE == 'BMW' or DEVICE_TYPE == 'Silvretta' or DEVICE_TYPE == 'SAM':
        print(bleController.print_output(bleController.ble_builder.send("fd92", handle="\x02\x02", value="\x02\x0F\x03")))                
 
def setTime(bleController):
    print "Setting time on device"

    # Get current time
    t = time.time()

    # Get the time interval and convert it to bytes in little endian format
    utcTime = util.convertUint32ToBytesLe(int(t))
    ms = (t - int(t)) * 1000

    # Get the milliseconds interval and convert it to bytes in little endian format
    ms = util.convertInt16ToBytesLe(int(ms))

    print(bleController.print_output(bleController.ble_builder.send("fd92", handle="\x02\x02", value="\x02\x04"+utcTime+ms+"\x00\x00")))

def getTime(bleController):
    print "Getting time on device"
    bleController.device_time_read = False
    bleController.str_read_type = 'device_time_value'        
    timeout = sendBTCommandWRetry(bleController, "device_time_read", "fd92", handle="\x02\x02", value="\x01\x04")
    bleController.str_read_type = None
    print "Device time: %s" % bleController.device.getDeviceTime() 
    return (timeout, bleController.device.device_time)


def closeLink(bleController):
    bleController.link_closed = False
    timeout = sendBTCommandWRetry(bleController, "link_closed", "fe0a", handle=None, value=None)

def sendBTCommandWRetry(bleController, var_name, command, handle, value):
    retry_count = 0
    timeout = False
    while retry_count < MAX_NUM_RETRIES_BT and (getattr(bleController, var_name) == False or getattr(bleController,var_name) == ''):

        # Open connection to device
        print "Sending " + command + " and checking " + var_name + " Retry count " + str(retry_count)
        print(bleController.print_output(bleController.ble_builder.send(command, handle=handle, value=value)))

        # Wait for link
        startTime = util.resetTimer()
        while not getattr(bleController,var_name) or getattr(bleController,var_name) == '':
            time.sleep(0.1)
            if util.getTimePassed(startTime) > BT_TIMEOUT:
                retry_count += 1
                if retry_count == MAX_NUM_RETRIES_BT:
                    timeout = True
                    print "TIMEOUT OCCURED"
                    break
            pass
        pass
    return timeout

def openConnection(ieee_address):

    timeout = False
    fw_rev = None

    print "\nOpening connection to ieee_address: %s \n" % ieee_address

    ieee_transmit = (ieee_address[10:12] + 
                    ieee_address[8:10] + 
                    ieee_address[6:8] + 
                    ieee_address[4:6] + 
                    ieee_address[2:4] + 
                    ieee_address[0:2])

    print "     ieee_transmit: %s" % ieee_transmit
    print "     ieee_address: %s" % ieee_address
    ieeeBinary = str(binascii.unhexlify(ieee_transmit))
    print "     ieee_binary: %s\n" % ieeeBinary

    # Instantiate BLE device, BLE controller
    bleDevice = BLEdevice(serial_number = None, 
                        serial_number_internal = None,
                        serial_number_smt = None,
                        ieee = ieeeBinary, 
                        ieeeString = ieee_address,
                        rssi = 0)
    bleController = BLEcontroller(bleDevice = bleDevice)

    print "Starting serial communications"
    bleController.startSerialCommunications()

    # Initialize dongle
    print "Initializing dongle..."
    initializeDongle(bleController)

    time.sleep(0.25) # Short delay between commands to ensure stability of ATE 2.  This is chose arbitrarily and should be revisited after the first 10k.

    # print "\nChanging connection interval\n"
    # updateLinkInterval(bleController)
    print "Dongle initialized"
    # Scan for DUT
    if SCAN_FOR_DUT:
        print "Scanning for DUT"    
        scanForDevice(bleController)

    # Connect to Shine
    timeout = connectToDevice(bleController)
    if not timeout:
        print "Connected to DUT"

        time.sleep(0.25) # Short delay between commands to ensure stability of ATE 2.  This is chose arbitrarily and should be revisited after the first 10k.

        print "\nSetting up Characteristics\n"
        setupCharacteristics(bleController)

        time.sleep(0.25) # Short delay between commands to ensure stability of ATE 2.  This is chose arbitrarily and should be revisited after the first 10k.

        # Get firmware revision
        print "\nGetting firmware revision\n"        
        (timeout, fw_rev) = getFirmwareRevision(bleController)
        print ""

    return (bleController, fw_rev, timeout)

def closeConnection(bleController):

    if not bleController.reset_done:
        # Close link
        closeLink(bleController)
        print "Link closed"

    # Reset controller
    print "\nResetting dongle"
    resetDongle(bleController)

    time.sleep(0.25) # Short delay between commands to ensure stability of ATE 2.  This is chose arbitrarily and should be revisited after the first 10k.

    # Need to close controller at end, before creating new ones
    bleController.stopSerialCommunications()
    print "Stopping serial communications\n"

    return True

class BLEcontroller():
        
    def __init__(self, bleDevice):
        self.device = bleDevice

        self.link_established = False
        self.link_closed = False
        self.is_rssi_retrieved = False
        self.serial_done = False
        self.sn_write_failed = False
        self.scan_done = False
        self.scan_by_serial = False  
        self.scan_by_serial_with_RSSI = False
        self.files_erased = False
        self.got_file = False
        self.erase_count = 0
        self.serial_received = False
        self.fw_rev_read = False
        self.accel_value_read = False
        self.battery_value_read = False
        self.reset_done = False
        self.param_updated_read = False
        self.captouch_value_read = False
        self.vibe_value_read = False
        self.led_self_test_read = False
        self.led_stop_read = False
        self.vibe_magnitude_read = False
        self.vibe_calibration_read = False
        self.average_rssi_read = False
        self.packet_count_total_read = False
        self.packet_count_total_errors_read = False
        self.device_time_read = False
        self.hand_postion_read = False
        self.boost_value_read = False
        # self.param_retrieved = False
        self.str_read_type = None
        self.max_rssi = APOLLO_RSSI_LOWER          #used for scan_by_serial_with_RSSI
        self.xData1 = ''
        self.xData2 = ''
        self.xData3 = ''
        self.yData1 = ''
        self.yData2 = ''
        self.yData3 = ''
        self.zData1 = ''
        self.zData2 = ''
        self.zData3 = ''
        self.captouch_calibration_read = False
        self.vibe_over_voltage = None
        self.vibe_rated_voltage = None
        return

    def startSerialCommunications(self):
        # Connect to USB radio

        self.serial_port = serial.Serial(USB_RADIO_PATH)

        # Setup bt module
        self.ble_builder = BLEBuilder(self.serial_port)
        self.ble_parser = BLEParser(self.serial_port, callback=self.__analysePacket)


    def stopSerialCommunications(self):

        self.ble_parser.stop()
        self.serial_port.close()

    def __analysePacket(self, (packet, dictionary)):    
        # pprint(vars(self))

        packet_str = self.__pretty(packet, '.')
        eventCode = packet_str[9:14] 
        status = packet_str[15:17]
        eventType = packet_str[18:20]
        if DEBUG_MODE:
            print "Printing packet string: "
            print packet_str
        print "Event code: %s" % eventCode

        # DEVICE INFORMATION EVENT
        if eventCode == '0D.06':
            print "\n......"            
            print "Device Info Packet"
            if eventType == '00':
                if DEBUG_MODE:
                    print "eventType = 0"
                misfitSN = True
                # Look for DF.00 and then take next 12 packets
                temp = packet_str[41:].split('DF.00.')
                # print "\n\nPost-IEEE packet string: %s" % packet_str[41:]
                if len(temp) >= 2:
                    currentSN = temp[1]                 
                    if DEBUG_MODE:   
                        print "\nUsing SN split on DF.00: %s" % currentSN
                else:
                    misfitSN = False
                    print "\n         Not a Misfit device...\n"
                    # currentSN = packet_str[69:98]

                if misfitSN:
                    ieeeLog = (packet_str[24:41])[::-1]  
                    # ieee = [_ for _ in reversed(packet_str[24:41].split('.'))]                              
                    ieee = [_ for _ in packet_str[24:41].split('.')]
                    # print "IEEE: %s" % ieee
                    ieeeString = ''
                    for each in ieee:
                        ieeeString = each + ieeeString
                    if VERBOSE_MODE:
                        print "\n         ieeeString: %s" % ieeeString
                        print "         self.device.ieee_string: %s" % self.device.ieee_string
                        print "         self.device.ieee_address: %s\n" % self.device.ieee_address                

                    currentSN_str = hexToSerialNum(currentSN)
                    if ieeeString == self.device.ieee_string:
                        if DEBUG_MODE:
                            print "\n......\n......\n......\n......\n"
                        print "Device found!"
                        if DEBUG_MODE:
                            print "\n......\n......\n......\n......\n"
                        print "         ieee: %s" % ieee
                        print "         ieeeLog %s" % ieeeLog
                        # self.device.serialNumber = currentSN
                        print "         Current serial number: %s" % currentSN
                        print "         Current serial number (string): %s\n\n\n" % currentSN_str
                        self.scan_done = True

                    if self.scan_by_serial:
                        print "         Serial number (from device): %s" % currentSN_str
                        print "         Serial number (from UI): %s\n\n" % self.device.serial_number
                        if currentSN_str == self.device.serial_number:
                            print "......\n......\n......"
                            print "Found %s!" % currentSN_str
                            print "......\n......\n......\n"                            
                            print "         Setting IEEE to %s." % ieeeString
                            self.device.setIEEEstring(ieeeString)
                            print "         IEEE is now: %s\n\n" % self.device.ieee_string
                            self.scan_done = True

                    if self.scan_by_serial_with_RSSI:
                        print "         Serial number (from device): %s" % currentSN_str
                        print "         Serial number (from UI): %s\n\n" % self.device.serial_number
                        if (currentSN_str == self.device.serial_number) or (currentSN_str == "9876543210"):
                            print "......\n......\n......"
                            print "Found %s!" % currentSN_str
                            print "......\n......\n......\n"  
                            tempRSSI = int(packet_str[42:44], 16) - 256 
                            print "getting RSSI: %d" % tempRSSI
                            if tempRSSI > self.max_rssi:  
                                print "......\n......\n......"
                                print "Found Better RSSI %d!" % tempRSSI
                                print "......\n......\n......\n" 
                                self.max_rssi = tempRSSI                       
                                print "         Setting IEEE to %s." % ieeeString
                                self.device.setIEEEstring(ieeeString)
                                print "         IEEE is now: %s\n\n" % self.device.ieee_string
                                #self.scan_done = True

        # Read Char 
        if eventCode == '0B.05':
            if DEBUG_MODE:
                print "eventType = 0B.05"            
            if self.str_read_type == 'firmware':
                fwRevReceived = [_ for _ in reversed(packet_str[27:].split('.'))]
                fwRev = ''
                for each in fwRevReceived:
                    fwRev = each + fwRev
                self.device.fw_rev = str(binascii.unhexlify(fwRev))
                print "fw_rev: %s\n" % self.device.fw_rev
                self.fw_rev_read = True
            elif self.str_read_type == 'serial_num':
                if DEBUG_MODE:
                    print "SN PACKET", packet_str[27:56]
                snRecieved = [_ for _ in reversed(packet_str[27:56].split('.'))]
                snRecievedString = ''
                for each in snRecieved:
                    snRecievedString = each + snRecievedString
                serialFromShine = str(binascii.unhexlify(snRecievedString))
                self.device.serial_number = serialFromShine
                self.device.serial_number_str = snRecievedString
                self.serial_received = True

        if eventCode == '1B.05':
            if DEBUG_MODE:
                print "eventType = 1B.05"   
            if self.str_read_type == 'accel_value':
                print "Get and set accel_value here\n"               
                accel_value = packet_str[40]
                self.device.setAccelValue(accel_value)
                self.accel_value_read = True
            elif self.str_read_type == 'accel_z_value' and packet_str[24:26] == '16' and self.zData1 =='':                
                print "Get streaming accelerometer data here\n"
                print "packet_str: "
                print packet_str
                foo = ''
                for x in range(0,len(packet_str),3):
                    foo = foo + str(x) + str(x+1) + '.'
                print foo
                print ""

                xData1 = ''
                xData2 = ''
                xData3 = ''

                yData1 = ''
                yData2 = ''
                yData3 = ''

                zData1 = ''
                zData2 = ''
                zData3 = ''
                
                xData1 = packet_str[42:44] + packet_str[39:41]
                yData1 = packet_str[48:50] + packet_str[45:47]
                zData1 = packet_str[54:56] + packet_str[51:53]

                xData2 = packet_str[60:62] + packet_str[57:59]
                yData2 = packet_str[66:68] + packet_str[63:65]
                zData2 = packet_str[72:74] + packet_str[69:71]

                xData3 = packet_str[78:80] + packet_str[75:77]
                yData3 = packet_str[84:86] + packet_str[81:83]
                zData3 = packet_str[90:92] + packet_str[87:89]

                if DEBUG_MODE:
                    print "xData1: %s" % xData1
                    print "xData2: %s" % xData2                
                    print "xData3: %s" % xData3

                if xData1 == '':
                    print "Warning: xData1 is empty!"
                    self.xData1 = 0
                else:
                    self.xData1 = util.twosComplement(int(xData1, 16))
                if xData2 == '':
                    print "Warning: xData2 is empty!"
                    self.xData2 = 0
                else:                    
                    self.xData2 = util.twosComplement(int(xData2, 16))
                if xData3 == '':
                    print "Warning: xData3 is empty!"
                    self.xData3 = 0
                else:
                    self.xData3 = util.twosComplement(int(xData3, 16))

                if DEBUG_MODE:
                    print "xData1: %s" % self.xData1
                    print "xData2: %s" % self.xData2                
                    print "xData3: %s" % self.xData3  

                    print "yData1: %s" % yData1
                    print "yData2: %s" % yData2                
                    print "yData3: %s" % yData3

                if yData1 == '':
                    print "Warning: yData1 is empty!"
                    self.yData1 = 0
                else:
                    self.yData1 = util.twosComplement(int(yData1, 16))
                if yData2 == '':
                    print "Warning: yData2 is empty!"
                    self.yData2 = 0
                else:                    
                    self.yData2 = util.twosComplement(int(yData2, 16))
                if yData3 == '':
                    print "Warning: yData3 is empty!"
                    self.yData3 = 0
                else:
                    self.yData3 = util.twosComplement(int(yData3, 16))

                if DEBUG_MODE:
                    print "yData1: %s" % self.yData1
                    print "yData2: %s" % self.yData2                
                    print "yData3: %s" % self.yData3   

                    print "zData1: %s" % zData1
                    print "zData2: %s" % zData2                
                    print "zData3: %s" % zData3

                if zData1 == '':
                    print "Warning: zData1 is empty!"
                    self.zData1 = 0
                else:
                    self.zData1 = util.twosComplement(int(zData1, 16))
                if zData2 == '':
                    print "Warning: zData2 is empty!"
                    self.zData2 = 0
                else:                    
                    self.zData2 = util.twosComplement(int(zData2, 16))
                if zData3 == '':
                    print "Warning: zData3 is empty!"
                    self.zData3 = 0
                else:
                    self.zData3 = util.twosComplement(int(zData3, 16))

                if DEBUG_MODE:
                    print "zData1: %s" % self.zData1
                    print "zData2: %s" % self.zData2                
                    print "zData3: %s" % self.zData3                
                self.accel_value_read = True            
            elif self.str_read_type == 'accel_z_value' and packet_str[24:26] == '16':                
                self.serial_done = True            
            elif self.str_read_type == 'battery_value':
                print "Getting battery base voltage and no load voltage\n"
                batteryVoltages = "".join(packet_str.split('.'))
                batteryVoltages = batteryVoltages[-8:]
                battery_base_str = batteryVoltages[2:4] + batteryVoltages[0:2]
                battery_load_str = batteryVoltages[6:8] + batteryVoltages[4:6]

                battery_base_value = int(battery_base_str, 16)
                battery_load_value = int(battery_load_str, 16)

                if DEBUG_MODE:
                    print "battery_base_str: %s" % battery_base_str
                    print "battery_load_str: %s" % battery_load_str
                    print "battery_base_value (dec): %s" % battery_base_value      
                    print "battery_load_value (dec): %s" % battery_load_value                          
                    print ""    

                self.device.setBatteryBaseValue(battery_base_value)
                self.device.setBatteryLoadValue(battery_load_value)                    
                print "Battery base value: %s" % self.device.getBatteryBaseValue()      
                print "Battery load value: %s" % self.device.getBatteryLoadValue()                                                      
                self.battery_value_read = True  
            elif self.str_read_type == 'boost_value':
                print "Getting no load voltage, load voltage, and boost voltage\n"
                voltages = "".join(packet_str.split('.'))
                voltages = voltages[-12:]
                no_load_str = voltages[2:4] + voltages[0:2]
                load_str = voltages[6:8] + voltages[4:6]
                boost_str = voltages[10:12] + voltages[6:8]

                no_load_value = int(no_load_str, 16)
                load_value = int(load_str, 16)
                boost_value = int(boost_str, 16)

                self.device.no_load_voltage = no_load_value
                self.device.load_voltage = load_value
                self.device.boost_voltage  = boost_value                    
                print "No Load Voltage: %s" % self.device.no_load_voltage    
                print "Load Voltage: %s" % self.device.load_voltage  
                print "Boost Voltage: %s" % self.device.boost_voltage         

                self.boost_value_read = True  
            elif self.str_read_type == 'captouch_value':
                print "Get captouch value\n"
                captouch_value = packet_str[-2:]
                captouch_value = int(captouch_value, 16)
                self.device.setCaptouchValue(captouch_value)
                print "Captouch value: %s" % self.device.getCaptouchValue()
                self.captouch_value_read = True
            elif self.str_read_type == 'captouch_calibration':
                print "Getting captouch MOD and COMP IDAC values"
                mod_idac = int(packet_str[-5:-3], 16)
                comp_idac = int(packet_str[-2:], 16)

                self.device.setCaptouchModIdacResult(mod_idac)
                self.device.setCaptouchCompIdacResult(comp_idac)

                print "MOD_IDAC: %s" % mod_idac
                print "COMP_IDAC: %s" % comp_idac

                self.captouch_calibration_read = True
            elif self.str_read_type == 'vibe_cal':
                print "Performing vibe calibration"
                self.vibe_cal_read = True
            elif self.str_read_type == 'vibe_value':
                print "Get vibe value"
                vibe_value_little = packet_str[-5:-3]
                vibe_value_big = packet_str[-2:]
                vibe_value = vibe_value_big + vibe_value_little

                vibe_value = float(int(vibe_value, 16) / 10)
                self.device.setVibeValue(vibe_value)
                print "Vibe frequency: %s hz" % self.device.getVibeValue()
                self.vibe_value_read = True
            elif self.str_read_type == 'vibe_magnitude':
                print "Get vibe magnitude"
                vibe_magnitude = packet_str[-2:]
                vibe_magnitude = int(vibe_magnitude, 16)
                self.device.setVibeMagnitude(vibe_magnitude)
                print "Vibe magnitude is %s" % self.device.getVibeMagnitude()
                self.vibe_magnitude_read = True
            elif self.str_read_type == 'vibe_calibration':
                vibe_calibration = packet_str[-2:]
                vibe_calibration = int(vibe_calibration, 16)
                self.device.setVibeCalibrationResult(vibe_calibration)
                print "Vibe calibration is %s" % self.device.getVibeCalibrationResult()
                self.vibe_calibration_read = True
            elif self.str_read_type == 'led_self_test':
                print "Getting LED self test results"
                led_value_little = packet_str[-5:-3]
                led_value_big = packet_str[-2:]
                led_value = led_value_big + led_value_little
                led_value = int(led_value, 16)
                self.device.setOpenLeds(led_value)
                print "Open LED self test results: %04X" % self.device.getOpenLeds()
                self.led_self_test_read = True
            elif self.str_read_type == 'mag_self_test':
                print "Getting Mag self test results"
                mag_result = packet_str[-2:]
                mag_result = int(mag_result)
                self.device.setMagResult(mag_result)
                self.mag_self_test_read = True
            elif self.str_read_type == 'average_rssi':
                print "Getting average RSSI."
                average_rssi = packet_str[-2:]
                average_rssi = int(average_rssi, 16) - 256
                self.device.setAverageRSSI(average_rssi)
                self.average_rssi_read = True
            elif self.str_read_type == 'packet_count_total':
                print "Getting BLE monitor data."
                monitorData = "".join(packet_str.split('.'))
                monitorData = monitorData[-16:]
                totalCount = int(monitorData[6:8] + monitorData[4:6] + monitorData[2:4] +  monitorData[0:2], 16)
                totalGoodPackets = int(monitorData[14:] + monitorData[12:14] + monitorData[10:12] +  monitorData[8:10], 16)

                self.device.setTotalPacketsReceived(totalCount)
                self.device.setTotalGoodPackets(totalGoodPackets)

                self.packet_count_total_read = True

            elif self.str_read_type == 'packet_count_total_errors':
                monitorData = "".join(packet_str.split('.'))
                monitorData = monitorData[-32:]

                crc_error = int(monitorData[2:4] +  monitorData[0:2], 16)
                len_error = int(monitorData[6:8] +  monitorData[4:6], 16)
                mic_error = int(monitorData[10:12] +  monitorData[8:10], 16)
                nesn_error = int(monitorData[14:16] +  monitorData[12:14], 16)
                sn_error = int(monitorData[18:20] +  monitorData[16:18], 16)
                sync_error = int(monitorData[22:24] +  monitorData[20:22], 16)
                type_error = int(monitorData[26:28] +  monitorData[24:26], 16)
                overflow_error = int(monitorData[30:32] +  monitorData[28:30], 16)

                self.device.setTotalCrcErrors(crc_error)
                self.device.setTotalLenErrors(len_error)
                self.device.setTotalMicErrors(mic_error)
                self.device.setTotalNesnErrors(nesn_error)
                self.device.setTotalSnErrors(sn_error)
                self.device.setTotalSyncErrors(sync_error)
                self.device.setTotalTypeErrors(type_error)
                self.device.setTotalOverflowErrors(overflow_error)

                self.packet_count_total_errors_read = True

            elif self.str_read_type == 'param_updated':
                response = "".join(packet_str.split('.'))
                response = response[-14:]
                isSuccessful = response[0:2]

                print "Response: " + isSuccessful

                self.param_updated_read = True

            elif self.str_read_type == 'device_time_value':
                deviceTime = "".join(packet_str.split('.'))
                deviceTime = deviceTime[-16:]

                utcTime = int(deviceTime[6:8] + deviceTime[4:6] + deviceTime[2:4] + deviceTime[0:2], 16)
                #milliseconds = int(deviceTime[10:12] + deviceTime[8:10])
                #timeZone = int(deviceTime[14:16] + deviceTime[12:14])

                self.device.setDeviceTime(utcTime)
                self.device_time_read = True
            elif self.str_read_type == 'hand_postion':
                positions = "".join(packet_str.split('.'))
                positions = positions[-12:]

                subeye = int(positions[2:4] + positions[0:2], 16)
                minute = int(positions[6:8] + positions[4:6], 16)
                hour = int(positions[10:12] + positions[8:10], 16)

                if subeye >= 360:
                    subeye = subeye - 360

                if minute >= 360:
                    minute = minute - 360

                if hour >= 360:
                    hour = hour - 360

                positions = ''.join( [ "%02X" % ord( x ) for x in util.convertInt16ToBytesLe(subeye) ] ).strip()
                positions += ''.join( [ "%02X" % ord( x ) for x in util.convertInt16ToBytesLe(minute) ] ).strip()
                positions += ''.join( [ "%02X" % ord( x ) for x in util.convertInt16ToBytesLe(hour) ] ).strip()

                print "Current hand positions: " + positions
                self.device.setCurrentHandPositions(positions)
                self.hand_postion_read = True

            elif packet_str[33:35] == '02':
                print "GET RESPONSE PACKET"
                if packet_str[42:44] == '02' or packet_str[36:38] == '00':
                    print "Get response successful."
                    self.got_file = True
            elif packet_str[33:35] == '04':
                print "ERASE RESPONSE PACKET"
                # erase_count += 1 # this will cause the main thread to erase another file
                if packet_str[42:44] == '02':
                    # invalid file handle so we've erased all files
                    self.files_erased = True

        # DEVICE DISCOVERY DONE
        if eventCode == '01.06':
            if DEBUG_MODE:
                print "eventType = 01.06"               
            print "Device discovery done"
            self.scan_done = True

        # LINK ESTABLISHED RESPONSE
        if eventCode == '05.06':
            if DEBUG_MODE:
                print "eventType = 05.06"              
            print "Link established"
            self.link_established = True

        # ATT_ErrorRsp
        if eventCode == '01.05':
            if DEBUG_MODE:
                print "eventType = 01.05"              
            self.sn_write_failed = True
            self.serial_done = True
        
        # Successful ATT_ReadRsp
        if eventCode == '13.05' and status == '00':
            if DEBUG_MODE:
                print "eventType = 13.05"              
            self.serial_done = True
            self.led_stop_read = True

        # Successful Close Link
        if eventCode == '06.06' and status == '00':
            if DEBUG_MODE:
                print "eventType = 06.06"              
            print "Link closed "
            self.link_closed = True

        # Successful Parameter Change
        if eventCode == '06.07' and status == '00':
            if DEBUG_MODE:
                print "eventType = 06.07"              
            print "Parameters updated "
            response = packet_str[-14:-12]

            print "The response is " + response

            self.param_updated = True

        # # Get parameters
        # if eventCode == '06.7F' and status == '00':
        #     print "parameters received "
        #     self.param_retrieved = True

        # Parse RSSI response
        if packet_str[3:5] == '0E':
            if packet_str[18:20] == '00' and packet_str[27:29] != '7F': #7F is -129 RSSI - invalid
                rssi = int(packet_str[27:29], 16) - 256
                rssi_read = True
                rssi_success = True
                print "PARSING RSSI: %s" % rssi
            else:
                invalidRssiCount = 0
                if packet_str[27:29] == '7F':
                    invalidRssiCount += 1
                    if invalidRssiCount > MAX_INVALID_RSSI_COUNT:
                        rssi_invalid = True
                rssi_success = False
                rssi_read = True
                rssi = 0
            self.device.rssi = rssi
            self.is_rssi_retrieved = True

    def __pretty(self, hex_string, seperator=None):
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

    def print_orderedDict(self, dictionary):
        result = ""
        for idx, key in enumerate(dictionary.keys()):
            if dictionary[key]:
                #convert e.g. "data_len" -> "Data Len"
                title = ' '.join(key.split("_")).title()
                if isinstance(dictionary[key], list):
                    for idx2, item in enumerate(dictionary[key]):
                        result += "{0} ({1})\n".format(title, idx2)
                        result += self.print_orderedDict(dictionary[key][idx2])
                elif isinstance(dictionary[key], type(collections.OrderedDict())):
                    result += '{0}\n{1}'.format(title, self.print_orderedDict(dictionary[key]))
                else:
                    result += "{0:15}\t: {1}\n\t\t  ({2})\n".format(title, self.__pretty(dictionary[key][0], ':'), dictionary[key][1])
            else:
                result += "{0:15}\t: None".format(key)
        return result

    def print_output(self, (packet, dictionary)):
        result = self.print_orderedDict(dictionary)
        result += 'Dump:\n{0}\n'.format(self.__pretty(packet))
        if DEBUG_MODE:
            return result
        else:
            return ''

# Convert serial number to hex
def serialNumToHex(serial_num):
    serial_hex = ''
    b = 1
    for letter in serial_number:
        hex = letter.encode('hex')
        hex = hex.upper()
        serial_hex += hex
        if b < len(serial_number):
            serial_hex += '.'
        b += 1

# Convert hex to serial number
def hexToSerialNum(serial_hex):
    serial_num = ''
    serial_hex_list = serial_hex.split('.')
    for hex in serial_hex_list:
        letter = hex.decode('hex')
        letter = letter.upper()
        serial_num += str(letter)
    return serial_num

