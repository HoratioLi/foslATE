#!/usr/bin/env python
'''
Created on 2013-06-11

@author: Trung Huynh, Rachel Kalmar
'''

import urllib2
import urllib
import httplib
import socket
import ssl
import json
import collections
import time
from constants import *
from model.device import Device
from model.device import *
from pprint import pprint

# if MFG_DB_STAGING:
#     # baseURL = "https://4.80.32.15/md/"
#     baseURL = "https://54.80.32.15/md/"    
#     baseURLDomainName = "https://md.api.int.misfitwearables.com/md/"
#     baseURLDomainNamePing = "https://md.api.int.misfitwearables.com/md/ping"
# if not MFG_DB_STAGING:
#     baseURL = "https://54.163.250.147/md/"    
#     baseURLDomainName = "https://md.api.misfitwearables.com/md/"
#     baseURLDomainNamePing = "https://md.api.misfitwearables.com/md/ping"

def internet_on():
    try:
        print("Attempting connection to %s" % INTERNET_TEST_URL)
        response=urllib2.urlopen(INTERNET_TEST_URL,timeout=DB_READ_TIMEOUT)      
        return True
    except urllib2.URLError as e: 
        print "URLError: %s" % e
        return False
    except urllib2.HTTPError, e:
        print "HTTPError: %s" % e
        return False           
    except httplib.HTTPException, e:
        print "HTTPException: %s" % e
        return False
    except (httplib.HTTPException, socket.error) as e:
        print "Socket error: %s" % e
        return False

def md_api_on():
    try:
        print("Trying misfit database")
        response=urllib2.urlopen(BASE_URL_DOMAIN_NAME_PING, timeout=DB_READ_TIMEOUT)
        return True
    except urllib2.URLError as e: 
        print "URLError: %s" % e
        return False
    except urllib2.HTTPError, e:
        print "HTTPError: %s" % e
        return False   
    except httplib.HTTPException, e:
        print "HTTPException: %s" % e
        return False
    except (httplib.HTTPException, socket.error) as e:
        print "Socket error: %s" % e
        return False

def misfitProductionPostBatchMisfitDevice(batchJSON):
    post_data = batchJSON.encode('utf-8')

    deviceURL = BASE_URL + "devices/batch"
    headers = {}
    headers['Content-Type'] = 'application/json'

    req = urllib2.Request(deviceURL, post_data, headers)
    response = ""

    try:
        response = urllib2.urlopen(req, timeout=DB_POST_TIMEOUT).read()
        response = json.loads(response)
        return str(response)
    except urllib2.HTTPError, e:
        return str(e.code)
    except urllib2.URLError, e:
        print str(e)
        return -1
    except httplib.HTTPException, e:
        print 'HTTPException'
        return -1
    except ssl.SSLError, e:
        print e
        return -50        
    except Exception:
        print 'generic exception'
        return -1

def misfitProductionPostMisfitDevice(mdJSON):
    post_data = mdJSON.encode('utf-8')

    # print "Post data: " 
    # pprint(post_data)
    # print ''

    deviceURL = BASE_URL + "devices"
    headers = {}
    headers['Content-Type'] = 'application/json'

    req = urllib2.Request(deviceURL, post_data, headers)
    response = ""

    print str(req)
    # pprint(vars(req))

    try:
        response = urllib2.urlopen(req, timeout=DB_POST_TIMEOUT).read()
        response = json.loads(response)
        return str(response)
    except urllib2.HTTPError, e:
        return str(e.code)
    except urllib2.URLError, e:
        #print str(e.code)
        return -1
    except httplib.HTTPException, e:
        print 'HTTPException'
        return -1
    except ssl.SSLError, e:
        print e
        return -50       
    except Exception:
        print 'generic exception'
        return -1

def misfitProductionPostStationTestForDevice(ieee, testJSON):
    post_data = testJSON.encode('utf-8')
    # print "Post data: " 
    # pprint(post_data)
    # print ''

    deviceURL = BASE_URL + "devices/" + ieee + "/add_stations"
    headers = {}
    headers['Content-Type'] = 'application/json'
    req = urllib2.Request(deviceURL, post_data, headers)
    print ""
    print str(req)
    # pprint(vars(req))
    print str(deviceURL)
    response = ""

    try:
        response = urllib2.urlopen(req, timeout=DB_POST_TIMEOUT).read()
        response = json.loads(response)
        return str(response)
    except urllib2.HTTPError, e:
        return str(e.code)
    except urllib2.URLError, e:
        print e
        return -1
    except httplib.HTTPException, e:
        print 'HTTPException'
        return -1
    except ssl.SSLError, e:
        print e
        return -50        
    except Exception:
        print 'generic exception'
        return -1

def misfitProductionUpdateDeviceWith(ieee, updateJSON):
    post_data = updateJSON.encode('utf-8')

    # print "\nPost data: " 
    # pprint(post_data)
    # print ''

    deviceURL = BASE_URL + "devices/" + ieee
    headers = {}
    headers['Content-Type'] = 'application/json'

    req = urllib2.Request(deviceURL, post_data, headers)
    req.get_method = lambda: 'PUT'
    response = ""

    if DEBUG_MODE:
        print "req: " + str(req)
    # pprint(vars(req))

    try:
        response = urllib2.urlopen(req, timeout=DB_POST_TIMEOUT).read()
        response = json.loads(response)
        print response
        return response
    except urllib2.HTTPError, e:
        return -1
    except urllib2.URLError, e:
        return -1
    except httplib.HTTPException, e:
        print 'HTTPException'
        return -1
    except ssl.SSLError, e:
        print e
        return -50
    except Exception:
        print 'generic exception'
        return -1

def misfitProductionUpdateDeviceWithSerialInternal(ieee, updateJSON):
    post_data = updateJSON.encode('utf-8')

    # print "\nPost data: " 
    # pprint(post_data)
    # print ''

    deviceURL = BASE_URL + "devices/" + ieee + "/internal"
    headers = {}
    headers['Content-Type'] = 'application/json'

    req = urllib2.Request(deviceURL, post_data, headers)
    req.get_method = lambda: 'PUT'
    response = ""

    if DEBUG_MODE:
        print "req: " + str(req)
    # pprint(vars(req))

    try:
        response = urllib2.urlopen(req, timeout=DB_POST_TIMEOUT).read()
        response = json.loads(response)
        print response
        return response
    except urllib2.HTTPError, e:
        return -1
    except urllib2.URLError, e:
        return -1
    except httplib.HTTPException, e:
        print 'HTTPException'
        return -1
    except ssl.SSLError, e:
        print e
        return -50
    except Exception:
        print 'generic exception'
        return -1

def misfitProductionUpdateDeviceWithSerialSMT(ieee, updateJSON):
    post_data = updateJSON.encode('utf-8')

    # print "\nPost data: " 
    # pprint(post_data)
    # print ''

    deviceURL = BASE_URL + "devices/" + ieee + "/smt"
    headers = {}
    headers['Content-Type'] = 'application/json'

    req = urllib2.Request(deviceURL, post_data, headers)
    req.get_method = lambda: 'PUT'
    response = ""

    if DEBUG_MODE:
        print "req: " + str(req)
    # pprint(vars(req))

    try:
        response = urllib2.urlopen(req, timeout=DB_POST_TIMEOUT).read()
        response = json.loads(response)
        print response
        return response
    except urllib2.HTTPError, e:
        return -1
    except urllib2.URLError, e:
        return -1
    except httplib.HTTPException, e:
        print 'HTTPException'
        return -1
    except ssl.SSLError, e:
        print e
        return -50
    except Exception:
        print 'generic exception'
        return -1

def misfitProductionUpdateDevicePhysicals(ieee, updateJSON):
    post_data = updateJSON.encode('utf-8')
    deviceURL = BASE_URL + "physicals/" + ieee
    headers = {}
    headers['Content-Type'] = 'application/json'

    req = urllib2.Request(deviceURL, post_data, headers)
    req.get_method = lambda: 'PUT'
    response = ""

    if DEBUG_MODE:
        print "req: " + str(req)
        pprint(vars(req))
        print ""

    try:
        response = urllib2.urlopen(req, timeout=DB_POST_TIMEOUT).read()
        response = json.loads(response)
        print response
        return response
    except urllib2.HTTPError, e:
        return -1
    except urllib2.URLError, e:
        return -1
    except httplib.HTTPException, e:
        print 'HTTPException'
        return -1
    except ssl.SSLError, e:
        print e
        return -50        
    except Exception:
        print 'generic exception'
        return -1

def misfitProductionGetDeviceWith(ieee_address, serial_number):
    deviceURL = BASE_URL + "devices" + "?"
    params = "serial_number=" + serial_number + "&ieee_address=" + ieee_address

    requestURL = deviceURL + params
    req = urllib2.Request(requestURL)

    try:
        response = urllib2.urlopen(req, timeout=DB_READ_TIMEOUT).read()
        response = json.loads(response)
        return response
    except urllib2.HTTPError, e:
        return -1
    except urllib2.URLError, e:
        return -1
    except httplib.HTTPException, e:
        print 'HTTPException'
        return -1
    except ssl.SSLError, e:
        print e
        return -50        
    except Exception:
        print 'generic exception'
        return -1
    #GET /md/devices?serial_number=SH0AZ03NHJ004&ieee_address=Binh002

def misfitProductionGetDeviceFromSerial(serial_number):
    deviceURL = BASE_URL + "devices_by_serial_number" + "?"
    params = "serial_number=" + serial_number

    requestURL = deviceURL + params
    req = urllib2.Request(requestURL)

    try:
        response = urllib2.urlopen(req, timeout=DB_READ_TIMEOUT).read()
        response = json.loads(response)
        return response
    except urllib2.HTTPError, e:
        return -1
    except urllib2.URLError, e:
        return -1
    except httplib.HTTPException, e:
        print 'HTTPException'
        return -1
    except ssl.SSLError, e:
        print e
        return -50       
    except Exception:
        print 'generic exception'
        return -1
    #GET /md/devices?serial_number=SH0AZ03NHJ004

def misfitProductionGetDeviceFromSerialInternal(serial_number_internal):
    deviceURL = BASE_URL + "devices_by_serial_number" + "?"
    # deviceURL = BASE_URL + "devices_by_serial_number_internal" + "?"    
    params = "serial_number_internal=" + serial_number_internal

    requestURL = deviceURL + params
    req = urllib2.Request(requestURL)

    # pprint(vars(req))

    try:
        response = urllib2.urlopen(req, timeout=DB_READ_TIMEOUT).read()
        response = json.loads(response)
        # print response
        return response
    except urllib2.HTTPError, e:
        return -1
    except urllib2.URLError, e:
        return -1
    except httplib.HTTPException, e:
        print 'HTTPException'
        return -1
    except ssl.SSLError, e:
        print e
        return -50
    except Exception:
        print 'generic exception'
        return -1
    #GET /md/devices?serial_number=SH0AZ03NHJ004

def misfitProductionGetDeviceFromSerialSMT(serial_number_smt):
    deviceURL = BASE_URL + "devices_by_serial_number" + "?"
    # deviceURL = BASE_URL + "devices_by_serial_number_smt" + "?"    
    params = "serial_number_smt=" + serial_number_smt

    requestURL = deviceURL + params
    req = urllib2.Request(requestURL)

    try:
        response = urllib2.urlopen(req, timeout=DB_READ_TIMEOUT).read()
        response = json.loads(response)
        return response
    except urllib2.HTTPError, e:
        return -1
    except urllib2.URLError, e:
        return -1
    except httplib.HTTPException, e:
        print 'HTTPException'
        return -1
    except ssl.SSLError, e:
        print e
        return -50
    except Exception:
        print 'generic exception'
        return -1
    #GET /md/devices?serial_number=SH0AZ03NHJ004    

def emptyDatabase():
    url = BASE_URL + "devices" + "/" + "please_be_careful_and_responsible_to_use_it_before_running"
    headers = {}
    headers['Content-Type'] = 'application/json'
    data = "{}"
    req = urllib2.Request(url, data, headers)
    req.get_method = lambda: 'DELETE'
    response = urllib2.urlopen(req).read()
    print response

def main():
    pass
    #emptyDatabase()
    #testStationOne()
    #testStationTwo()

########## DEPRECATED ###########
# def testStationOne():
#      #Create the device object
#     md = Device("sn99540110", "ieee991220", "123123123", "misfitVS")
#     md.physical['mechanical_revision'] = "12"
#     md.physical['pcb_revision'] = "101"
#     md.physical['pcba_revision'] = "102"
#     md.physical['color'] = "Space Grey"
#     md.physical['model_number'] = "Saturn"

#     #create each indivudal test object
#     nowtime = time.time()
#     stationOneTests = []

#     stationOneTests.append(UnlockEFMTest(isPassed=True, timestamp=nowtime, name="UNLOCK EFM"))

#     stationOneTests.append(ProgramCCTest(isPassed=True, timestamp=nowtime, name="PROGRAM CC", ccFirmware="sadkfdfsd.bin"))

#     stationOneTests.append(ProgramEFMTest(isPassed=True, timestamp=nowtime, name="PROGRAM EFM", efmTestFirmware="tester.bin"))

#     currents = [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6]
#     passes = [True, True, True, True, True, False, False]
#     stationOneTests.append(LEDCurrentTest(isPassed=True, timestamp=nowtime, name="LED CURRENT", ledCurrents=currents, passes=passes))

#     allC = [1, 1, 1, 1, 1, 1.0, -1, -1.0, 0, 1]
#     avg = 10.5
#     stationOneTests.append(SixLEDCurrentTest(isPassed=True, timestamp=nowtime, name="SIX LED CURRENT", avgCurrent=avg, allCurrent=allC))

#     stationOneTests.append(AccelSelfTest(isPassed=True, timestamp=nowtime, name="ACCEL SELF"))

#     allLPC = [0, 0, 0, 3.5, 4, 5, 6, 7, 1, 2]
#     avgLP = 6.3
#     stationOneTests.append(LowPowerCurrentTest(isPassed=True, timestamp=nowtime, name="LOW POWER CURRENT", avgCurrent=avgLP, allCurrent=allLPC))

#     stationOneTests.append(FinalFlashTest(isPassed=True, timestamp=nowtime, name="FINAL FLASH", finalFW="prod_boot.28.x"))

#     rssis = [2, 1, 3, 4, 5]
#     avgRssi = 2.5
#     stationOneTests.append(RSSIValueTest(isPassed=True, timestamp=nowtime, name="RSSI VALUE", rssiValues=rssis, avgRssi=avgRssi))

#     rssiInvalidCount = 1
#     stationOneTests.append(InvalidRSSITest(isPassed=True, timestamp=nowtime, name="INVALID RSSI", invalidCount=rssiInvalidCount))

#     timeouts = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ,0]
#     stationOneTests.append(StationOneTimeoutTest(isPassed=True, timestamp=nowtime, name="STATIONE ONE TIMEOUT", timeouts=timeouts))

#     #create the overall station test object
#     md.addStationTest(StationTest("ate 01", False, "v20", "v19", stationOneTests))

#     temp = md.jsonize()

#     #post to the database
#     misfitProductionPostMisfitDevice(temp)

# def testStationTwo():
#     #Create the device object
#     md = Device("sn99540110", "ieee991220", "123123123", "misfitVS")
#     md.physical['mechanical_revision'] = "12"
#     md.physical['pcb_revision'] = "101"
#     md.physical['pcba_revision'] = "102"
#     md.physical['color'] = "Space Grey"
#     md.physical['model_number'] = "Saturn"

#     #create each indivudal test object
#     nowtime = time.time()
#     stationTwoTests = []

#     rssi = -60
#     stationTwoTests.append(ScanTest(isPassed=True, timestamp=nowtime, name="SCAN", rssi=rssi))

#     numberSamples = 1
#     stationTwoTests.append(AdvSamplesTest(isPassed=True, timestamp=nowtime, name="ADVERTISING SAMPLES", numSamples=numberSamples))

#     operCurrents = [1.1, 1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7, 8.8, 9.9]
#     avgCurrent = 20.0
#     stationTwoTests.append(OperCurrentTest(isPassed=True, timestamp=nowtime, name="OPERATING CURRENT", currents=operCurrents, average=avgCurrent))

#     expectedFW = "expected.bin"
#     fwVersion = "fwVersion.bin"
#     stationTwoTests.append(FirmwareCheckTest(isPassed=True, timestamp=nowtime, name="FIRMWARE CHECK", expectedFW=expectedFW, fwVersion=fwVersion))

#     zData = [256,256,256]
#     stationTwoTests.append(AccelZDataTest(isPassed=True, timestamp=nowtime, name="ACCEL Z DATA", zData=zData))

#     confirmCurrent = [2.5, 2.5, 2.5, 2.5, 2.5, 3.5, 2.5, 2.5, 2.7, 3.3]
#     average = 3.1
#     stationTwoTests.append(ConfirmLEDCurrentTest(isPassed=True, timestamp=nowtime, name="CONFIRM LED ON", confirm=confirmCurrent, average=average))

#     qrSerial = "SHXXXXXXXX"
#     stationTwoTests.append(WriteSerialTest(isPassed=True, timestamp=nowtime, name="WRITE SERIAL", qrSerial=qrSerial))

#     initial = "9876543210"
#     final = "SHXXXXXXXX"
#     stationTwoTests.append(ReadSerialTest(isPassed=True, timestamp=nowtime, name="READ SERIAL", initialSerial=initial, finalSerial=final))

#     timeouts = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
#     stationTwoTests.append(StationTwoTimeoutTest(isPassed=True, timestamp=nowtime, name="STATIONE TWO TIMEOUT", timeouts=timeouts))

#     #create the overall station test object
#     md.addStationTest(StationTest("ate 01", False, "v20", "v19", stationTwoTests))

#     temp = md.jsonize()
#     print temp

#     #post to the database
#     misfitProductionPostMisfitDevice(temp)

if __name__ == '__main__':
    main()
