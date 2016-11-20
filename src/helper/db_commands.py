#!/usr/bin/env python
'''
Created on 2014-08-12

@author: Rachel Kalmar
'''

from constants import *
from pprint import pprint
from model.bleDevice import *

import os
import collections
import helper.utils as util
import helper.MDapi as MDapi
import time
import datetime
import sys
import json

from os import listdir

# Check to see if the internet is on, retry if can't connect
def checkInternetWithRetries():
    tries = 0
    failed = True

    while tries < MAX_INTERNET_CONNECT_ATTEMPTS and failed:
        failed = False
        internet_on = MDapi.internet_on()
        if not internet_on:
            failed = True
            tries += 1
            print "\nInternet connect attempt %s/%s\n" % (tries, MAX_INTERNET_CONNECT_ATTEMPTS)

    if tries >= MAX_INTERNET_CONNECT_ATTEMPTS:
        print "\n...\n...\n..."                                                                    
        print "\nFailed connecting to internet after %s retries." % tries
        print "...\n...\n..."   

    if internet_on:
        print "\nConnected to the internet on attempt %s." % tries 

    return internet_on

# Check to see if the database can be accessed, retry if can't connect
def checkDatabaseWithRetries():
    tries = 0
    failed = True

    while tries < MAX_INTERNET_CONNECT_ATTEMPTS and failed:
        failed = False
        #md_api_on = MDapi.md_api_on()

        misfitDevice = MDapi.misfitProductionGetDeviceFromSerialInternal("SZ2ZZ00H5F")

        if misfitDevice == -50 or misfitDevice == -1:
            failed = True
            tries += 1
            print "\nDatabase contact attempt %s/%s\n" % (tries, MAX_INTERNET_CONNECT_ATTEMPTS)

    if tries >= MAX_INTERNET_CONNECT_ATTEMPTS:
        print "\n...\n...\n..."                                                                    
        print "\nFailed contacting database after %s retries." % tries
        print "...\n...\n..." 

    if failed == False:
        print "\nContacted the database on attempt %s." % tries 

    return not failed 

# Get ieee address from database using serial_number, either internal, smt, or packaging
def getIEEEfromDatabase(serial_number, serial_num_type):
    duplicateEntries = False
    serial_from_database = None
    serial_internal_from_database = None
    serial_smt_from_database = None
    tries  = 0
    failed = True

    # TODO: If the device is empty, don't retry, fail.
    while tries < MAX_DATABASE_READ_ATTEMPTS and failed:
        failed = False
        if serial_num_type == 'internal':
            misfitDevice = MDapi.misfitProductionGetDeviceFromSerialInternal(serial_number)  
            serial_number_internal = serial_number
        elif serial_num_type == 'smt':
            misfitDevice = MDapi.misfitProductionGetDeviceFromSerialSMT(serial_number)  
            serial_number_smt = serial_number
        elif serial_num_type == 'packaging':
            misfitDevice = MDapi.misfitProductionGetDeviceFromSerial(serial_number) 
            if misfitDevice == -1: # if the serial number doesn't exist or device is empty, return
                print "\nPackaging serial number does not exist in database"  
                return (None, None, None, None, False)
        if misfitDevice == -50 or misfitDevice == -1:
            failed = True
            tries += 1
            print "\nRead attempt %s/%s\n" % (tries, MAX_DATABASE_READ_ATTEMPTS)

    if failed == False:
        print "..."                                   
        print "Read after %s retries." % tries
        print "...\n"            

    if tries >= MAX_DATABASE_POST_ATTEMPTS:
            print "\n...\n...\n..."                                                                    
            print "\nFailed reading after %s retries." % tries
            print "...\n...\n..."                                             

    if failed == True:
        return (None, None, None, None, None)

    misfitDevice = util.convertUnicode(misfitDevice)

    ieee_addresses = []
    serial_numbers_internal = []
    serial_numbers_smt = []
    serial_numbers = []

    print "\nmisfitDevice: ", misfitDevice
    for i, x in enumerate(misfitDevice['devices']):
        ieee_addresses.append(x['ieee_address'])
        serial_numbers_internal.append(x['serial_number_internal'])
        serial_numbers_smt.append(x['serial_number_smt'])        
        serial_numbers.append(x['serial_number'])
    if len(ieee_addresses) == 0:
        if serial_num_type == 'internal':
            print "\nError: no ieee addresses exist in database for this internal serial number (%s).\n" % serial_number             
        elif serial_num_type == 'smt':
            print "\nError: no ieee addresses exist in database for this SMT serial number (%s).\n" % serial_number             
        elif serial_num_type == 'packaging':
            print "\nError: no ieee addresses exist in database for this serial number (%s).\n" % serial_number 
        ieee_address = None
    elif len(ieee_addresses) > 1:
        print "\nError: %s ieee addresses exist for this serial number.\n" % len(ieee_addresses)
        for x in ieee_addresses:
            print "     %s" % x
        # ieee_address = ieee_addresses[0]
        # print "\nieee address: %s \n" % ieee_address
        ieee_address = None
        duplicateEntries = True
    else:
        ieee_address = ieee_addresses[0]
        print "\nieee address: %s \n" % ieee_address

    if ieee_address is not None:
        # print "serial_numbers: %s" % serial_numbers
        if len(serial_numbers) == 0:
            print "\nError: no serial numbers exist for this IEEE address.\n" 
            serial_from_database = None
        elif len(serial_numbers) > 1:
            print "\nError: %s serial numbers exist for this IEEE address." % len(serial_numbers)
            for x in serial_numbers:
                print "     %s" % x
            # serial_number = serial_numbers[0]
            # print "\nserial number: %s \n" % serial_number
            serial_from_database = None
            duplicateEntries = True            
        else:
            serial_from_database = serial_numbers[0]
            print "\nserial number: %s \n" % serial_from_database    

        # print "serial_numbers_internal: %s" % serial_numbers_internal
        if len(serial_numbers_internal) == 0:
            print "\nError: no internal serial numbers exist for this IEEE address." 
            serial_internal_from_database = None
        elif len(serial_numbers_internal) > 1:
            print "\nError: %s internal serial numbers exist for this IEEE address." % len(serial_numbers_internal)
            for x in serial_numbers_internal:
                print "     %s" % x
            # serial_number_internal = serial_numbers_internal[0]
            # print "\nserial number internal: %s \n" % serial_number_internal
            serial_internal_from_database = None
            duplicateEntries = True            
        else:
            serial_internal_from_database = serial_numbers_internal[0]
            print "\nserial number internal: %s \n" % serial_internal_from_database

        # print "serial_numbers_internal: %s" % serial_numbers_internal
        if len(serial_numbers_smt) == 0:
            print "\nError: no SMT serial numbers exist for this IEEE address." 
            serial_smt_from_database = None
        elif len(serial_numbers_smt) > 1:
            print "\nError: %s SMT serial numbers exist for this IEEE address." % len(serial_numbers_internal)
            for x in serial_numbers_smt:
                print "     %s" % x
            # serial_number_internal = serial_numbers_internal[0]
            # print "\nserial number internal: %s \n" % serial_number_internal
            serial_smt_from_database = None
            duplicateEntries = True            
        else:
            serial_smt_from_database = serial_numbers_smt[0]
            print "\nserial number SMT: %s \n" % serial_smt_from_database

    return (ieee_address, serial_from_database, serial_internal_from_database, serial_smt_from_database, duplicateEntries)

def updateDeviceWithInternalSerialNum(ieee, serial_number_internal):
    update = {'device':{'serial_number_internal': serial_number_internal}}

    (status, tries) = updateDeviceWithJSON(ieee, update, "internal")

    if status:
        print "Updated internal serial number in database."
    else:
        print "Did not update internal serial number in database, after %s tries." % tries
    return status

def updateDeviceWithSMTSerialNum(ieee, serial_number_smt):
    update = {'device':{'serial_number_smt': serial_number_smt}}

    (status, tries) = updateDeviceWithJSON(ieee, update, "smt")

    if status:
        print "Updated smt serial number in database."
    else:
        print "Did not update smt serial number in database, after %s tries." % tries
    return status

def updateDeviceWithSerialNumAndPass(ieee, serial_number, passed):
    update = {'device':{'serial_number': serial_number, 'is_passed': passed}}

    (status, tries) = updateDeviceWithJSON(ieee, update, "serial_and_pass")

    if status:
        print "Updated serial number and is_passed in database."
    else:
        print "Did not update serial number and is_passed in database, after %s tries." % tries
    return status

def updateDeviceWithPass(ieee, passed):
    update = {'device':{'is_passed': passed}}

    (status, tries) = updateDeviceWithJSON(ieee, update, "pass")

    if status:
        print "Updated is_passed in database."
    else:
        print "Did not update is_passed in database, after %s tries." % tries
    return status

def updateDeviceWithPhysicals(ieee, physicals):

    update = {'physical': physicals}
    print "\nphysicals:"
    print physicals
    print ""

    (status, tries) = updateDeviceWithJSON(ieee, update, "physicals")

    if status:
        print "Updated physicals in database."
    else:
        print "Did not update physicals in database, after %s tries." % tries
    return status

def updateDeviceWithJSON(ieee, update, post_type):
    status = -1
    tries = 0

    updateJSON = json.dumps(update)

    while status == -1 and tries < MAX_DATABASE_POST_ATTEMPTS:
        if post_type == "internal":
            status = MDapi.misfitProductionUpdateDeviceWithSerialInternal(ieee, updateJSON)
        elif post_type == "smt":
            status = MDapi.misfitProductionUpdateDeviceWithSerialSMT(ieee, updateJSON)
        elif post_type == "physicals":
            status = MDapi.misfitProductionUpdateDevicePhysicals(ieee, updateJSON)
        else:
            status = MDapi.misfitProductionUpdateDeviceWith(ieee, updateJSON)
        if DEBUG_MODE:
            print "Status: %s\n" % status
        tries += 1

    if tries == MAX_DATABASE_POST_ATTEMPTS:
        status = False
    else:
        if DEBUG_MODE:
            print "Status: %s\n" % status        
        status = True

    return (status, tries)

## ---------------------------------------------------------- ##
## Code for posting results to log files and database
## ---------------------------------------------------------- ##

# Store logs that have been posted to database
def logPostedEntry(logEntry, logname):
    filetimestamp = datetime.datetime.utcnow().strftime("%Y_%m_%d_%H%M_%S")    
    device_log_file_name = PATH_TO_LOGS + 'log_posted/' + logname + '_' + filetimestamp + '.log'
    print "Device log file name: %s\n" % device_log_file_name
    device_log_file = open(device_log_file_name, 'a')
    try:
        device_log_file.write(str(logEntry) + '\n')
    finally:
        device_log_file.close()

# Store logs that have not been posted to database
def logUnpostedEntry(logEntry, logname):
    filetimestamp = datetime.datetime.utcnow().strftime("%Y_%m_%d_%H%M_%S")        
    device_log_file_name = PATH_TO_LOGS + 'log_unposted/'+ logname + '_' + filetimestamp + '.log'
    print "Device log file name: %s\n" % device_log_file_name    
    device_log_file = open(device_log_file_name, 'a')
    try:
        device_log_file.write(str(logEntry) + '\n')
    finally:
        device_log_file.close()

def postTestEntryToMFGdb(stationTestObject, misfitDevice):
    tries = 0
    status = ''
    status2 = ''
    status_internal = None
    status_smt = None
    failed = True

    # TRY POSTING THIS ENTRY UP TO 5 TIMES
    if misfitDevice.ieee_address:
        while tries < MAX_DATABASE_POST_ATTEMPTS and failed:
            failed = False
            status = addStationTestToDevice(misfitDevice.ieee_string, stationTestObject)
            if status == '400': # Doesn't exist in DB, so create it
                print "New device; creating database entry."
                status2 = postMisfitDeviceWithStationTest(misfitDevice)
            elif STATION_ID == 1 and UPDATE_INTERNAL_SERIALS_IN_DB:
                print "\nserial_number_internal: %s" % misfitDevice.serial_number_internal
                print "serial_number_smt: %s\n" % misfitDevice.serial_number_smt                
                status_internal = updateDeviceWithInternalSerialNum(misfitDevice.ieee_string, misfitDevice.serial_number_internal)
                status_smt = updateDeviceWithSMTSerialNum(misfitDevice.ieee_string, misfitDevice.serial_number_smt)
                print "\nstatus_internal posting: %s" % status_internal
                print "status_smt posting: %s\n" % status_smt
            if status == -50 or status2 == -50 or status == -1 or status2 == -1:
                failed = True
                print "Timeout in posting to the database on attempt %s.\n" % tries                
                tries += 1
            elif (status != '{}' and status != '400') or (status == '400' and status2 != '{}'):
                failed = True
                print "Failed in posting to the database on attempt %s.\n" % tries
                tries += 1
            # print "Attempt %s %s" % (status, status2)

        if failed == False:
            print "\n..."                                   
            print "Posted after %s retries." % tries
            print "...\n"                                     

        if tries == MAX_DATABASE_POST_ATTEMPTS:
            print "\n...\n...\n..."                                                                    
            print "\nFailed after %s retries." % tries
            print "...\n...\n..."                                             
            print "FAILED STATION - INTERNET?"
            return False
    else:
        print "FAILED STATION - NO IEEE?"
        return False
    return True

def addStationTestToDevice(ieee, stationTestObject):
    # Translate to JSON and post
    testJSON = stationTestObject.jsonize()
    status = MDapi.misfitProductionPostStationTestForDevice(ieee, testJSON)
    print "Status: %s" % status
    return status

def postMisfitDeviceWithStationTest(misfitDevice):
    # Translate to JSON and post
    print ""
    mdJSON = misfitDevice.jsonize()
    print ""
    print "mdJSON: "
    parsed = json.loads(mdJSON)
    print json.dumps(parsed, indent=4)
    print ""
    status = MDapi.misfitProductionPostMisfitDevice(mdJSON)
    print "Status: %s" % status
    return status

## ---------------------------------------------------------- ##
## Code for processing saved log files 
## ---------------------------------------------------------- ##
def processStationLogs():

    numNoPosts = 0
    numPosted = 0
    numUnposted = 0

    log_dirs = {}
    log_dirs['posted'] = PATH_TO_LOGS + 'log_posted/'
    log_dirs['unposted'] = PATH_TO_LOGS + 'log_unposted/'
    log_dirs['no_post'] = PATH_TO_LOGS + 'log_no_post/'

    # List files in unposted directory 
    fnames = os.listdir(log_dirs['unposted'])

    # Create list of logfiles in this directory
    logfiles = []
    for fname in fnames:
        if fname.endswith(".log"):
            logfiles.append(fname)    

    # For each file, update log entry
    for i, logfile in enumerate(logfiles):
        print "\nProcessing %s (log %s/%s)...\n" % (logfile, i, len(logfiles))        
        result = updateStationLogs(logfile, log_dirs)
        if result == -1:
            numNoPosts += 1
        elif result == True:
            numPosted += 1
        else:
            numUnposted += 1

    print "\nDone uploading unposted station logs.\n"
    print "Total files: %s" % len(logfiles)
    print "     # posted: %s" % numPosted
    print "     # not postable: %s" % numNoPosts       
    print "     # still unposted: %s" % numUnposted
    print ""

def updateStationLogs(log_file, log_dirs):

    # For each file, get the log entry
    test_file = open(log_dirs['unposted'] + log_file, 'r')

    # Convert to json
    file_json = json.load(test_file)

    test_file.close()

    # Read from unicode
    station_test_entry = util.convertUnicode(file_json)

    print ""
    pprint(station_test_entry)
    print ""

    # For each file, try to post
    result = postStationEntryLogToDB(station_test_entry)

    # If successfully posted, copy to log_posted directory and remove file from unposted
    if result == -1:
        print "Log file '%s' not postable; moving to log_no_post directory." % log_file
        os.rename(log_dirs['unposted']+log_file, log_dirs['no_post']+log_file)
    elif result == True:
        print "Log file '%s' successfully posted; moving to log_posted directory." % log_file
        os.rename(log_dirs['unposted']+log_file, log_dirs['posted']+log_file)
    else:
        print "Log file '%s' not posted; keeping in log_unposted directory." % log_file

    if DEBUG_MODE:
        choice = raw_input("Hit 'Enter' to continue: ")

    return result

# Tries to post the contents of the log file to the database
def postStationEntryLogToDB(entry):
    # If returns True, post was successful
    # If returns False, internet/database was down, will keep in unposted directory
    # If returns -1, move to log_no_post directory

    tries = 0
    status = ''
    status2 = ''    
    status_internal = None
    status_smt = None    
    failed = True
    postSuccess = True

    serial_number_internal = None
    serial_number_smt = None
    station_id = None

    test_began = entry.has_key('test_began') and entry['test_began'] == True
    not_yet_posted = entry.has_key('mfg_db_post_success') and entry['mfg_db_post_success'] == False
    ieee_read = entry.has_key('ieee_read') and entry['ieee_read'] == True
    has_misfit_device = entry.has_key('misfit_device') and entry['misfit_device']

    if test_began and not_yet_posted and ieee_read and has_misfit_device:
        mdDict = entry['misfit_device'] 
        stationTestDict = mdDict['station_tests']
        ieee = entry['ieee']
        if entry.has_key('station_id'):
            station_id = entry['station_id']
        if mdDict.has_key('serial_number_internal'):
            serial_number_internal = mdDict['serial_number_internal']
        if mdDict.has_key('serial_number_smt'):
            serial_number_smt = mdDict['serial_number_smt']

        # If this log file is for station 2, update the serial number from device
        if station_id == 2:
            serial_from_device = entry['serial_from_device']
            overallPass = entry['overallPass']
            did_updates = False
            if ieee is not None and serial_from_device is not None and overallPass is not None:
                did_updates = updateDeviceWithSerialNumAndPass(ieee, serial_from_device, overallPass)
        # else:
        #     overallPass = entry['overallPass']
        #     did_updates = False
        #     if ieee is not None and overallPass is not None:
        #         did_updates = updateDeviceWithPass(ieee, overallPass)

        mdPost = {}
        mdPost['device'] = mdDict
        stationTestPost = {}
        stationTestPost['station_tests'] = stationTestDict

        # If there is a field here for a test named "Uploaded via Cron Test"
        # Set uploaded_via_cron to true
        cronTestFound = False
        if stationTestDict[0].has_key('individual_tests'):
            indTests = stationTestDict[0]['individual_tests']
            for indTest in indTests:
                if indTest.has_key('name') and indTest['name'] == 'Uploaded via Cron Test':
                    indTest['uploaded_via_cron'] = True
                    cronTestFound = True
                    print indTest
                indTestTimestamp = indTest['timestamp']
            if not cronTestFound:
                indTest = {}
                indTest['name'] = 'Uploaded via Cron Test'
                indTest['timestamp'] = indTestTimestamp
                indTest['is_passed'] = True
                indTest['uploaded_via_cron'] = True
                indTests.append(indTest)

        if ieee:
            while tries < MAX_DATABASE_POST_ATTEMPTS and failed:
                failed = False
                status = MDapi.misfitProductionPostStationTestForDevice(ieee, json.dumps(stationTestPost))
                print "Status: %s" % status

                if status == '400': # Doesn't exist in DB, so create it
                    print "New device; creating database entry."
                    status2 = MDapi.misfitProductionPostMisfitDevice(json.dumps(mdPost))
                elif station_id == 1 and UPDATE_INTERNAL_SERIALS_IN_DB:
                    if mdDict['serial_number_internal'] is not None:
                        status_internal = updateDeviceWithInternalSerialNum(ieee, mdDict['serial_number_internal'])
                    if mdDict['serial_number_smt'] is not None:
                        status_smt = updateDeviceWithSMTSerialNum(ieee, mdDict['serial_number_smt'])
                    print "\nstatus_internal posting: %s" % status_internal
                    print "status_smt posting: %s\n" % status_smt
                    overallPass = entry['overallPass']
                    did_updates = False
                    if ieee is not None and overallPass is not None:
                        did_updates = updateDeviceWithPass(ieee, overallPass)

                if status == -50 or status2 == -50 or status == -1 or status2 == -1:
                    failed = True
                    print "Timeout in posting to the database on attempt %s.\n" % tries                
                    tries += 1
                elif (status != '{}' and status != '400') or (status == '400' and status2 != '{}'):
                    failed = True
                    print "Failed in posting to the database on attempt %s.\n" % tries
                    tries += 1
                # print "Attempt %s %s" % (status, status2)

            if failed == False:
                print "\n..."                                   
                print "Posted after %s retries." % tries
                print "...\n"                                         

            if tries == MAX_DATABASE_POST_ATTEMPTS:
                print "\n...\n...\n..."                                                                    
                print "\nFailed after %s retries." % tries
                print "...\n...\n..."     
                print "FAILED STATION - INTERNET?"                
                postSuccess = False
        else:
            print "No ieee address; not posting."
            postSuccess = -1
    else:
        if not test_began:
            print "test_began = false. No tests run; not posting."
            postSuccess = -1            
        if not not_yet_posted:
            print "Log file already posted; not posting."
            postSuccess = -1            
        if not ieee_read:
            print "No ieee address; not posting."
            postSuccess = -1            
        if not has_misfit_device:
            print "Log file missing misfitDevice field; not posting."
            postSuccess = -1            

    return postSuccess







