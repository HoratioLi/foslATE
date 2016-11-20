#! /usr/bin/env python

'''
Created on 2015-06-01
@author: James Quen
'''

from constants import *
import os
DIRECTORY = "/home/pi/Desktop/FlexFlow/"

def createTestReport(results, failedTests):
    """
    This function is used to generate reports of test results.
    The format of the file name is:
    <internal serial number>_<YYYYMMDDhhmmss>.TXT

    The format of the reports are as follows:

    For Passing:
    <project>ATE<STATION_ID>-<STATION_INDEX>;
    MSN:<Module serial number>; This is for ATE 3
    SN:<internal serial number>;
    Status:Pass;

    For Failing:
    <project>ATE<STATION_ID>-<STATION_INDEX>;
    MSN:<Module serial number>; This is for ATE 3
    SN:<internal serial number>;
    Status:Fail;
    FailureCode:<Test1>,<Test2>,etc...;
    """
	
    # If the directory does not exist, create it.
    if not os.path.exists(DIRECTORY):
        print "Creating test report directory."
        os.makedirs(DIRECTORY) 

    serialNumber = ""

    if STATION_ID == 3:
        serialNumber = results['serial_number']
    else:
        serialNumber = results['serial_number_internal']


    fileName = serialNumber + "_" + results['end_time'] + ".txt"

    result_print = ""

    # Construct the string as <project>ATE<STATION_ID>-<STATION_INDEX>;SN:xxxxxxxxxx;Status:
    if STATION_ID == 3:
        result_print = DEVICE_TYPE + "ATE" + str(STATION_ID) + "-" + str(STATION_INDEX) + ";MSN:" + results['serial_number_internal'] + ";SN:" + serialNumber + ";Status:"
    else:
        result_print = DEVICE_TYPE + "ATE" + str(STATION_ID) + "-" + str(STATION_INDEX) + ";SN:" + serialNumber + ";Status:"

    if len(failedTests) == 0:
        result_print +="Pass;"
        print "Writing the following to file: \n" + result_print
    else:
        result_print += "Fail;FailureCode:"
        numberOfTests = len(failedTests)

        for test in failedTests:
            testName = test.name.split()
            result_print += "_".join(testName).upper()

            numberOfTests -= 1

            if numberOfTests != 0:
                result_print += ","

        result_print += ";"
        print "Writing the following to file: \n" + result_print


    print "Creating file: " + fileName

    f = open(DIRECTORY + fileName, "w")

    f.write(result_print)
    f.close()