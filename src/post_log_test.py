#!/usr/bin/env python
'''
Created on 2014-10-27

@author: Rachel Kalmar
'''

from constants import *
from pprint import pprint
from model.bleDevice import *
from helper.db_commands import *

import os
import collections
import helper.utils as util
import helper.MDapi as MDapi
import time
import datetime
import sys
import json

def testPostStationLog(path_to_log):

    numNoPosts = 0
    numPosted = 0
    numUnposted = 0

    # Get the log entry
    test_file = open(path_to_log, 'r')

    # Convert to json
    file_json = json.load(test_file)

    test_file.close()

    # Read from unicode
    station_test_entry = util.convertUnicode(file_json)

    if 0:
        print ""
        pprint(station_test_entry)
        print ""

    # For each file, try to post
    result = postStationEntryLogToDB(station_test_entry)

    # If successfully posted, copy to log_posted directory and remove file from unposted
    if result == -1:
        print "Log file '%s' not postable." % path_to_log
        numNoPosts += 1        
    elif result == True:
        print "Log file '%s' successfully posted." % path_to_log
        numPosted += 1
    else:
        print "Log file '%s' not posted; keeping in log_unposted directory." % path_to_log
        numUnposted += 1        

    if 0:
        print "\nDone uploading unposted station logs.\n"
        print "Total files: 1"
        print "     # posted: %s" % numPosted
        print "     # not postable: %s" % numNoPosts       
        print "     # still unposted: %s" % numUnposted
        print ""

    return (numPosted, numNoPosts, numUnposted)

def main(argv):
    if len (argv) < 1:
        print "Missing path to log file."
        sys.exit(1)
    if len (argv) < 2:
        numTestPosts = 1
    else:
        numTestPosts = int(argv[1])

    path_to_log = argv[0]
    print path_to_log
    print "Running %s test post(s)" % numTestPosts

    totalNumPosted = 0
    totalNumNotPosted = 0
    totalNumUnposted = 0

    for i in range(numTestPosts):
        print "\nTest %s/%s\n" % (i+1, numTestPosts)
        summary = testPostStationLog(path_to_log)
        totalNumPosted = totalNumPosted + summary[0]
        totalNumNotPosted = totalNumNotPosted + summary[1]
        totalNumUnposted = totalNumUnposted + summary[2]

    print "\n......."
    print "Total # posted: %s" % totalNumPosted
    print "Total # posted: %s" % totalNumNotPosted
    print "Total # unposted: %s" % totalNumUnposted
    print ".......\n"    

if __name__ == "__main__":
    main(sys.argv[1:])

