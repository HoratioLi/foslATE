'''
Created on 09-16-2013

@author: Michael Akilian
'''
import json
import datetime
import time

class DeviceEncoder(json.JSONEncoder):
	def default(self, obj):
		# if isinstance(obj, Device):
		# 	return obj.__dict__	
		if isinstance(obj, StationTest):
			return obj.__dict__
		if isinstance(obj, IndividualTest):
			return obj.__dict__
		return json.JSONEncoder.default(self, obj)

class StationTestEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, StationTest):
			return obj.__dict__
		if isinstance(obj, IndividualTest):
			return obj.__dict__
		return json.JSONEncoder.default(self, obj)

class IndividualTestEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, IndividualTest):
			return obj.__dict__
		return json.JSONEncoder.default(self, obj)

class StationTest():
	def __init__(self, 
				 ateID = None, 
				 isPassed = None, 
				 scriptVersion = None, 
				 firmwareVersion = None,
				 tests = None,
				 date = None,
				 adict = None):
		if adict:
			self.__dict__.update(adict)
		else:
			self.ate_id = ateID
			self.is_passed = isPassed
			self.script_revision = scriptVersion
			self.firmware_revision = firmwareVersion
			self.individual_tests = tests
			self.date = date
		

	def jsonize(self):
		temp = {"station_tests":[self]}
		return json.dumps(temp, cls = StationTestEncoder)

class IndividualTest():
	def __init__(self, isPassed, timestamp):
		self.is_passed = isPassed
		self.timestamp = timestamp
		self.timestamp = time.mktime(datetime.datetime.utcnow().timetuple())
		self.name = ''

	def jsonize(self):
		return json.dumps(self, cls = IndividualTestEncoder)


#~~~~~~~~~~INDIVIDUAL TEST SUBCLASSES~~~~~~~~~~

class TimeoutTest(IndividualTest):
	name = 'Timeout Test'
	def __init__(self, isPassed=None, timestamp=None, adict=None, timeout=True):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.name = 'Timeout Test'


class SingleVoltageTest(IndividualTest):
	name = 'Single Voltage Test'
	def __init__(self, isPassed=None, timestamp=None, voltage=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.voltage = voltage
			self.name = 'Single Voltage Test'

class SingleCurrentTest(IndividualTest):
	name = 'Single Current Test'
	def __init__(self, isPassed=None, timestamp=None, current=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.current = current
			self.name = 'Single Current Test'

class MultipleCurrentTest(IndividualTest):
	name = "Multiple Current Test"
	def __init__(self, isPassed=None, timestamp=None,  currents=None, average=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.currents = currents
			self.average = average
			self.name = "Multiple Current Test"

class AccelSelfTest(IndividualTest):
	name = "Accel Self Test"
	def __init__(self, isPassed=None, timestamp=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.name = "Accel Self Test"

class RSSIValueTest(IndividualTest):
	name = "RSSI Value Test"
	def __init__(self, isPassed=None, timestamp=None, rssiValues=None, avgRssi=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.rssi_values = rssiValues
			self.average_rssi = avgRssi
			self.name = "RSSI Value Test"

class AverageRssiTest(IndividualTest):
	name = "Average RSSI Test"
	def __init__(self, isPassed=None, timestamp=None, rssiValues=None, average_rssi=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.average_rssi = average_rssi
			self.name = "Average RSSI Test"

class PerTest(IndividualTest):
	name = "Packet Error Rate Test"
	def __init__(self, isPassed=None, timestamp=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.name = "Packet Error Rate Test"

class FirmwareCheckTest(IndividualTest):
	name = "Firmware Check Test"
	def __init__(self, isPassed=None, timestamp=None,  expectedFW=None, fwVersion=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.expected_fw = expectedFW
			self.fw_version = fwVersion
			self.name = "Firmware Check Test"

class AccelZDataTest(IndividualTest):
	name = "Accelerometer Orientation Test"
	def __init__(self, isPassed=None, timestamp=None, zData=None, pinState=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.z_data = zData
			self.pin_state = pinState
			self.name = "Accelerometer Orientation Test"

class WriteSerialTest(IndividualTest):
	name = "Write Serial Test"
	def __init__(self, isPassed=None, timestamp=None, serialNumber=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.serial_number = serialNumber
			self.name = "Write Serial Test"

class ReadSerialTest(IndividualTest):
	name = "Read Serial Test"
	def __init__(self, isPassed=None, timestamp=None, serialToCheck=None, serialFromDevice=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.serial_to_check = serialToCheck
			self.serial_from_device = serialFromDevice
			self.name = "Read Serial Test"

class DefaultSNCheckTest(IndividualTest):
	name = "Default Serial Test"
	def __init__(self, isPassed=None, timestamp=None, serialNumber=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.serial_number = serialNumber
			self.name = "Default Serial Test"

class DuplicateSNTest(IndividualTest):
	name = "Duplicate Serial Number"
	def __init__(self, isPassed=None, timestamp=None,  serialNumber=None, serialNumberInternal=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.serial_number = serialNumber
			self.serial_number_internal = serialNumberInternal			
			self.name = "Duplicate Serial Number"

class RecentSyncTest(IndividualTest):
	name = "Recent Sync Test"
	def __init__(self, isPassed=None, timestamp=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.name = "Recent Sync Test"

class BatteryTest(IndividualTest):
	name = "Battery Test"
	def __init__(self, isPassed=None, timestamp=None, baseLoadDifference=None, baseVoltage=None, loadVoltage=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.baseLoadDifference = baseLoadDifference
			self.baseVoltage = baseVoltage
			self.loadVoltage = loadVoltage
			self.name = "Battery Test"

class BoostTest(IndividualTest):
	name = "Boost Test"
	def __init__(self, isPassed=None, timestamp=None, boostVoltage=None, noLoadVoltage=None, loadVoltage=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.boostVoltage = boostVoltage
			self.noLoadVoltage = noLoadVoltage
			self.loadVoltage = loadVoltage
			self.name = "Boost Test"

class CaptouchTest(IndividualTest):
	name = "Captouch Test"
	def __init__(self, isPassed=None, timestamp=None, captouchValue=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.captouchValue = captouchValue
			self.name = "Captouch Test"

class VibeBTTest(IndividualTest):
	name = "Vibe BT Test"
	def __init__(self, isPassed=None, timestamp=None, vibeValue=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.vibeValue = vibeValue
			self.name = "Vibe BT Test"

class CaptouchBTCalibration(IndividualTest):
	name = "Captouch BT Calibration"
	def __init__(self, isPassed=None, timestamp=None, modIdac=None, compIdac=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.modIdac = modIdac
			self.compIdac = compIdac
			self.name = "Captouch BT Calibration"

class DrvCalibration(IndividualTest):
	name = "DRV Calibration"
	def __init__(self, isPassed=None, timestamp=None, result=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.name = "DRV Calibration"

class CaptouchProgramming(IndividualTest):
	name = "Captouch Programming"
	def __init__(self, isPassed=None, timestamp=None, result=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.name = "Captouch Programming"
			self.result = result

class DrvPartIdTest(IndividualTest):
	name = "DRV Part ID Test"
	def __init__(self, isPassed=None, timestamp=None, result=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.name = "DRV Part ID Test"
			self.result = result

class RtcPartIdTest(IndividualTest):
	name = "RTC Part ID Test"
	def __init__(self, isPassed=None, timestamp=None, result=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.name = "RTC Part ID Test"
			self.result = result

class MagSelfTest(IndividualTest):
	name = "Mag self test"
	def __init__(self, isPassed=None, timestamp=None, result=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.name = "Mag self test"
			self.result = result

class LEDSelfTest(IndividualTest):
	name = "LED Self Test"
	def __init__(self, isPassed=None, timestamp=None, result=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.name = "LED Self Test"
			self.result = result

class PusherPushTest(IndividualTest):
	name = "Pusher Push Test"
	def __init__(self, isPassed=None, timestamp=None, result=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.name = "Pusher Push Test"
			self.result = result

class PusherReleaseTest(IndividualTest):
	name = "Pusher Release Test"
	def __init__(self, isPassed=None, timestamp=None, result=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.name = "Pusher Release Test"
			self.result = result

class VibeTest(IndividualTest):
	name = "Vibe Test"
	def __init__(self, isPassed=None, timestamp=None, vibeValue=None, magnitudeValue=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.vibeValue = vibeValue
			self.vibeMagnitude = magnitudeValue
			self.name = "Vibe Test"

class VibeBTMagnitudeTest(IndividualTest):
	name = "Vibe BT Magnitude Test"
	def __init__(self, isPassed=None, timestamp=None, magnitudeValue=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.vibeMagnitude = magnitudeValue
			self.name = "Vibe BT Magnitude Test"

class VibeBTCalibration(IndividualTest):
	name = "Vibe BT Calibration"
	def __init__(self, isPassed=None, timestamp=None, overVoltage=None, ratedVoltage=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.name = "Vibe BT Calibration"

class BTSetHandPositions(IndividualTest):
	name = "BT Set Hand Positions"
	def __init__(self, isPassed=None, timestamp=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.name = "BT Set Hand Positions"

class BTSetTime(IndividualTest):
	name = "BT Set Time"
	def __init__(self, isPassed=None, timestamp=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.name = "BT Set Time"

class AudioTest(IndividualTest):
	name = "Audio Test"
	def __init__(self, isPassed=None, timestamp=None, frequency=None, magnitude=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.frequency = frequency
			self.magnitude = magnitude
			self.name = "Audio Test"

class BatteryPlotTest(IndividualTest):
	name = "Battery Plot Test"
	def __init__(self, isPassed=None, timestamp=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.name = "Battery Plot Test"

class MacAddressTest(IndividualTest):
	name = "Read Mac Address Test"
	def __init__(self, isPassed=None, timestamp=None, macMasked=None, macRaw=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.macMasked = macMasked   	### Masked version of the mac - or'd with C in MSB
			self.macRaw = macRaw 			### Raw Mac value from device
			self.name = "Read Mac Address Test"

class LinkSerialInDBtest(IndividualTest):
	name = "Link Serial Number in DB Test"
	def __init__(self, isPassed=None, timestamp=None, serialNumber=None, serialNumberInternal=None, serialNumberSMT=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.serial_number = serialNumber
			self.serial_number_internal = serialNumberInternal
			self.serial_number_smt = serialNumberSMT
			self.name = "Link Serial Number in DB Test"

class ReadIEEEaddressTest(IndividualTest):
	name = "Read IEEE Address Test"
	def __init__(self, isPassed=None, timestamp=None, ieeeAddress=None, ieeeAddressSource=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.ieee_address = ieeeAddress
			self.ieee_address_source = ieeeAddressSource
			self.name = "Read IEEE Address Test"

class BluetoothConnectedTest(IndividualTest):
	name = "Bluetooth Connected Test"
	def __init__(self, isPassed=None, timestamp=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.name = "Bluetooth Connected Test"

class ResetViaBTtest(IndividualTest):
	name = "Reset via BT"
	def __init__(self, isPassed=None, timestamp=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.name = "Reset via BT"

class StoreGitCommitHash(IndividualTest):
	name = "Store Git Commit Hash"
	def __init__(self, isPassed=None, timestamp=None, gitCommitHash=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.git_commit_hash = gitCommitHash
			self.name = "Store Git Commit Hash"

class UploadedViaCronTest(IndividualTest):
	name = "Uploaded via Cron Test"
	def __init__(self, isPassed=None, timestamp=None, uploadedViaCron=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.uploaded_via_cron = uploadedViaCron
			self.name = "Uploaded via Cron Test"			

class McuProgramming(IndividualTest):
	name = 'MCU Programming'
	def __init__(self, isPassed=None, timestamp=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.name = 'MCU Programming'

class PogoPinTest(IndividualTest):
	name = 'Pogo Pin Test'
	def __init__(self, isPassed=None, timestamp=None, value=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.value = value
			self.name = 'Pogo Pin Test'

class usedInTLA(IndividualTest):
	name = "PCB used for TLA"
	def __init__(self, isPassed=None, timestamp=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.name = "PCB used for TLA"

class CrystalTest(IndividualTest):
	name = "CrystalTest"
	def __init__(self, isPassed=None, timestamp=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.name = "Crystal Test"

class CrystalCalibrationTest(IndividualTest):
	name = "Crystal Calibration Test"
	def __init__(self, isPassed=None, timestamp=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.name = "Crystal Calibration Test"
			
###############################################
# Deprecated
###############################################

class Device():
	def __init__(self, serial_number,	
				 ieee,
				 creation_time,
				 manufacturer):
		# DEVICE INFO
		self.ieee_address = ieee
		self.is_passed = False
		self.is_duplicated = False
		self.manufacturer = manufacturer 
		self.serial_number = serial_number

		# PHYSICALS
		self.physical = {
			"mechanical_revision":"",
			"pcb_revision":"",
			"pcba_revision":"",
			"color":"",
			"model_number":""
		}

		#STATION TESTS
		self.station_tests = []

	def addStationTest(self, test):
		#any logic needed here?
		self.station_tests.append(test)

	def getPhysicals(self):
		return physical

	def jsonize(self):
		temp = {"device":self}
		return json.dumps(temp, cls=DeviceEncoder)

	@staticmethod
	def from_dict(payload):
		return Device(
			serial_number=payload.get('serial_number'),
			ieee=payload.get('ieee'),
			creation_time=payload.get('creation_time'),
			manufacturer=payload.get('manufacturer'),
		)

class UnlockEFMTest(IndividualTest):
	name = 'UNLOCK EFM TEST'
	def __init__(self, isPassed=None, timestamp=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.name = 'UNLOCK EFM TEST'

class ProgramCCTest(IndividualTest):
	name = 'PROGRAM CC TEST'
	def __init__(self, isPassed=None, timestamp=None, ccFirmware=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.cc_fw = ccFirmware
			self.name = 'PROGRAM CC TEST'

class ProgramEFMTest(IndividualTest):
	name = 'PROGRAM EFM TEST'
	def __init__(self, isPassed=None, timestamp=None, efmTestFirmware=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp, )
			self.efm_test_fw = efmTestFirmware
			self.name = 'PROGRAM EFM TEST'

class MCUCurrentTest(IndividualTest):
	name = 'MCU CURRENT TEST'
	def __init__(self, isPassed=None, timestamp=None, mcuCurrent=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.mcuCurrent = mcuCurrent
			self.name = 'MCU CURRENT TEST'

class LEDCurrentTest(IndividualTest):
	name = 'LED CURRENT TEST'
	def __init__(self, isPassed=None, timestamp=None, ledCurrents=None, passes=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.ledCurrents = ledCurrents
			self.passes = passes
			self.name = 'LED CURRENT TEST'

class SixLEDCurrentTest(IndividualTest):
	name = 'SIX LED CURRENT TEST'
	def __init__(self, isPassed=None, timestamp=None, avgCurrent=None, allCurrent=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.avgCurrent = avgCurrent
			self.allCurrent = allCurrent
			self.name = 'SIX LED CURRENT TEST'

class LowPowerCurrentTest(IndividualTest):
	name = "LOW POWER CURRENT TEST"
	def __init__(self, isPassed=None, timestamp=None, avgCurrent=None, allCurrent=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.avgCurrent = avgCurrent
			self.allCurrent = allCurrent
			self.name = "LOW POWER CURRENT TEST"

class FinalFlashTest(IndividualTest):
	name = "FINAL FLASH TEST"
	def __init__(self, isPassed=None, timestamp=None, finalFW=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.prod_fw = finalFW
			self.name = "FINAL FLASH TEST"

class InvalidRSSITest(IndividualTest):
	name = "INVALID RSSI TEST"
	def __init__(self, isPassed=None, timestamp=None, invalidCount=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.rssi_invalid_count = invalidCount
			self.name = "INVALID RSSI TEST"

class StationOneTimeoutTest(IndividualTest):
	name = "STATION ONE TIMEOUT TEST"
	def __init__(self, isPassed=None, timestamp=None, timeouts=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.timeouts = timeouts
			self.name = "STATION ONE TIMEOUT TEST"


class ScanTest(IndividualTest):
	name = "SCAN TEST"
	def __init__(self, isPassed=None, timestamp=None, rssi=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.rssi = rssi
			self.name = "SCAN TEST"

class AdvSamplesTest(IndividualTest):
	name = "ADV SAMPLES TEST"
	def __init__(self, isPassed=None, timestamp=None,  numSamples=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.adv_samples = numSamples
			self.name = "ADV SAMPLES TEST"

class ConfirmLEDCurrentTest(IndividualTest):
	name = "CONFIRM LED CURRENT TEST"
	def __init__(self, isPassed=None, timestamp=None,  confirm=None, average=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.confirm_current = confirm
			self.average = average
			self.name = "CONFIRM LED CURRENT TEST"

class SNMismatchTest(IndividualTest):
	name = "SERIAL MISMATCH TEST"
	def __init__(self, isPassed=None, timestamp=None,  initialSerial=None, finalSerial=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.initial_serial = initialSerial
			self.final_serial = finalSerial
			self.name = "SERIAL MISMATCH TEST"

class StationTwoTimeoutTest(IndividualTest):
	name = "STATION TWO TIMEOUT TEST"
	def __init__(self, isPassed=None, timestamp=None,  timeouts=None, adict=None):
		if adict:
			self.__dict__.update(adict)
		else:
			IndividualTest.__init__(self, isPassed, timestamp)
			self.timeouts = timeouts
			self.name = "STATION TWO TIMEOUT TEST"
