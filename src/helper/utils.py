'''
Created on 2014-07-07

@author: Rachel Kalmar
'''

import os, sys, csv
import time
import collections
from constants import *
import re
from multiprocessing import Process
import subprocess
import itertools
import struct


def resetTimer():
    startTime = time.time()
    return startTime

def getTimePassed(startTime):
    return time.time() - startTime

def shortenPath(path):
    l = len(path)
    return path if l <= 40 else path[:25] + '...' + path[l - 10:]

def flattenList(inputList):
    return list(itertools.chain.from_iterable(itertools.repeat(x,1) if isinstance(x,str) else x for x in inputList))

def convertUnicode(data):
    if isinstance(data, basestring):
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(convertUnicode, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(convertUnicode, data))
    else:
        return data

# Wrapper for launching a function in multiple instances
def runParallel(function, iterable, returned_code_list, log_queue):
    process = []
    for i in range(len(iterable)):
        process.append(Process(target=function,
                args=(iterable[i], returned_code_list, log_queue)))
        process[i].start()
    for p in process:
        p.join()

def twosComplement(data):
    if data > 32768:
        data = (65536 - data) * -1
    return data

def writeCSV(filepath, filename, data):
    target_file = generateFileName(filepath, filename, "csv") + ".csv"
    print 'Saving ' + target_file + '...'
    csv.writer(open(target_file, 'w')).writerows(data)

def writePlist(filepath, filename, plist):
    target_file = generateFileName(filepath, filename, "plist") + ".plist"
    print 'Saving ' + target_file + '...'
    try:
        plistlib.writePlist(plist, target_file)
    except:
        print plist
        print target_file
        exit(1)
    print 'CREATING ' + target_file   

def generateFileName(target_folder, filename, dir_name):
    if dir_name:
        return os.path.join(os.path.abspath(target_folder), (dir_name + "/"),
                           (filename)) 
    else:
        return os.path.join(os.path.abspath(target_folder),
                       (filename)) 

def my_dict(obj):
    if not  hasattr(obj,"__dict__"):
        return obj
    result = {}
    for key, val in obj.__dict__.items():
        if key.startswith("_"):
            continue
        if isinstance(val, list):
            element = []
            for item in val:
                element.append(my_dict(item))
        else:
            element = my_dict(val)
        result[key] = element
    return result

def get_git_revision_hash():
    return subprocess.check_output(['git', 'rev-parse', 'HEAD']).strip()

def get_git_revision_short_hash():
    return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).strip()

# Check serial number from GUI or CLI 
def serialNumberCheck(packagingSerialNumber, internalSerialNumber, smtSerialNumber):

    """
    This function needs to check each serial number against the format defined per project.
    Not all serial numbers are required at a station, this function must know which serial number
    is required.
    """
    validInternalSerialNumber = True

    validSerialNumber = True
    
    # Check if the serial number is matched
    if INTERNAL_SN_REQUIRED:
        internalMatched = re.match(MATCHSTR_INTERNAL_REGEX, internalSerialNumber)

        # if the returned value is the same length as the expected serial number length,
        # we have the correct serial number format.
        if internalMatched and len(internalSerialNumber) == SERIAL_NUMBER_LENGTH:
            print "Valid internal serial number (%s)." % internalSerialNumber
            validInternalSerialNumber = True
            
        elif internalMatched == None and len(internalSerialNumber) == 0:
            print "Error: Empty internal (PCBA) serial number."
            validInternalSerialNumber = False
            
        elif internalMatched == None and len(internalSerialNumber) < SERIAL_NUMBER_LENGTH:
            print "Error: Serial number too short. There are only %d digits." % len(internalSerialNumber)
            validInternalSerialNumber = False
            

    validPackagingSerialNumber = True
    
    if PACKAGING_SN_REQUIRED:
        
        packagingMatched = re.match(MATCHSTR_REGEX, packagingSerialNumber)

        if packagingMatched and len(packagingSerialNumber) == SERIAL_NUMBER_LENGTH:
            print "Valid packaging serial number (%s)." % packagingSerialNumber
            validPackagingSerialNumber = True
            
        elif packagingMatched == None and len(packagingSerialNumber) == 0:
            print "Error: Empty packaging serial number."
            validPackagingSerialNumber = False
            
        elif packagingMatched == None and len(packagingSerialNumber) < SERIAL_NUMBER_LENGTH:
            print "Error: Serial number too short. There are only %d digits." % len(packagingSerialNumber)
            validPackagingSerialNumber = False

    if not validPackagingSerialNumber or not validInternalSerialNumber:
        validSerialNumber = False


    return (validSerialNumber, packagingSerialNumber, internalSerialNumber, smtSerialNumber)

"""
# Check serial number from GUI or CLI 
def serialNumberCheck(serial_num, serial_num_internal, serial_num_smt):

    #need to implement new way to check serial numbers.
    if STATION_ID == 1 or STATION_ID == 3 or GET_IEEE_FROM_SERIAL_INTERNAL:
        matchstr_internal = SERIAL_NUM_PREFIX + MATCHSTR_INTERNAL_REGEX        
        match_internal = re.match(matchstr_internal, serial_num_internal)
    else:
        match_internal = True

    if STATION_ID == 1:
        match = True
    else:
        matchstr = SERIAL_NUM_PREFIX + MATCHSTR_REGEX
        match = re.match(matchstr, serial_num)

    # TODO: Add checking for serial_num_smt format here too

    if STATION_ID == 3:                        
        if match and serial_num != "":
            print "Using packaging serial number (%s)." % serial_num
            return (True, serial_num, None, serial_num_smt)
        elif match_internal and serial_num_internal != "":
            print "Using internal serial number (%s)." % serial_num_internal
            return (True, None, serial_num_internal, serial_num_smt)
        else:
            print "Error: serial number (%s) has incorrect format." % serial_num
            return (False, serial_num, serial_num_internal, serial_num_smt)

    if (serial_num != None and serial_num == "" and STATION_ID != 1) or (serial_num_internal != None and serial_num_internal == ""):
        print "Error: empty serial number."
        return (False, serial_num, serial_num_internal, serial_num_smt)
    elif (serial_num != None and serial_num != "" and len(serial_num) < 10) or (serial_num_internal != None and len(serial_num_internal) < 10):
        print "Error: serial number too short."
        return (False, serial_num, serial_num_internal, serial_num_smt)
    elif (serial_num != None and len(serial_num) > 10) or (serial_num_internal != None and len(serial_num_internal) > 10):
        print "Error: serial number too long."
        return (False, serial_num, serial_num_internal, serial_num_smt)
    elif match_internal == None:
        print "Error: internal serial number (%s) has incorrect format." % serial_num_internal            
        return (False, serial_num, serial_num_internal, serial_num_smt)
    elif STATION_ID == 2 and match == None:
        print "Error: serial number (%s) has incorrect format." % serial_num
        return (False, serial_num, serial_num_internal, serial_num_smt)
    else: 
        if not (STATION_ID == 2 and not GET_IEEE_FROM_SERIAL_INTERNAL):
            print "Valid internal serial number (%s)." % serial_num_internal            
        if STATION_ID == 2:
            print "Valid serial number (%s)." % serial_num                
        return (True, serial_num, serial_num_internal, serial_num_smt)
"""


# Create list structure for creating lists of ATE tests
def createTestOrder(testList):
    testOrder = []
    testIndex = 0
    for testName in testList:
        test = {}
        testIndex +=1
        test['name'] = testName
        test['testFunction'] = testNameMap[testName]
        test['index'] = testIndex
        testOrder.append(test)
    return testOrder


def convertInt16ToBytesLe(number=0):
    """
    This function converts an int16 to bytes in little endian format
    """
    l = [hex(number >> i & 0xff)[2:].zfill(2) for i in (8, 0)]
    l = l[::-1]

    b = ""
    for h in l:
        b += h.decode('hex')
    return b

def convertUint32ToBytesLe(number=0):
    """
    This function converts an int32 to bytes in little endian format
    """
    l = [hex(number >> i & 0xff)[2:].zfill(2) for i in (24, 16, 8, 0)]
    l = l[::-1]

    b = ""
    for h in l:
        b += h.decode('hex')
    return b

def deviceColorLookup(colorCode=''):

    if STATION_ID == 1:
        print "No device color information for Station 1."
        return None

    color = ''

    if colorCode in colorMap:
        color = colorMap[colorCode]
    else:
        print "Warning, color code ""%s"" for %s unknown.\n" % (colorCode, DEVICE_TYPE)
        color = None

    return color

def brandLookup(serial_number=''):
    if STATION_ID == 1 or STATION_ID == 2:
        print "No brand information for Station 1."
        return None

    brandCode = serial_number[3] # get the third and fourth characters for 
    brand = ''

    if brandCode in brandMap:
        brand = brandMap[brandCode]


    else:
        print "Warning, brand ""%s"" for %s unknown.\n" % (brandCode, DEVICE_TYPE)
        brand = None

    return brand