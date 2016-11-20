#!/usr/bin/env python
'''
Created on 2014-09-09

@author: Rachel Kalmar
'''

from controller.stationTest_commands import *
from constants import *

def main(argv):
    print "num args: %s" % len(argv)
    if len(argv) != 3:
        print "Missing arguments"
        status = 1
        # Save status to file
        sf = open(STATUS_FILE,'w')
        sf.write(str(status) + '\n')
        sf.close()        
        sys.exit (1)

    serial_num = argv[0]
    serial_num_internal = argv[1]
    serial_num_smt = argv[2]

    if serial_num == "None":
        serial_num = None
    if serial_num_internal == "None":
        serial_num_internal = None
    if serial_num_smt == "None":
        serial_num_smt = None

    input_type = 'cli'

    status = executeTestSequence(serial_num, serial_num_internal, serial_num_smt, None, input_type)

    # Save status to file
    sf = open(STATUS_FILE,'w')
    sf.write(str(status) + '\n')
    sf.close()

    return status

if __name__ == "__main__":
    main(sys.argv[1:])