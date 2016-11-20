#!/usr/bin/env python
'''
Created on 2015-07-07

@author: James Quen
'''


import pexpect
import re
import os
from constants import *
from view.gui_run_tests import MainWindowClass
import sys
from PyQt4 import QtGui
 
DIR = "/home/pi/Desktop/FlexFlow/"
UMOUNT_CMD = "umount " + DIR
MOUNT_CMD = "sudo mount.cifs //172.30.31.21/TestFile/RebelTestFile/ATE" + str(STATION_ID) + " " + DIR + " -o user=rebelte,password=rebel@123,sec=ntlm,uid=pi,gid=pi"

def startGui():

    if MANUFACTURER_NAME == 'Endor' and not MFG_DB_STAGING and STATION_ID != 3:

        # If the directory does not exist, create it.
        if not os.path.exists(DIR):
            print "Creating test report directory."
            os.makedirs(DIR) 

        unmount = pexpect.spawn(UMOUNT_CMD, timeout=120)
        unmount.expect(pexpect.EOF)

        mount = pexpect.spawn(MOUNT_CMD, timeout=120)
        mount.expect(pexpect.EOF)
        response = mount.before

        if re.search("error", response):
            print "Error mounting shared drive: " + response
            print "\nTry mounting again by closing and reopening the ATE application."

    app = QtGui.QApplication(sys.argv)
    windowClass = MainWindowClass(None)
    windowClass.show()
    app.exec_()

def usage():
    '''
    TODO
    '''
    pass

def main(options):
    if len(options) == 0:
        usage()

    # Start GUI
    startGui()

if __name__ == "__main__":
    main(sys.argv[1:])
