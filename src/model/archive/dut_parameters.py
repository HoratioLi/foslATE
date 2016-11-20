'''
Created on 14-06-2013

@author: Trung Huynh
'''


import os
import time
import uuid


class DutParameters():
    '''
    This class contains all the DUT (Device Under Test) parameters
    '''
    def __init__(self, ate_id,
                 device_code_name,
                 device_type,
                 eb_id,
                 jlink_serial_number,
                 environment,
                 ieee=None):
        self.ate_id = ate_id
        self.code_name = device_code_name
        self.device_type = device_type
        self.ieee = ieee
        self.srfpc_args = [
            environment.srfpc_path,
            'S(' + eb_id + ')', # EB ID
            'EPV', # Erase, Program, Verify`
            'F=' + environment.cc2541_firmware_path, # path to .HEX file
            'KI(F=0)' + # Keep the IEEE MAC address currently on the chip
            'RI()' # Read out IEEE address
        ]
        self.srfpc_args_ieee = [
            environment.srfpc_path,
            'S(' + eb_id + ')', #EB ID
            'RI(F=0)'
        ]
        self.eac_args = [
            environment.eac_path,
            '--verify',
#             '--reset', # Uncomment this line to active reset on completion
            '--flash',
            environment.efm32_firmware_path,
            '--serialno',
            jlink_serial_number
        ]
        self.eac_args_unlock = [
            environment.eac_path,
            '--unlock'
        ]
        self.eac_args_final = [
            environment.eac_path,
            '--verify',
#             '--reset', # Uncomment this line to active reset on completion
            '--flash',
            environment.efm32_firmware_path_final,
            '--serialno',
            jlink_serial_number
        ]
        self.serial_number = str(uuid.uuid4())
        self.cc2541_firmware_name = os.path.basename(environment.cc2541_firmware_path)
        self.efm32_firmware_name = os.path.basename(environment.efm32_firmware_path)
        self.status = None # 0 for OK, positive number for ERRORS
        self.logCreationTime(time.time())

    def getCc2541FirmwareVersion(self):
        return self.cc2541_firmware_name

    def getEfm32FirmwareVersion(self):
        return self.efm32_firmware_name

    def logCreationTime(self, time):
        self.creation_time = time

    def logIeee(self, ieee):
        self.ieee = ieee

    def logUpdateTime(self, time):
        self.update_time = time

    def logStatus(self, status):
        self.status = status 

    def generateLogRecord(self):
        return dict(
            device_record = dict(
                ate_id = self.ate_id,
                serial_number = self.serial_number,
                code_name = self.code_name,
                device_type = self.device_type,
                hardware_revision = '',
                creation_time = self.creation_time,
                update_time = self.update_time,
                status = self.status,
                ieee = self.ieee
            )
        )

class FlashRecord():
    def __init__(self, ate_id,
                 serial_number,
                 command,
                 firmware_name,
                 revision,
                 target_component,
                 flashing_time,
                 returned_code=None,
                 stdout=None,
                 stderr=None,
                 ieee=None):
        self.ate_id = ate_id
        self.serial_number = serial_number
        self.command = command
        self.firmware_name = firmware_name
        self.revision = revision
        self.target_component = target_component
        self.flashing_time = flashing_time
        self.returned_code = returned_code
        self.stdout = stdout
        self.stderr = stderr
        self.ieee = ieee

    @staticmethod
    def from_dict(payload):
        return FlashRecord(
            ate_id=payload.get('ate_id'),
            serial_number=payload.get('serial_number'),
            command=payload.get('command'),
            firmware_name=payload.get('firmware_name'),
            revision=payload.get('revision'),
            target_component=payload.get('target_component'),
            flashing_time=payload.get('flashing_time'),
            returned_code=payload.get('returned_code'),
            stdout=payload.get('stdout'),
            stderr=payload.get('stderr'),
            ieee=payload.get('ieee')
        )

    def logReturnedCode(self, returned_code):
        self.returned_code = returned_code

    def generateLogRecord(self):
        return dict(
            flash_record = dict (
                ate_id = self.ate_id,
                serial_number = self.serial_number,
                command = self.command,
                firmware_name = self.firmware_name,
                revision = self.revision,
                target_component = self.target_component,
                flashing_time = self.flashing_time,
                returned_code = self.returned_code,
                stdout = self.stdout,
                stderr = self.stderr,
                ieee = self.ieee
            )
        )

class TestRecord():
    def __init__(self, serial_number,
                 ieee=None,
                 ate_id=None,
                 led_current=None,
                 low_power_current=None,
                 accelerometer_self_test=None,
                 lfxo=None,
                 rssi=None,
                 rssi_list=None,
                 invalid_rssi=None,
                 test_time=None,
                 sixLEDCurrent=None,
                 testFailures=None):
        self.serial_number = serial_number
        self.ieee = ieee
        self.ate_id = ate_id
        self.led_current = led_current
        self.low_power_current = low_power_current
        self.accelerometer_self_test = accelerometer_self_test
        self.lfxo = lfxo
        self.rssi = rssi
        self.rssi_list = rssi_list
        self.invalid_rssi = invalid_rssi
        self.test_time = test_time
        self.sixLEDCurrent = sixLEDCurrent
        self.testFailures = testFailures

    @staticmethod
    def from_dict(payload):
        return TestRecord(
            serial_number=payload.get('serial_number'),
            ieee=payload.get('ieee'),
            ate_id=payload.get('ate_id'),
            led_current=payload.get('led_current'),
            low_power_current=payload.get('low_power_current'),
            accelerometer_self_test=payload.get('accelerometer_self_test'),
            lfxo=payload.get('lfxo'),
            rssi=payload.get('rssi'),
            rssi_list=payload.get('rssi_list'),
            invalid_rssi=payload.get('invalid_rssi'),
            test_time=payload.get('test_time'),
            sixLEDCurrent=payload.get('sixLEDCurrent'),
            testFailures=payload.get('testFailures'),
        )

    def __logTestTime(self, test_time=None):
        if test_time:
            self.test_time = test_time
        else:
            self.test_time = time.time()

    def logLedCurrent(self, led_current):
        self.led_current = led_current
        self.__logTestTime()

    def logLowPowerCurrent(self, low_power_current):
        self.low_power_current = low_power_current
        self.__logTestTime()

    def logAccelerometerSelfTest(self, accelerometer_self_test):
        self.accelerometer_self_test = accelerometer_self_test
        self.__logTestTime()

    def logLfxo(self, lfxo):
        self.lfxo = lfxo
        self.__logTestTime()

    def logRssi(self, rssi):
        self.rssi = rssi
        self.__logTestTime()

    def logBluetoothAdvertisingCurrent(self, rssi_list):
        self.rssi_list = rssi_list
        self.__logTestTime()

    def logSixLEDCurrent(self, sixLEDCurrent):
        self.sixLEDCurrent = sixLEDCurrent
        self.__logTestTime()

    def logTestFailures(self, testFailures):
        self.testFailures = testFailures
        self.__logTestTime()

    def generateLogRecord(self):
        return dict(
            test_record = dict (
                serial_number=self.serial_number,
                ieee = self.ieee,
                ate_id = self.ate_id,
                led_current = self.led_current,
                low_power_current = self.low_power_current,
                accelerometer_self_test = self.accelerometer_self_test,
                lfxo = self.lfxo,
                rssi = self.rssi,
                rssi_list = self.rssi_list,
                invalid_rssi = self.invalid_rssi,
                test_time=self.test_time,
                sixLEDCurrent=self.sixLEDCurrent,
                testFailures=self.testFailures,
            )
        )
