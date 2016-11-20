#!/usr/bin/env python
'''
Created on 2015-10-27

@author: James Quen
'''

from segger.updaterController import MainWindowClass
import sys
from PyQt4 import QtGui

def startGui():
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
