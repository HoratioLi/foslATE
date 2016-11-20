#!/usr/bin/env python
'''
Created on 2014-07-07

@author: Rachel Kalmar
'''

import json
import datetime
import time
from constants import *
from device import *

class BLEdeviceEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, BLEdevice):
            return obj.__dict__
        if isinstance(obj, StationTest):
            return obj.__dict__
        if isinstance(obj, IndividualTest):
            return obj.__dict__
        return json.JSONEncoder.default(self, obj)

class BLEdevice():
    def __init__(self, 
                 serial_number, 
                 serial_number_internal,
                 serial_number_smt,
                 ieee,
                 ieeeString,
                 rssi):

        # DEVICE INFO
        self.ieee_address = ieee
        self.ieee_string = ieeeString
        self.manufacturer = MANUFACTURER_NAME
        self.serial_number = serial_number
        self.serial_number_internal = serial_number_internal
        self.serial_number_smt = serial_number_smt
        self.created_at = time.mktime(datetime.datetime.utcnow().timetuple())
        self.rssi = rssi
        self.is_passed = False
        self.is_duplicated = False    
        self.fw_rev = None   
        self.accel_value = None
        self.battery_base_value = None         
        self.battery_load_value = None 
        self.captouch_value = None   
        self.vibe_value = None 
        self.open_leds = None
        self.mag_self_test = 0    
        self.captouch_mod_idac = None
        self.captouch_comp_idac = None    
        self.vibe_magnitude = 0 
        self.vibe_calibration_result = 0  
        self.average_rssi = 0    
        self.total_packets_received = 0
        self.total_good_packets = 0
        self.total_crc_errors = 0
        self.total_len_errors = 0
        self.total_mic_errors = 0
        self.total_nesn_errors = 0
        self.total_sn_errors = 0
        self.total_sync_errors = 0
        self.total_type_errors = 0
        self.total_overflow_errors = 0 
        self.device_time = 0   
        self.current_hand_positions = None
        self.no_load_voltage = 0
        self.load_voltage = 0
        self.boost_voltage = 0
    
        # PHYSICALS
        self.physical = {
            "mechanical_revision":MECHANICAL_REVISION,
            "pcb_revision":PCB_REVISION,
            "pcba_revision":PCBA_REVISION,
            "color":DEVICE_COLOR,
            "ledColor":LED_COLOR,
            "model_number":MODEL_NUMBER
        }

        # STATION TESTS
        self.station_tests = []     

    def getIEEEaddress(self):
        return self.ieee_address

    def setIEEEaddress(self, ieee):
        self.ieee_address = ieee
        return self.ieee_address

    def getIEEEstring(self):
        return self.ieee_string

    def setIEEEstring(self, ieee):
        self.ieee_string = ieee
        return self.ieee_string

    def getSerialNumber(self):
        return self.serial_number

    def setSerialNumber(self, serial_number):
        self.serial_number = serial_number
        return self.serial_number

    def getRSSI(self):
        return self.rssi

    def getFWrev(self):
        return self.fw_rev

    def setFWrev(self, fw_rev):
        self.fw_rev = fw_rev
        return self.fw_rev
 
    def getAccelValue(self):
        return self.accel_value

    def setAccelValue(self, accel_value):
        self.accel_value = accel_value
        return self.accel_value

    def getBatteryBaseValue(self):
        return self.battery_base_value      

    def setBatteryBaseValue(self, battery_base_value):
        self.battery_base_value = battery_base_value
        return self.battery_base_value              

    def getBatteryLoadValue(self):
        return self.battery_load_value      

    def setBatteryLoadValue(self, battery_load_value):
        self.battery_load_value = battery_load_value
        return self.battery_load_value   

    def addStationTest(self, test):
        self.station_tests.append(test)
        
    def getPhysicals(self):
        return physical

    def getCaptouchValue(self):
        return self.captouch_value

    def setCaptouchValue(self, captouch_value):
        self.captouch_value = captouch_value

    def getVibeValue(self):
        return self.vibe_value

    def setVibeValue(self, vibe_value):
        self.vibe_value = vibe_value

    def getVibeMagnitude(self):
        return self.vibe_magnitude

    def setVibeMagnitude(self, vibe_magnitude):
        self.vibe_magnitude = vibe_magnitude

    def getOpenLeds(self):
        return self.open_leds

    def setOpenLeds(self, open_leds):
        self.open_leds = open_leds

    def getMagResult(self):
        return self.mag_self_test

    def setMagResult(self, mag_self_test):
        self.mag_self_test = mag_self_test

    def getCaptouchModIdacResult(self):
        return self.captouch_mod_idac

    def setCaptouchModIdacResult(self, captouch_mod_idac):
        self.captouch_mod_idac = captouch_mod_idac

    def getCaptouchCompIdacResult(self):
        return self.captouch_comp_idac

    def setCaptouchCompIdacResult(self, captouch_comp_idac):
        self.captouch_comp_idac = captouch_comp_idac

    def getVibeCalibrationResult(self):
        return self.vibe_calibration_result

    def setVibeCalibrationResult(self, vibe_calibration_result):
        self.vibe_calibration_result = vibe_calibration_result

    def getAverageRSSI(self):
        return self.average_rssi

    def setAverageRSSI(self, average_rssi):
        self.average_rssi = average_rssi

    def getTotalPacketsReceived(self):
        return self.total_packets_received

    def setTotalPacketsReceived(self, total_packets_received):
        self.total_packets_received = total_packets_received

    def getTotalGoodPackets(self):
        return self.total_good_packets

    def setTotalGoodPackets(self, total_good_packets):
        self.total_good_packets = total_good_packets   

    def getTotalCrcErrors(self):
        return self.total_crc_errors

    def setTotalCrcErrors(self, total_crc_errors):
        self.total_crc_errors = total_crc_errors 

    def getTotalLenErrors(self):
        return self.total_len_errors

    def setTotalLenErrors(self, total_len_errors):
        self.total_len_errors = total_len_errors 

    def getTotalMicErrors(self):
        return self.total_mic_errors

    def setTotalMicErrors(self, total_mic_errors):
        self.total_mic_errors = total_mic_errors 

    def getTotalNesnErrors(self):
        return self.total_nesn_errors

    def setTotalNesnErrors(self, total_nesn_errors):
        self.total_nesn_errors = total_nesn_errors 

    def getTotalSnErrors(self):
        return self.total_sn_errors

    def setTotalSnErrors(self, total_sn_errors):
        self.total_sn_errors = total_sn_errors 

    def getTotalSyncErrors(self):
        return self.total_sync_errors

    def setTotalSyncErrors(self, total_sync_errors):
        self.total_sync_errors = total_sync_errors 

    def getTotalTypeErrors(self):
        return self.total_type_errors

    def setTotalTypeErrors(self, total_type_errors):
        self.total_type_errors = total_type_errors 

    def getTotalOverflowErrors(self):
        return self.total_overflow_errors

    def setTotalOverflowErrors(self, total_overflow_errors):
        self.total_overflow_errors = total_overflow_errors 

    def getDeviceTime(self):
        return self.device_time

    def setDeviceTime(self, device_time):
        self.device_time = device_time

    def getCurrentHandPositions(self):
        return self.current_hand_positions

    def setCurrentHandPositions(self, current_hand_positions):
        self.current_hand_positions = current_hand_positions

    def jsonize(self):
        temp = {"device":self}
        return json.dumps(temp, cls=BLEdeviceEncoder)

    @staticmethod
    def from_dict(payload):
        return BLEdevice(
            serial_number=payload.get('serial_number'),
            serial_number_internal=payload.get('serial_number_internal'),
            serial_number_smt=payload.get('serial_number_smt'),            
            ieee=payload.get('ieee'),
            ieeeString=payload.get('ieee_string'),
            rssi=payload.get('rssi'),
        )


