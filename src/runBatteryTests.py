#!/usr/bin/env python
'''
Created on 2014-09-09

@author: Rachel Kalmar
'''

import helper.posgresDB_extractor as pgdb
from constants import *
from params import *

def main(argv):
    print "num args: %s" % len(argv)
    if len(argv) != 3:
        print "Missing arguments"
        passed = False
        # Save status to file
        sf = open(BATTERY_PASSED_FILE,'w')
        sf.write(str(passed) + '\n')
        sf.close()      
        sys.exit (1)

    serial_number = argv[0]
    startDateStr = argv[1]
    endDateStr = argv[2]

    if serial_number == "None":
        serial_number = None

    input_type = 'cli'

    (bat, reset) = pgdb.getBatteryWithResetData('shine_prod','serial_number', str(serial_number), startDateStr, endDateStr)
    passed = pgdb.plotActivityBatterryReset(bat, reset, input, startDateStr, endDateStr, params)

    # Save status to file
    sf = open(BATTERY_PASSED_FILE,'w')
    sf.write(str(passed) + '\n')
    sf.close()

    return passed

if __name__ == "__main__":
    main(sys.argv[1:])