#!/usr/bin/env python
'''
Created on 2014-09-03

@author: Rachel Kalmar
'''


from constants import *
# from controller.stationTest_commands import *
from controller.raspberryPi_commands import *
from helper.utils import serialNumberCheck
from helper.agilent_34461 import A34461
# from multiprocessing import Array, Process
# from multiprocessing.queues import SimpleQueue

import os, sys
import time
import subprocess

USAGE_TEXT = """
Usage: python cli_run_tests.py <SERIAL_NUMBER> <SERIAL_NUMBER_INTERNAL> <SERIAL_NUMBER_SMT>
"""

def setStatusLabel(success):
    if success == 0:
        print ""
        print "Success!"
        print ""
    elif success == 2:
        print ""
        print "Tests succeeded, Raspberry Pi not connected to internet."
        print ""
    elif success == 3:
        print ""
        print "Check errors"
        print ""            
    elif success == 4:
        print ""
        print "Tests running"
        print ""     
    else:
        print ""
        print "Tests failed"
        print ""

def main(argv):
    if len (argv) != 3:
        print "Missing arguments"
        sys.exit (1)

    serial_num = argv[0]
    serial_num_internal = argv[1]
    serial_num_smt = argv[2]

    (validSerialNumber, serial_num, serial_num_internal, serial_num_smt) = serialNumberCheck(serial_num, serial_num_internal, serial_num_smt)

    print "\nvalidSerialNumber: %s" % validSerialNumber
    print "serial_num: %s (%s)" % (serial_num, len(serial_num))
    print "serial_num_internal: %s (%s)" % (serial_num_internal, len(serial_num_internal))
    print "serial_num_smt: %s (%s)\n" % (serial_num_smt, len(serial_num_smt))

    if len(serial_num) == 0:
        serial_num = "None"
    if len(serial_num_internal) == 0:
        serial_num_internal = "None"
    if len(serial_num_smt) == 0:
        serial_num_smt = "None"

    if validSerialNumber:

        # Check whether operating current directory exists
        if (STATION_ID == 2 or STATION_ID == 3) and (SAVE_OP_CURRENT_CSV or SAVE_OP_CURRENT_PNG):
            subprocess.call("/home/pi/misfit/Production/src/scripts/checkOpCurrDirectory.sh")    
        if CLI_MODE:
            status = subprocess.call(["/home/pi/misfit/Production/src/scripts/runStationTests.sh", serial_num, serial_num_internal, serial_num_smt])        
            print "\n....\n....\n....\nCLI status returned: %s\n....\n....\n....\n" % status
        else:
            # Set current local time
            os.environ['TZ'] = TIMEZONE
            time.tzset()
            curr_time = datetime.datetime.now()
            print "\nCurrent local time is %s\n" % datetime.datetime.strftime(curr_time,"%Y-%m-%d %H:%M:%S")

            # Initialize the Agilent 34461
            instr = A34461(AGILENT_BASE_ADDRESS, AGILENT_SUB_ADDRESS)
            if instr.instr is not None:
                instr.setModeToCurrent()

            # Initialize the DUT
            initDUT()

            input_type = 'normal'
            status = executeTestSequence(serial_num, serial_num_internal, serial_num_smt, instr, input_type)

    else: 
        status = 3
    
    print 'Status: {}'.format(status)

    setStatusLabel(status)

if __name__ == "__main__":
    main(sys.argv[1:])

