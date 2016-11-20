import sys
import os
import ast
from itertools import izip
from model.device import Device
from model.device import *
import MDapi
import time
import threading
import Queue
from Queue import Queue
import urllib2
import time
import datetime

MASTER_LOG_PATH = '/Users/akilian/ShineProduction/src/FULL_LOGS/'
MFG_LOGS_PATH = '/Users/akilian/Dropbox/MisfitSharedHWScience/Production/not_imported_to_mfg_db/'

PREFIX = 'logs_'
ATE_PREFIX = 'ate_'
STATION_1 = 'test.log'
STATION_1_DEVICE = 'device.log'
STATION_2 = 'serial.log'
formats = []
concurrent = 10
q = Queue(20)


debug_station1_lock = threading.Lock()
debug_station2_lock = threading.Lock()

station_1_formats = {
						'log_format_1':['bluetooth_advertising_current', 'accelerometer_self_test', 'lfxo', 'led_current', 'rssi', 'ieee', 'ate_id', 'low_power_current'], #for these two I could grab the corresponding status.log file?
						'log_format_2':['test_time', 'bluetooth_advertising_current', 'ieee', 'lfxo', 'led_current', 'serial_number', 'rssi', 'accelerometer_self_test', 'ate_id', 'low_power_current'], #for these two I could grab the corresponding status.log file?
						'log_format_3':['test_time', 'bluetooth_advertising_current', 'testFailures', 'ieee', 'sixLEDCurrent', 'lfxo', 'led_current', 'serial_number', 'rssi', 'accelerometer_self_test', 'ate_id', 'low_power_current'],
						'log_format_4':['test_time', 'testFailures', 'ieee', 'sixLEDCurrent', 'lfxo', 'led_current', 'rssi', 'serial_number', 'rssi_list', 'accelerometer_self_test', 'ate_id', 'low_power_current'],
						'log_format_5':['test_time', 'testFailures', 'ieee', 'sixLEDCurrent', 'lfxo', 'led_current', 'rssi', 'serial_number', 'rssi_list', 'accelerometer_self_test', 'invalid_rssi', 'ate_id', 'low_power_current']
					}

station_2_formats = {
						'log_format_1':['rssi', 'serial', 'ieee', 'low_power_current'], 
						'log_format_2':['rssi', 'serial', 'z_data', 'ieee', 'low_power_current'], 
						'log_format_3':['shine_serial', 'initial_shine_sn', 'initial_current', 'serial_qr', 'rssi', 'z_data', 'failures', 'fw_rev', 'ieee', 'low_power_current'],
						'log_format_4':['shine_serial', 'average_accel_current', 'initial_shine_sn', 'initial_current', 'serial_qr', 'rssi', 'z_data', 'accel_current', 'failures', 'fw_rev', 'ieee', 'low_power_current'],
						'log_format_5':['shine_serial', 'average_accel_current', 'initial_shine_sn', 'initial_current', 'serial_qr', 'rssi', 'z_data', 'accel_current', 'failures', 'fw_rev', 'ieee', 'ate_id', 'low_power_current'],
						'log_format_6':['shine_serial', 'average_accel_current', 'initial_shine_sn', 'timeouts', 'serial_qr', 'average_operating_current', 'z_data', 'accel_current', 'operating_current', 'fw_rev', 'rssi', 'failures', 'ieee', 'ate_id']
					}

colorMap = {
			'A':'GRAY', 
			'B':'BLACK', 
			'F':'RED', 
			'G':'TOPAZ', 
			'H':'CHAMPAGNE', 
			}

########################################################
#CREATE MASTER LOG FILES
########################################################
def build_master_log_files():
	##################################################
	#COLLECT ALL STATION ONE AND STATION TWO LOG FILES
	##################################################
	folds = []
	for folders in os.listdir(MFG_LOGS_PATH):
		if PREFIX in folders:
			folds.append(folders)

	ateFolders = []
	for each in folds:
		for sub in os.listdir(MFG_LOGS_PATH+each):
			if ATE_PREFIX in sub:
				ateFolders.append(MFG_LOGS_PATH + each + '/' + sub)

	station_1_log_files = []
	station_2_log_files = []

	station_1_new_log_files = []

	for each in ateFolders:
		for log in os.listdir(each):
			if STATION_1_DEVICE == log:
				if not STATION_1 in os.listdir(each):
					station_1_new_log_files.append(str(each + '/' + str(STATION_1_DEVICE)))
				else:
					station_1_log_files.append((str(each + '/' + STATION_1), str(each + '/' + str(STATION_1_DEVICE))))
			if STATION_2 == log:
				station_2_log_files.append(each + '/' + log)

	#######################################################
	#BUILD MASTER STATION ONE FILE
	#######################################################
	master_test_file = open(MASTER_LOG_PATH + STATION_1, 'w')
	master_device_file = open(MASTER_LOG_PATH + STATION_1_DEVICE, 'w')
	station_1_hashed_entries = []

	for each in station_1_log_files:
		for testLine, deviceLine in izip(open(each[0]), open(each[1])):
			dictionaryTest = ast.literal_eval(testLine)
			dictionaryDevice = ast.literal_eval(deviceLine)
			hashed = hash(deviceLine)
			if hashed not in station_1_hashed_entries:
				station_1_hashed_entries.append(hashed)
				if dictionaryTest['ieee'] and dictionaryDevice['ieee']:
					if dictionaryTest['ieee'] == dictionaryDevice['ieee']:
						master_device_file.write(deviceLine)
						master_test_file.write(testLine)
					else:
						pass
				else:
					pass
			else:
				pass

	########################################################
	#BUILD NEW MASTER STATION ONE FILE
	########################################################
	new_hashed_entreies = []
	master_new_device_file = open(MASTER_LOG_PATH + 'device_new.log', 'w')

	for each in station_1_new_log_files:
		newDeviceFile = open(each, 'r')
		for deviceLine in newDeviceFile.readlines():
			dictionaryDevice = ast.literal_eval(deviceLine)
			hashed = hash(deviceLine)
			if hashed not in new_hashed_entreies:
				new_hashed_entreies.append(hashed)
				if ('test_begun' in dictionaryDevice.keys() and dictionaryDevice['test_begun'] == True) or ('test_began' in dictionaryDevice.keys() and dictionaryDevice['test_began'] == True): #CHANGE THIS BACK!
					if dictionaryDevice['ieee_read'] == True:
						master_new_device_file.write(deviceLine)

	########################################################
	#BUILD MASTER STATION TWO FILE
	########################################################
	master_serial_file = open(MASTER_LOG_PATH + STATION_2, 'w')
	station_2_hashed_entries = []
	
	for each in station_2_log_files:
		testFile = open(each, 'r')
		for testLine in testFile.readlines():
			dictionaryTest = ast.literal_eval(testLine)
			hashed = hash(testLine)
			if hashed not in station_2_hashed_entries:
				station_2_hashed_entries.append(hashed)
				if dictionaryTest['ieee']:
					master_serial_file.write(testLine)
				else:
					pass
			else:
				pass


def buildBatchQueries():
	master_test_file = MASTER_LOG_PATH + STATION_1
	master_device_file = MASTER_LOG_PATH + STATION_1_DEVICE
	master_serial_file = MASTER_LOG_PATH + 'serial.log'
	testFile = open(master_serial_file, 'r')

	ieeeDictionary = {}
	print "START: " + str(datetime.datetime.now())

	#process logs
	#build dictionary (key = ieee, value = list of all entries across log)
	for testLine, deviceLine in izip(open(master_test_file), open(master_device_file)):
		dictionaryTest = stringToDictionary(testLine)
		dictionaryDevice = stringToDictionary(deviceLine)
		if dictionaryTest['ieee'] and dictionaryDevice['ieee']:
			ieeeValue = dictionaryTest['ieee'] 
			if ieeeValue not in ieeeDictionary:
				ieeeDictionary[ieeeValue] = {'1':list(), '2':list()}
			ieeeDictionary[ieeeValue]['1'].append((testLine, deviceLine))
	
	for testLine in testFile.readlines():
		dictionaryTest = stringToDictionary(testLine)
		if dictionaryTest['ieee']:
			ieeeValue = dictionaryTest['ieee']
			if ieeeValue not in ieeeDictionary:
				ieeeDictionary[ieeeValue] = {'1':list(), '2':list()}
			ieeeDictionary[ieeeValue]['2'].append(testLine)

	print len(ieeeDictionary)
	print "IEEE DICTIONARY BUILT: " + str(datetime.datetime.now())

	master_list = []
	#for each IEEE in dictionary
	for key in ieeeDictionary.keys():
		#create misfit device
		md = Device(serial_number="", ieee=key, creation_time="", manufacturer="MisfitVS")
		md.physical['mechanical_revision'] = "1.0"
		md.physical['pcb_revision'] = "0.9"
		md.physical['pcba_revision'] = "0.9"
		md.physical['color'] = "TBD"
		md.physical['model_number'] = "TBD"
		
		station1_entries = ieeeDictionary[key]['1']
		station2_entries = ieeeDictionary[key]['2']

		for each in station1_entries:
			dict1 = ast.literal_eval(each[0])
			dict2 = ast.literal_eval(each[1])
			test = createStation1TestForEntry(dict1, dict2)
			md.addStationTest(test)
		
		for each in station2_entries:
			dict1 = ast.literal_eval(each)
			test = createStation2TestForEntry(dict1)
			if len(station1_entries) > 0:
				test.date = station1_entries[0].date
			md.addStationTest(test)
			if test.is_passed: #if a station 2 passed, we update everything.
				serial = getSerial(dict1)
				(color, model_number) = lookupPhysicalsForSerial(serial)
				md.physical['color'] = color
				md.physical['model_number'] = model_number
				md.serial_number = serial
				md.is_passed = True #defaults to false

		#append device to master device list.
		master_list.append(md)

	print len(master_list)
	print "MISFIT DEVICE LIST BUILT: " + str(datetime.datetime.now())

	#DUPLICATE DETECTION
	serialDictionary = {}
	for md in master_list:
		if md.serial_number != '':
			if md.serial_number not in serialDictionary:
				serialDictionary[md.serial_number] = list()
				serialDictionary[md.serial_number].append(md)
			else:
				serialDictionary[md.serial_number].append(md)
				for each in serialDictionary[md.serial_number]:
					each.is_duplicated = True
					print "duplicate: " + str(md.serial_number)

	print len(serialDictionary)
	print "DUPLICATE DETECTION COMPLETED: " + str(datetime.datetime.now())
	
	#BATCH POSTINGS
	i = 0
	while i < len(master_list):
		a = 0
		batch_device_list = []
		while a < 250 and i < len(master_list):
			batch_device_list.append(master_list[i])
			i+=1
			a+=1
		result = postBatchDeviceList(batch_device_list)
		print str(i)
		print str(result)
		if result != '{}':
			logFailedBatchEntry(batch_device_list)

def postFailedBatchEntries():
	batch_fail_file = MASTER_LOG_PATH + 'failed_batch.log'
	failedFile = open(batch_fail_file, 'r')
	stringVersion = failedFile.read()
	lines = stringVersion.replace('{"devices"', '\n{"devices"')
	lines = lines.split('\n')
	for line in lines:
		if '{"devices"' in line:
			batchJSON = line
			result = MDapi.misfitProductionPostBatchMisfitDevice(batchJSON)
			print str(result)
			if result != '{}':
				print "fail"
				#logFailedBatchEntry(batch_device_list)

def logFailedBatchEntry(device_list):
	temp = {"devices":device_list}
	batchJSON = json.dumps(temp, cls=DeviceEncoder)
	failFilePath = MASTER_LOG_PATH + 'failed_batch.log'
	failFile = open(failFilePath, 'a')
	failFile.write(str(batchJSON))
	failFile.close()

########################################################
#PROCESS AND IMPORT ALL STATION ONE ENTRIES TO DATABASE
########################################################
#ONLY RUN THIS ON NEW LOG FORMATS
def CRON_processAndUpdateStation1Log():
	log_file = '.\log_unposted\device.log'
	testFile = open(log_file, 'r')

	#READ FORM LOG FILE
	station_1_entries = []
	for testLine in testFile.readlines():
		station_1_entries.append(testLine)
	testFile.close()

	#process and update all entries
	new_station_1_entries = []
	for each in station_1_entries:
		result = CRON_stationOneEntryToDB(each)
		print result
		if result:
			new_station_1_entries.append(result)

	#open temporary unposted log and posted log file
	new_log_file = '.\log_unposted\device_temp.log'
	newLogFile = open(new_log_file, 'w')

	posted_log_file = '.\log_posted\device.log'
	postedFile = open(posted_log_file, 'a') 

	#put updated entries where they belong
	for each in new_station_1_entries:
		if each['mfg_db_post_success'] == True:
			postedFile.write(str(each) + '\n')
		else:
			newLogFile.write(str(each) + '\n')
			
	
	#close file
	newLogFile.close()
	postedFile.close()

	#remove old file
	for filename in os.listdir(".\log_unposted"):
		if filename == 'device.log':
			os.remove('.\log_unposted\\' + filename)

	#rename temp file to regular
	for filename in os.listdir(".\log_unposted"):
		if filename == 'device_temp.log':
			os.rename('.\log_unposted\\'+filename, '.\log_unposted\device.log')

def CRON_processAndUpdateStation1Log_MAC():
	log_file = './log_unposted/device.log'
	testFile = open(log_file, 'r')

	#READ FORM LOG FILE
	station_1_entries = []
	for testLine in testFile.readlines():
		station_1_entries.append(testLine)
	testFile.close()

	#process and update all entries
	new_station_1_entries = []
	for each in station_1_entries:
		result = CRON_stationOneEntryToDB(each)
		if result:
			new_station_1_entries.append(result)

	#open temporary unposted log and posted log file
	new_log_file = './log_unposted/device_temp.log'
	newLogFile = open(new_log_file, 'w')

	posted_log_file = './log_posted/device.log'
	postedFile = open(posted_log_file, 'a') 

	#put updated entries where they belong
	for each in new_station_1_entries:
		if each['mfg_db_post_success'] == True:
			postedFile.write(str(each) + '\n')
		else:
			newLogFile.write(str(each) + '\n')
			
	
	#close file
	newLogFile.close()
	postedFile.close()

	#remove old file
	for filename in os.listdir("./log_unposted"):
		if filename == 'device.log':
			os.remove('./log_unposted/' + filename)

	#rename temp file to regular
	for filename in os.listdir("./log_unposted"):
		if filename == 'device_temp.log':
			os.rename('./log_unposted/'+filename, './log_unposted/device.log')

def CRON_stationOneEntryToDB(entry):
	check = ast.literal_eval(entry)
	
	if ('test_began' in check.keys() and check['test_began'] == True) or ('test_begun' in check.keys() and check['test_begun'] == True):
		dictionaryTest = stringToDictionary(entry)

		if 'station_one_log_format' in dictionaryTest:
			return postNewStationOneLogFormat(dictionaryTest, False)

def processStationOneEntries():
	while True:
		(testLine, deviceLine) = q.get(True, None)
		stationOneEntryToDB(testLine, deviceLine)
		q.task_done()

def station_one_failed_daemon_import():
	master_failed_file = MASTER_LOG_PATH + 'failed_station1.log'

	count = 0
	#START 'consumer' threads that process station one queries

	failedFile = open(master_failed_file, 'r')
	for i in range(concurrent):
		t = threading.Thread(target=processStationOneEntries)
		t.daemon = True
		t.start()

	stringVersion = failedFile.read()
	lines = stringVersion.replace('\'}', '\'}\n')
	lines = lines.split('\n')
	#start putting station one entries on the queue to be consumed by the 400 station one 'consumer' threads
	for line in lines:
		if len(line) > 10:
			diction = ast.literal_eval(line)
			
			if diction['status'] != 'no_ieee':
				print str(count)
				count += 1
				q.put((diction['testLine'], diction['deviceLine']), True, None)
	q.join()

def station_one_daemon_import():
	master_test_file = MASTER_LOG_PATH + STATION_1
	master_device_file = MASTER_LOG_PATH + STATION_1_DEVICE

	master_failed_file = MASTER_LOG_PATH + 'failed_station1.log'
	
	count = 0
	#START 'consumer' threads that process station one queries
	for i in range(concurrent):
		t = threading.Thread(target=processStationOneEntries)
		t.daemon = True
		t.start()

	#start putting station one entries on the queue to be consumed by the 400 station one 'consumer' threads
	for testLine, deviceLine in izip(open(master_test_file), open(master_device_file)):
		count += 1
		print str(count)
		q.put((testLine, deviceLine), True, None)
	q.join()

def stationOneEntryToDB(testLine, deviceLine):
	dictionaryDevice = stringToDictionary(deviceLine)

	if 'station_one_log_format' in dictionaryDevice:
		postNewStationOneLogFormat(dictionaryDevice, True)
	else:
		postOldStationOneLogFormat(testLine, deviceLine)

#PARSES log_format_1 to log_format_5
def postOldStationOneLogFormat(testLine, deviceLine):
	dictionaryTest = stringToDictionary(testLine)
	dictionaryDevice = stringToDictionary(deviceLine)

	status = ''
	status2 = ''
	failed = True
	tries = 0

	#TRY POSTING THIS ENTRY UP TO 5 TIMES
	if dictionaryTest['ieee'] and dictionaryDevice['ieee']:
		while tries < 5 and failed:
			failed = False
			status = addStation1TestToDevice(dictionaryTest, dictionaryDevice)
			if status == '400': #doesn't exist in DB, so create it
				status2 = createMisfitDeviceWithStation1Test(dictionaryTest, dictionaryDevice)
			
			if (status != '{}' and status != '400') or (status == '400' and status2 != '{}'):
				print "~~ FAILED STATION ONE ENTRY ~~"
				print status
				print status2
				failed = True
				tries += 1

		#IF IT FAILED 5 TIMES -> LOG IT TO FAIL FILE
		if tries == 5:
			print "LOGGING ENTRY TO FAIL LOG"
			logFailedStationOneEntry(testLine, deviceLine, status, status2)
	else:
		print "LOGGING ENTRY TO FAIL LOG"
		logFailedStationOneEntry(testLine, deviceLine, 'no_ieee', 'no_ieee')

#PARSES log_format_7
def postNewStationOneLogFormat(device, log):
	if device['mfg_db_post_success'] == False:
		if device['ieee_read'] == True:
			if device['station_test']:
				stationTestDict = device['station_test']
				ieee = device['ieee']
				date = stationTestDict['date']
				#SERIALIZE DICTIONARY INTO StationTest object
				stationTest = StationTest(adict=stationTestDict)
				stationTest.individual_tests = create(adict=stationTestDict)

				tries = 0
				status = ''
				status2 = ''
				failed = True

				while tries < 5 and failed:
					failed = False
					status = MDapi.misfitProductionPostStationTestForDevice(ieee, stationTest.jsonize())
					if status == '400': #doesn't exist in DB, so create it
						md = Device("", ieee, date, "MisfitVS")
						md.physical['mechanical_revision'] = "1.0"
						md.physical['pcb_revision'] = "0.9"
						md.physical['pcba_revision'] = "0.9"
						md.physical['color'] = "TBD"
						md.physical['model_number'] = "TBD"
						md.addStationTest(stationTest)
						mdJSON = md.jsonize()
						status2 = MDapi.misfitProductionPostMisfitDevice(mdJSON)
					
					if (status != '{}' and status != '400') or (status == '400' and status2 != '{}'):
						failed = True
						tries += 1

				#IF IT FAILED 5 TIMES -> LOG IT TO FAIL FILE
				if log:
					if tries == 5:
						print "LOGGING ENTRY TO FAIL LOG"
						logFailedStationOneEntry(device, status, status2)
				else:
					if tries == 5:
						device['mfg_db_post_success'] = False
					else:
						device['mfg_db_post_success'] = True
					return device
	return device

#THIS NEEDS TO BE THREAD SAFE
def logFailedStationOneEntry(testLine, deviceLine, status, status2):
	debug_station1_lock.acquire()
	print "LOGGING STATION ONE FAIL TO HTTP POST"

	logger = {'testLine':testLine, 'deviceLine':deviceLine, 'status':status, 'status2':status2}

	failFilePath = MASTER_LOG_PATH + 'failed_failed_station1.log'
	
	fail1File = open(failFilePath, 'a')
	fail1File.write(str(logger))
	fail1File.close()
	
	print "DONE LOGGING STATION ONE FAIL TO HTTP POST"
	debug_station1_lock.release()

########################################################
#PROCESS AND IMPORT ALL STATION TWO ENTRIES TO DATABASE
########################################################

#ONLY RUN THIS ON NEW LOG FORMATS
def CRON_processAndUpdateStation2Log():
	log_file = '.\log_unposted\serial.log'
	testFile = open(log_file, 'r')

	#READ FORM LOG FILE
	station_2_entries = []
	for testLine in testFile.readlines():
		station_2_entries.append(testLine)
	testFile.close()

	#PROCESS AND UPDATE ENTRIES IN MEMORY
	new_station_2_entries = []
	for each in station_2_entries:
		result = CRON_stationTwoEntryToDB(each)
		print result
		if result:
			new_station_2_entries.append(result)

	#write to temp file or posted file
	new_log_file = '.\log_unposted\serial_temp.log'
	newLogFile = open(new_log_file, 'w')

	posted_log_file = '.\log_posted\serial.log'
	postedLog = open(posted_log_file, 'a')

	for each in new_station_2_entries:
		if each['mfg_db_update_success'] == True and each['mfg_db_post_success'] == True:
			postedLog.write(str(each) + '\n')
		else:
			newLogFile.write(str(each) + '\n')
			

	postedLog.close()
	newLogFile.close()

	#remove old file
	for filename in os.listdir(".\log_unposted"):
		if filename == 'serial.log':
			os.remove('.\log_unposted\\' + filename)

	#rename temp file to regular
	for filename in os.listdir(".\log_unposted"):
		if filename == 'serial_temp.log':
			os.rename('.\log_unposted\\'+filename, '.\log_unposted\serial.log')

def CRON_stationTwoEntryToDB(entry):
	dictionaryTest = stringToDictionary(entry)

	if 'station_two_log_format' in dictionaryTest:
		return postNewStationTwoLogFormat(dictionaryTest, False)

def processStationTwoEntries():
	while True:
		testLine = q.get(True, None)
		stationTwoEntryToDB(testLine)
		q.task_done()

def station_two_daemon_import():
	master_serial_file = MASTER_LOG_PATH + 'serial.log'
	testFile = open(master_serial_file, 'r')

	count = 0
	#START 400 'consumer' threads that process station one queries
	for i in range(concurrent):
		t = threading.Thread(target=processStationTwoEntries)
		t.daemon = True
		t.start()

	#start putting station one entries on the queue to be consumed by the 400 station one 'consumer' threads
	for testLine in testFile.readlines():
		count += 1
		print str(count)
		q.put(testLine, True, None)
	q.join()

def stationTwoEntryToDB(testLine):
	dictionaryTest = stringToDictionary(testLine)

	if 'station_two_log_format' in dictionaryTest:
		postNewStationTwoLogFormat(dictionaryTest, True)
	else:
		postOldStationTwoLogFormat(testLine)


#PARSES log_format_1 to log_format_6
def postOldStationTwoLogFormat(testLine):
	dictionaryTest = stringToDictionary(testLine)

	tries = 0
	status = ''
	status2 = ''
	status3 = ''
	failed = True

	#TRY POSTING UP TO 5 TIMES
	if dictionaryTest['ieee']:
		while tries < 5 and failed:
			failed = False
			(status, passed) = addStation2TestToDevice(dictionaryTest)
			
			if status == '{}':
				serial = getSerial(dictionaryTest)
				status2 = updateDeviceWithSerialAndPass(dictionaryTest['ieee'], serial, passed)
				if serial:
					(color, model_number) = lookupPhysicalsForSerial(serial)
					status3 = updateDevicePhysicalsWithColorAndModel(dictionaryTest['ieee'], color, model_number)
			elif status == '400':
				print "IEEE NOT IN DB"
				logFailedStationTwoEntry(testLine, 'ieee_not_in_db', 'ieee_not_in_db')
				return

			if (status != '{}' and status != '400') or (status == '{}' and (status2 == -1 or status3 == -1)):
				print "~~FAILED STATION TWO ENTRY~~"
				print "STATUS 1:" + str(status) + "STATUS 2:" + str(status2) + "STATUS 3:" + str(status3)
				failed = True
				tries += 1
		#IF IT FAILED 5 TIMES -> LOG IT TO FAIL FILE
		if tries == 5:
			print "FAILED 5 TIMES: LOGGING ENTRY TO FAIL LOG"
			logFailedStationTwoEntry(testLine, status, status2)
		else:
			print "SUCCESS"
	else:
		print "NO IEEE: LOGGING ENTRY TO FAIL LOG"
		logFailedStationTwoEntry(testLine, 'no_ieee', 'no_ieee')

#PARSES log_format_7
def postNewStationTwoLogFormat(device, log):
	if device['ieee']:
		if device['station_two_test']:
			serial = device['final_serial']
			ieee = device['ieee']
			stationTestDict = device['station_two_test']
			date = stationTestDict['date']
			stationTest = StationTest(adict=stationTestDict)
			stationTest.individual_tests = create(adict=stationTestDict)

			posted_st = device['mfg_db_post_success']

			if device['mfg_db_post_success'] == False:
				testJSON = stationTest.jsonize()
				posted_st = MDapi.misfitProductionPostStationTestForDevice(ieee, testJSON)
				if posted_st == '{}':
					posted_st = True
				else:
					posted_st = False
				device['mfg_db_post_success'] = posted_st

			if device['mfg_db_update_success'] == False:
				#TRY POSTING UP TO 5 TIMES
				if ieee:
					did_updates = False
					duplicate = False

					(color, model_number) = lookupPhysicalsForSerial(serial)
					
					if posted_st and stationTest.is_passed:
						did_updates = updateDeviceWithSerialAndPass_NEW(ieee, serial, stationTest.is_passed)
						print did_updates
						did_updates = updateDevicePhysicalsWithColorAndModel_NEW(ieee, color, model_number)
						print did_updates
						(did_updates, duplicate) = isDuplicate(ieee, serial)
						print did_updates
						if duplicate:
							did_updates = updateDeviceWithSerialAndPass_NEW(ieee, serial, False)
							print did_updates

					if stationTest.is_passed == False:
						device['mfg_db_update_success'] = True
					else:
						device['mfg_db_update_success'] = did_updates
					device['duplicate'] = duplicate

			if log:
				if device['mfg_db_update_success'] == False or device['mfg_db_post_success'] == False:
					logNewFailedStationTwoEntry(device)
			else:
				return device

def updateDeviceWithSerialAndPass_NEW(ieee, serial, passed):
    update = {'device':{'serial_number': serial, 'is_passed':passed}}
    updateJSON = json.dumps(update)

    status = -1
    tries = 0

    while status == -1 and tries < 5:
        status = MDapi.misfitProductionUpdateDeviceWith(ieee, updateJSON)
        tries += 1

    if tries == 5:
    	return False
    else:
    	return True

def updateDevicePhysicalsWithColorAndModel_NEW(ieee, color, model_number):
    update = {'physical':{'color':color, 'model_number':model_number}}
    updateJSON = json.dumps(update)

    status = -1
    tries = 0

    while status == -1 and tries < 5:
        status = MDapi.misfitProductionUpdateDevicePhysicals(ieee, updateJSON)
        tries += 1

    if tries == 5:
    	return False
    else:
    	return True

def isDuplicate(ieee, serial):
	device = MDapi.misfitProductionGetDeviceWith(ieee, serial)
	if device != -1:
		if device['is_duplicated']:
			return (True, True)
		else:
			return (True, False)
	else:
		return (False, False)


def logNewFailedStationTwoEntry(device):
	debug_station2_lock.acquire()

	failFilePath = MASTER_LOG_PATH + 'failed_station2_new.log'
	
	fail2File = open(failFilePath, 'a')
	fail2File.write(str(device))
	fail2File.close()
	
	debug_station2_lock.release()

#THIS NEEDS TO BE THREAD SAFE
def logFailedStationTwoEntry(testLine, status, status2):
	debug_station2_lock.acquire()

	logger = {'testLine':testLine, 'status':status, 'status2':status2}

	failFilePath = MASTER_LOG_PATH + 'failed_station2.log'
	
	fail2File = open(failFilePath, 'a')
	fail2File.write(str(logger))
	fail2File.close()
	
	debug_station2_lock.release()

#########
#HELPERS
#########

def stringToDictionary(line):
	diction = ast.literal_eval(line)
	if diction['ieee']:
		if diction['ieee'][0:2] == '09':
			diction['ieee'] = reverseIEEE(diction['ieee'])
		diction['ieee'] = diction['ieee'].translate(None, '.')
	return diction

def reverseIEEE(ieee):
	parts = ieee.split('.')
	whole = ''
	for part in parts:
		whole += part[::-1]
		whole += '.'
	whole = whole[:-1]
	return whole

def getSerial(diction):
	serial = ''
	if 'shine_serial' in diction.keys():
		serial = diction['shine_serial']
	if 'serial' in diction.keys():
		serial = diction['serial']
	return serial

def lookupPhysicalsForSerial(serial):
	if serial[3] in colorMap:
		return (colorMap[serial[3]], serial[0:5])
	else:
		return ('UNKNOWN', serial[0:5])

############################################################
#PARSE, CREATE JSON, AND POST TO DATABASE#
############################################################

def postBatchDeviceList(device_list):
	temp = {"devices":device_list}
	batchJSON = json.dumps(temp, cls=DeviceEncoder)
	status = MDapi.misfitProductionPostBatchMisfitDevice(batchJSON)
	return status

def createMisfitDeviceWithStation1Test(testEntry, testDevice):
	#print "Creating misfit device with station 1 test"
	#CREATE MISFIT DEVICE
	md = Device("", testEntry['ieee'], testDevice['creation_time'], "MisfitVS")
	md.physical['mechanical_revision'] = "1.0"
	md.physical['pcb_revision'] = "0.9"
	md.physical['pcba_revision'] = "0.9"
	md.physical['color'] = ""
	md.physical['model_number'] = "SH0AZ"

	#CREATE STAION TEST
	test = createStation1TestForEntry(testEntry, testDevice)
	md.addStationTest(test)

	#TRANSLATE TO JSON AND POST
	mdJSON = md.jsonize()
	status = MDapi.misfitProductionPostMisfitDevice(mdJSON)
	return status

def addStation1TestToDevice(testEntry, testDevice):
	#CREATE STATION 1 TEST
	#print "Adding station 1 test to device"
	test = createStation1TestForEntry(testEntry, testDevice)

	#TRANSLATE TO JSON AND POST
	testJSON = test.jsonize()
	status = MDapi.misfitProductionPostStationTestForDevice(testEntry['ieee'], testJSON)
	return status

def addStation2TestToDevice(testEntry):
	#print "Adding station 2 test to device"
	#CREATE STATION 2 TEST
	test = createStation2TestForEntry(testEntry)

	#TRANSLATE TO JSON AND POST
	testJSON = test.jsonize()
	status = MDapi.misfitProductionPostStationTestForDevice(testEntry['ieee'], testJSON)
	
	return (status, test.is_passed)

def updateDeviceWithSerialAndPass(ieee, serial, passed):
	#print "Updating device with serial and pass"

	update = {'device':{'serial_number': serial, 'is_passed':passed}}
	updateJSON = json.dumps(update)

	status = MDapi.misfitProductionUpdateDeviceWith(ieee, updateJSON)
	return status

def updateDevicePhysicalsWithColorAndModel(ieee, color, model_number):
	update = {'physical':{'color':color, 'model_number':model_number}}
	updateJSON = json.dumps(update)

	status = MDapi.misfitProductionUpdateDevicePhysicals(ieee, updateJSON)
	return status

############################################################
#HELPERS STATION ONE#
############################################################

def createStation1TestForEntry(testEntry, testDevice):
	keys = testEntry.keys()
	stationTest =''
	if set(keys) == set(station_1_formats['log_format_1']):
		stationTest = station1TestForLogFormat1(testEntry, testDevice)
	elif set(keys) == set(station_1_formats['log_format_2']):
		stationTest = station1TestForLogFormat2(testEntry, testDevice)
	elif set(keys) == set(station_1_formats['log_format_3']):
		stationTest = station1TestForLogFormat3(testEntry, testDevice)
	elif set(keys) == set(station_1_formats['log_format_4']):
		stationTest = station1TestForLogFormat4(testEntry, testDevice)
	elif set(keys) == set(station_1_formats['log_format_5']):
		stationTest = station1TestForLogFormat5(testEntry, testDevice)
	else:
		print "impossible!"
	return stationTest

def station1TestForLogFormat1(testEntry, deviceEntry):
	#test entry contains the following DATA
	#bluetooth_advertising_current, accelerometer_self_test, lfxo, led_current, rssi, ieee, ate_id, low_power_current

	#DEVICE ENTRY INFO
	#status (PASS/FAIL), update_time (epoch), creation_time (epoch), code_name(Saturn), ieee, ate_id

	#create Device and StationTest object for posting to MD API
	stationOneTests = []
	passed = True
	if int(deviceEntry['status']) >= 1:
		passed = False

	test = StationTest("1."+str(testEntry['ate_id']), passed, 'log_format_1', "0.0.21.ht03", stationOneTests, deviceEntry['creation_time'])
	return test

def station1TestForLogFormat2(testEntry, deviceEntry):
	#test entry contains the following DATA
	#'test_time', 'bluetooth_advertising_current', 'ieee', 'lfxo', 'led_current', 'serial_number', 'rssi', 'accelerometer_self_test', 'ate_id', 'low_power_current'

	#DEVICE ENTRY INFO
	#status (PASS/FAIL)update_time (epoch)creation_time (epoch) code_name(Saturn) ieee ate_id

	stationOneTests = []
	passed = True
	if int(deviceEntry['status']) >= 1:
		passed = False

	test = StationTest("1."+str(testEntry['ate_id']), passed, 'log_format_2', "0.0.21.ht03", stationOneTests, deviceEntry['creation_time'])
	return test

def station1TestForLogFormat3(testEntry, deviceEntry):
	#manipulate into correct formal for CURL request.
	#'test_time''bluetooth_advertising_current', testFailures','ieee', 'sixLEDCurrent', 'lfxo', 'led_current', 'serial_number', 'rssi', 'accelerometer_self_test', 'ate_id', 'low_power_current'

	#DEVICE ENTRY INFO
	#status (PASS/FAIL)update_time (epoch)creation_time (epoch) code_name(Saturn) ieee ate_id

	stationOneTests = []

	#[0, 0, 0, 0, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 0, 0, 0, 0, 0, 1]
	#DETERMINE IF PASSED OR NOT

	failures = testEntry['testFailures']

	ledPass = True
	for each in failures[4]:
		if each:
			ledPass = False

	passed = True
	i = 0
	while i < len(failures):
		if i != 4 and failures[i]:
			passed = False
		i += 1

	passed = passed and ledPass

	test = StationTest("1."+str(testEntry['ate_id']), passed, 'log_format_3', "0.0.21.ht03", stationOneTests, deviceEntry['creation_time'])
	return test

def station1TestForLogFormat4(testEntry, deviceEntry):
	#manipulate into correct formal for CURL request.
	#'test_time', 'testFailures', 'ieee', 'sixLEDCurrent', 'lfxo', 'led_current', 'rssi', 'serial_number', 'rssi_list', 'accelerometer_self_test', 'ate_id', low_power_current'

	#DEVICE ENTRY INFO
	#status (PASS/FAIL)update_time (epoch)creation_time (epoch) code_name(Saturn) ieee ate_id

	stationOneTests = []
	passed = True

	#[0, 0, 0, 0, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 0, 0, 0, 0, 0, 1]

	failures = testEntry['testFailures']

	#DETERMINE IF PASSED OR NOT
	ledPass = True
	for each in failures[4]:
		if each:
			ledPass = False

	passed = True
	i = 0
	while i < len(failures):
		if i != 4 and failures[i]:
			passed = False
		i += 1

	passed = passed and ledPass

	test = StationTest("1."+str(testEntry['ate_id']), passed, 'log_format_4', "0.0.21.ht03", stationOneTests, deviceEntry['creation_time'])
	return test

def station1TestForLogFormat5(testEntry, deviceEntry):
	
	#manipulate into correct formal for CURL request.
	#'test_time', 'testFailures', 'ieee', 'sixLEDCurrent', 'lfxo', 'led_current', 'rssi', 'serial_number', 'rssi_list', 'accelerometer_self_test', 'invalid_rssi', 'ate_id', 'low_power_current'

	#DEVICE ENTRY INFO
	#status (PASS/FAIL)update_time (epoch)creation_time (epoch) code_name(Saturn) ieee ate_id

	#{'status': 0, 'update_time': 1378141686.75, 'device_type': 'Shine', 'hardware_revision': '', 
	#'creation_time': 1378141657.062, 'code_name': 'Saturn', 'serial_number': 'f06aceb6-168d-48d9-a661-3390dd537ef6', 
	#'ieee': '1C.BA.8C.2C.24.A1', 'ate_id': 8}

	#{'test_time': 1378141690.078, 'testFailures': [0, 0, 0, 0, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 0, 0, 0, 0, 0, 0, ++0++], 
	#'accelerometer_self_test': 1, 'sixLEDCurrent': [0.02315804, 0.02316122, 0.02316462, 0.02316672, 0.023163, 0.02316494, 0.02316343, 0.0231636, 0.02316714, 0.02316964], 
	#'lfxo': None, 'led_current': [0.003786914, 0.006465086, 0.006528375999999999, 0.006376445999999999, 0.006496656, 0.006414415999999999, 0.006428435999999999], 
	#'serial_number': 'f06aceb6-168d-48d9-a661-3390dd537ef6', 'rssi': -60, 'rssi_list': [-60, -58, -58, -61, -61], 'ieee': '1C.BA.8C.2C.24.A1', 
	#'invalid_rssi': 1, 'ate_id': 8, 
	#'low_power_current': [3.357191e-06, 3.214284e-06, 3.273835e-06, 3.315377e-06, 3.32687e-06, 3.365986e-06, 3.315816e-06, 3.198179e-06, 3.3013e-06, 3.363966e-06]}

	map_pass = {'0': True, '1': False}

	testtime = deviceEntry['creation_time']
	failures = testEntry['testFailures']

	stationOneTests = []

	stationOneTests.append(UnlockEFMTest(map_pass[str(failures[0])], timestamp=testtime))
	stationOneTests.append(ProgramCCTest(map_pass[str(failures[1])], timestamp=testtime, ccFirmware="SBLplusController_v1.3.1_noPM3_SBLcommand_small_20130627.hex"))
	stationOneTests.append(ProgramEFMTest(map_pass[str(failures[2])], timestamp=testtime, efmTestFirmware="0.0.21.ht03"))


	#MCU CURRENT CHECK???
	stationOneTests.append(MCUCurrentTest(map_pass[str(failures[3])], timestamp=testtime, mcuCurrent=testEntry['led_current'][0]))

	#this is going in a circle turning on LEDs
	ledPass = True
	for each in failures[4]:
		if each:
			ledPass = False
	ledCurrent = testEntry['led_current'][1:]
	stationOneTests.append(LEDCurrentTest(ledPass, timestamp=testtime, ledCurrents=ledCurrent, passes=failures[4]))


	#THIS IS 6 LEDS on at one time
	summ = 0
	average = 0
	if len(testEntry['sixLEDCurrent']):
		for each in testEntry['sixLEDCurrent']:
			summ += float(each)
			average = summ/len(testEntry['sixLEDCurrent'])
	stationOneTests.append(SixLEDCurrentTest(map_pass[str(failures[5])], timestamp=testtime, avgCurrent=average, allCurrent=testEntry['sixLEDCurrent']))

	stationOneTests.append(AccelSelfTest(map_pass[str(failures[6])], timestamp=testtime))

	summ = 0
	average = 0
	if len(testEntry['low_power_current']):
		for each in testEntry['low_power_current']:
			summ += float(each)
			average = summ/len(testEntry['low_power_current'])

	stationOneTests.append(LowPowerCurrentTest(map_pass[str(failures[7])], timestamp=testtime, avgCurrent=average, allCurrent=testEntry['low_power_current']))


	stationOneTests.append(FinalFlashTest(map_pass[str(failures[8])], timestamp=testtime, finalFW="0.0.28x.boot2_prod.bin"))
	stationOneTests.append(RSSIValueTest(map_pass[str(failures[9])], timestamp=testtime, rssiValues=testEntry['rssi_list'], avgRssi=testEntry['rssi']))
	stationOneTests.append(StationOneTimeoutTest(map_pass[str(failures[10])], timestamp=testtime, timeouts=[]))

	if len(failures) == 12: #THERE WAS A PERIOD OF A FEW DAYS WHERE THIS WASNT A TEST
		stationOneTests.append(InvalidRSSITest(map_pass[str(failures[11])], timestamp=testtime, invalidCount=testEntry['invalid_rssi']))

	#CHECK GLOBAL PASS
	passed = True
	i = 0
	while i < len(failures):
		if i != 4 and failures[i]:
			passed = False
		i += 1
	passed = passed and ledPass #4th element of failures array is an array - we checked it earlier in this function

	test = StationTest("1."+str(testEntry['ate_id']), passed, 'log_format_5', "0.0.21.ht03", stationOneTests, deviceEntry['creation_time'])
	return test

############################################################
#HELPERS STATION TWO#
############################################################

def createStation2TestForEntry(entry):
	keys = entry.keys()
	stationTest =''
	if set(keys) == set(station_2_formats['log_format_1']):
		stationTest = station2TestForLogFormat1(entry)
	elif set(keys) == set(station_2_formats['log_format_2']):
		stationTest = station2TestForLogFormat2(entry)
	elif set(keys) == set(station_2_formats['log_format_3']):
		stationTest = station2TestForLogFormat3(entry)
	elif set(keys) == set(station_2_formats['log_format_4']):
		stationTest = station2TestForLogFormat4(entry)
	elif set(keys) == set(station_2_formats['log_format_5']):
		stationTest = station2TestForLogFormat5(entry)
	elif set(keys) == set(station_2_formats['log_format_6']):
		stationTest = station2TestForLogFormat6(entry)
	else:
		print "impossible!"
	return stationTest

def station2TestForLogFormat1(entry):
	#'log_format_1':['rssi', 'serial', 'ieee', 'low_power_current']
	#testtime = entry['creation_time']
	passed = True

	#RSSI CHECK
	if entry['rssi'] < -60:
		passed = False

	#CURRENT CHECK
	summ = 0
	for each in entry['low_power_current']:
		summ += float(each[1])
	avg = summ/len(entry['low_power_current'])
	if avg > .010:
		passed = False
	if avg < .000020:
		passed = False

	#SERIAL CHECK
	if not entry['serial']:
		passed = False
	
	stationTwoTests = []

	test = StationTest("2.1", passed, 'log_format_1', "0.0.28x.boot2_prod", stationTwoTests)
	return test

def station2TestForLogFormat2(entry):
	#'log_format_2':['rssi', 'serial', 'z_data', 'ieee', 'low_power_current']
	passed = True

	#RSSI CHECK
	if entry['rssi'] < -60:
		passed = False

	#CURRENT CHECK
	summ = 0
	for each in entry['low_power_current']:
		summ += float(each[1])
	avg = summ/len(entry['low_power_current'])
	if avg > .010:
		passed = False
	if avg < .000020:
		passed = False

	#SERIAL CHECK
	if not entry['serial']:
		passed = False
	
	stationTwoTests = []

	test = StationTest("2.1", passed, 'log_format_2', "0.0.28x.boot2_prod", stationTwoTests)
	return test

def station2TestForLogFormat3(entry):
	#'log_format_3':['shine_serial', 'initial_shine_sn', 'initial_current', 'serial_qr', 'rssi', 'z_data', 'failures', 'fw_rev', 'ieee', 'low_power_current'],
	stationTwoTests = []
	nowtime = time.time()

	passed = True
	if entry['failures'] >= 1:
		passed = False

	test = StationTest("2.1", passed, 'log_format_3', "0.0.28x.boot2_prod", stationTwoTests)
	return test

def station2TestForLogFormat4(entry):
	#'log_format_4':['shine_serial', 'average_accel_current', 'initial_shine_sn', 'initial_current', 'serial_qr', 'rssi', 'z_data', 'accel_current', 'failures', 'fw_rev', 'ieee', 'low_power_current'],
	stationTwoTests = []

	passed = True
	if entry['failures'] >= 1:
		passed = False

	test = StationTest("2.1", passed, 'log_format_4', "0.0.28x.boot2_prod", stationTwoTests)
	return test

def station2TestForLogFormat5(entry):
	#'log_format_5':['shine_serial', 'average_accel_current', 'initial_shine_sn', 'initial_current', 'serial_qr', 'rssi', 'z_data', 'accel_current', 'failures', 'fw_rev', 'ieee', 'ate_id', 'low_power_current'],
	stationTwoTests = []

	passed = True
	if entry['failures'] >= 1:
		passed = False

	test = StationTest("2."+str(entry['ate_id']), passed, 'log_format_5', "0.0.28x.boot2_prod", stationTwoTests)
	return test

def station2TestForLogFormat6(entry):
	#'log_format_6':['shine_serial', 'average_accel_current', 'initial_shine_sn', 'timeouts', 'serial_qr', 'average_operating_current', 'z_data', 'accel_current', 'operating_current', 'fw_rev', 'rssi', 'failures', 'ieee', 'ate_id']

	#{'shine_serial': 'SH0AZ01HYK', 'average_accel_current': 0.0040509471, 'initial_shine_sn': '9876543210', 
	#'timeouts': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'serial_qr': 'SH0AZ01HYK', 
	#'average_operating_current': 0.00010987287666666666, 'z_data': [64992, 65008, 65008], 
	#'accel_current': [0.004659593, 0.005038253, 0.00371973, 0.003930369, 0.003877925, 0.003860474, 0.004012081, 0.003864414, 0.003670936, 0.003875696], 
	#'operating_current': [7.273108e-05, 7.460565e-05, 7.738173e-05, 7.976293e-05, 0.0005107, 0.0001261219, 0.000138475, 0.0001495942, 0.0001327723, 0.0001374111], 
	#'rssi': -35, 'fw_rev': '0.0.28x.boot2_prod', 'failures': [0, 0, 1, 0, 0, 0, 0, 0, 0], 'ieee': '90.59.AF.11.BD.E9', 'ate_id': 3}

	#SCAN_FAIL = 0
	#ADV_SAMPLES_FAIL = 1
	#AVG_CURRENT_FAIL = 2
	#CHECK_FW_FAIL = 3
	#ACCEL_STREAM_FAIL = 4
	#CONFIRM_LED_FAIL = 5
	#SN_PROGRAM_FAIL = 6
	#SN_READ_FAIL = 7
	#TIMEOUT_FAIL = 8

	map_pass = {'0': True, '1': False}
	
	nowtime = time.time()
	stationTwoTests = []
	failures = entry['failures']

	stationTwoTests.append(ScanTest(isPassed=map_pass[str(failures[0])], timestamp=nowtime, rssi=entry['rssi']))

	numberSamples = 0
	if len(entry['operating_current']) > 0:
		for each in entry['operating_current']:
			if each > .000240:
				numberSamples += 1

	stationTwoTests.append(AdvSamplesTest(isPassed=map_pass[str(failures[1])], timestamp=nowtime, numSamples=numberSamples))
	stationTwoTests.append(OperCurrentTest(isPassed=map_pass[str(failures[2])], timestamp=nowtime, currents=entry['operating_current'], average=entry['average_operating_current']))
	stationTwoTests.append(FirmwareCheckTest(isPassed=map_pass[str(failures[3])], timestamp=nowtime, expectedFW='0.0.28x.boot2_prod', fwVersion=entry['fw_rev']))
	stationTwoTests.append(AccelZDataTest(isPassed=map_pass[str(failures[4])], timestamp=nowtime, zData=entry['z_data']))

	average = 0
	if len(entry['accel_current']) > 0:
		summ = 0
		for each in entry['accel_current']:
				summ += float(each)
		average = summ/len(entry['accel_current'])

	stationTwoTests.append(ConfirmLEDCurrentTest(isPassed=map_pass[str(failures[5])], timestamp=nowtime, confirm=entry['accel_current'], average=average))
	stationTwoTests.append(WriteSerialTest(isPassed=map_pass[str(failures[6])], timestamp=nowtime, qrSerial=entry['serial_qr']))
	stationTwoTests.append(ReadSerialTest(isPassed=map_pass[str(failures[7])], timestamp=nowtime, initialSerial=entry['initial_shine_sn'], finalSerial=entry['shine_serial']))
	stationTwoTests.append(StationTwoTimeoutTest(isPassed=map_pass[str(failures[8])], timestamp=nowtime, timeouts=entry['timeouts']))

	passed = True
	for each in entry['failures']:
		if each:
			passed = False

	test = StationTest("2."+ str(entry['ate_id']), passed, 'log_format_6', "0.0.28x.boot2_prod", stationTwoTests)
	return test

##############################
#NO LONGER USED
##############################
def findFormats(entry):
	keys = entry.keys()

	if set(keys) not in formats:
		formats.append(set(keys))

def detectFormat_Station2(entry):
	keys = entry.keys()

def create(adict):
	individual_tests = []
	for k, val in adict.items():
		print str(k) + ", " + str(val)
		if isinstance(val, list):
			for v in val:
				test = ''
				if v['name'] == UnlockEFMTest.name:
					test = UnlockEFMTest(adict=v)
				elif v['name'] == ProgramCCTest.name:
					test = ProgramCCTest(adict=v)
				elif v['name'] == ProgramEFMTest.name:
					test = ProgramEFMTest(adict=v)
				elif v['name'] == MCUCurrentTest.name:
					test = MCUCurrentTest(adict=v)
				elif v['name'] == LEDCurrentTest.name:
					test = LEDCurrentTest(adict=v)
				elif v['name'] == SixLEDCurrentTest.name:
					test = SixLEDCurrentTest(adict=v)
				elif v['name'] == AccelSelfTest.name:
					test = AccelSelfTest(adict=v)
				elif v['name'] == LowPowerCurrentTest.name:
					test = LowPowerCurrentTest(adict=v)
				elif v['name'] == InvalidRSSITest.name:
					test = InvalidRSSITest(adict=v)
				elif v['name'] == RSSIValueTest.name:
					test = RSSIValueTest(adict=v)
				elif v['name'] == FinalFlashTest.name:
					test = FinalFlashTest(adict=v)
				elif v['name'] == StationOneTimeoutTest.name:
					test = StationOneTimeoutTest(adict=v)
				elif v['name'] == ScanTest.name:
					test = ScanTest(adict=v)
				elif v['name'] == AdvSamplesTest.name:
					test = AdvSamplesTest(adict=v)
				elif v['name'] == OperCurrentTest.name:
					test = OperCurrentTest(adict=v)
				elif v['name'] == FirmwareCheckTest.name:
					test = FirmwareCheckTest(adict=v)
				elif v['name'] == AccelZDataTest.name:
					test = AccelZDataTest(adict=v)
				elif v['name'] == ConfirmLEDCurrentTest.name:
					test = ConfirmLEDCurrentTest(adict=v)
				elif v['name'] == WriteSerialTest.name:
					test = WriteSerialTest(adict=v)
				elif v['name'] == ReadSerialTest.name:
					test = ReadSerialTest(adict=v)
				elif v['name'] == StationTwoTimeoutTest.name:
					test = StationTwoTimeoutTest(adict=v)
						
				individual_tests.append(test)
	return individual_tests

def testStuff1():
	device = {'mfg_db_post_success': True, 'unlocked': True, 'station_one_log_format': 'log_format_7', 'ieee_read': True, 'test_began': True, 
	'station_test': {'firmware_revision': '0.0.21.ht03', 'is_passed': True, 'individual_tests': [{'timestamp': 1392159616.308, 
	'is_passed': True, 'name': 'UNLOCK EFM TEST'}, {'timestamp': 1392159629.498, 'is_passed': True, 'name': 'PROGRAM CC TEST', 
	'cc_fw': 'SBLplusController_v1.3.1_noPM3_SBLcommand_small_20130627.hex'}, {'timestamp': 1392159633.217, 'efm_test_fw': '0.0.21.ht03', 
	'is_passed': True, 'name': 'PROGRAM EFM TEST'}, {'timestamp': 1392159636.235, 'is_passed': True, 'name': 'MCU CURRENT TEST', 
	'mcuCurrent': 0.003626212}, {'timestamp': 1392159636.235, 'ledCurrents': [0.006341853, 0.006367444999999999, 0.006299526, 0.006335475, 0.0063392150000000005, 0.006292879999999999], 
	'is_passed': True, 'passes': [True, True, True, True, True, True], 'name': 'LED CURRENT TEST'}, 
	{'timestamp': 1392159639.058, 'is_passed': True, 'name': 'SIX LED CURRENT TEST', 
	'allCurrent': [0.02244297, 0.02245161, 0.02245585, 0.02245992, 0.02246204, 0.02246341, 0.02246297, 0.02246555, 0.0224674, 0.0224723], 
	'avgCurrent': 0.037434003333333334}, {'timestamp': 1392159639.477, 'is_passed': True, 'name': 'ACCEL SELF TEST'}, 
	{'timestamp': 1392159642.279, 'is_passed': True, 'name': 'LOW POWER CURRENT TEST', 'allCurrent': [3.45946e-06, 3.567561e-06, 3.46154e-06, 3.452982e-06, 3.44186e-06, 3.425997e-06, 3.259667e-06, 3.415377e-06, 3.900481e-06, 3.551497e-06], 
	'avgCurrent': 3.4936422e-06}, {'prod_fw': '0.0.28x.boot2_prod', 'timestamp': 1392159648.239, 'is_passed': True, 'name': 'FINAL FLASH TEST'}, 
	{'timestamp': 1392159651.184, 'is_passed': True, 'name': 'RSSI VALUE TEST', 'rssi_values': [-47, -48, -48, -48, -48], 'average_rssi': -48}, 
	{'timestamp': 1392159651.184, 'is_passed': True, 'rssi_invalid_count': 0, 'name': 'INVALID RSSI TEST'}, 
	{'timeouts': ['0', '0'], 'timestamp': 1392159651.189, 'is_passed': True, 'name': 'STATION ONE TIMEOUT TEST'}], 
	'script_revision': 'log_format_7', 'date': 1392159651.189, 'ate_id': '1.0'}, 'ieee': '001831F0E016'}
	postNewStationOneLogFormat(device, True)

def testStuff2():
	device = {'global_pass': False, 'station_two_log_format': 'log_format_7', 'mfg_db_post_success': True, 
	'station_two_test': {'firmware_revision': '0.0.28x.boot2_prod', 'is_passed': True, 
	'individual_tests': [{'timestamp': 1392159328.136, 'is_passed': True, 'name': 'SCAN TEST', 'rssi': -69}, {'adv_samples': 1, 
	'timestamp': 1392159328.136, 'is_passed': True, 'name': 'ADV SAMPLES TEST'}, {'timestamp': 1392159328.136, 
	'average': 0.00014128933333333333, 'is_passed': True, 'currents': [0.0001479566, 0.0001347274, 0.000146161, 
	0.0001423329, 0.0001441136, 0.0001403943, 0.0001385197, 0.0006502017, 0.0001321584, 0.0001452401], 
	'name': 'OPER CURRENT TEST'}, {'timestamp': 1392159328.136, 'is_passed': True, 'name': 'FIRMWARE CHECK TEST', 
	'fw_version': '0.0.28x.boot2_prod', 'expected_fw': '0.0.28x.boot2_prod'}, {'timestamp': 1392159328.136, 
	'is_passed': True, 'name': 'ACCEL Z DATA TEST', 'z_data': [64992, 65008, 65008]}, {'timestamp': 1392159328.136, 
	'average': 0.0034794269, 'confirm_current': [0.003662007, 0.003459914, 0.003455158, 0.003320815, 0.003528572, 0.003549976, 0.003477342, 0.003483295, 0.003391528, 0.003465662], 
	'is_passed': True, 'name': 'CONFIRM LED CURRENT TEST'}, {'timestamp': 1392159328.136, 'is_passed': True, 
	'name': 'WRITE SERIAL TEST', 'qr_serial': 'SH0AZ049BY'}, {'timestamp': 1392159328.136, 'is_passed': True, 
	'initial_serial': 'SH0AZ049BY', 'name': 'READ SERIAL TEST', 'final_serial': 'SH0AZ049BY'}, 
	{'timeouts': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'timestamp': 1392159328.136, 'is_passed': True, 'name': 'STATION TWO TIMEOUT TEST'}], 
	'script_revision': 'log_format_7', 'date': 1392159328.136, 'ate_id': '2.0'}, 'duplicate': True, 'ieee': '9059AF1153DA', 'final_serial':'SH0AZ049BY'}
	postNewStationTwoLogFormat(device, True)


USAGE_TEXT = """
USAGE: python mfg_logs_to_db_extractor.py batch_full|batch_master_log_files|batch_failed|station_one_daemon|station_one_daemon_failed|station_two_daemon|station_two_daemon_failed|test_stuff1|test_stuff2
"""

def usage():
	print USAGE_TEXT
	sys.exit(-1)

def main(argv):
	if len(argv) != 1:
		usage()

	type = argv[0]

	if type == 'batch_full':
		buildBatchQueries()
	elif type == 'build_master_log_files':
		build_master_log_files()
	elif type == 'batch_failed':
		postFailedBatchEntries()
	elif type == 'station_one_daemon':
		station_one_daemon_import()
	elif type == 'station_one_daemon_failed':
		station_one_failed_daemon_import()
	elif type == 'station_two_daemon':
		station_two_daemon_import()
	elif type == 'station_two_daemon_failed':
		station_two_failed_daemon_import()
	elif type == 'test_stuff1':
		testStuff1()
	elif type == 'test_stuff2':
		testStuff2()
	elif type == 'station_two_cron':
		CRON_processAndUpdateStation2Log()
	elif type == 'station_one_cron':
		CRON_processAndUpdateStation1Log()
	else:
		usage()

if __name__ == '__main__':
	main(sys.argv[1:])
	