#!/usr/bin/env python
'''
Created on 2015-07-07

@author: James Quen
'''


from constants import *
from controller.stationTest_commands import *
from controller.raspberryPi_commands import *
from helper.utils import shortenPath, serialNumberCheck
from helper.agilent_34461 import A34461
from helper.gpio_no_sudo import *
from multiprocessing import Array, Process
from multiprocessing.queues import SimpleQueue

import os
import time
import re
import subprocess
import sys
from PyQt4 import QtCore, QtGui, uic

log_queue = SimpleQueue()
form_class = uic.loadUiType("/home/pi/misfit/ShineProduction/src/view/mainwindow.ui")[0]

class MainWindowClass(QtGui.QMainWindow, form_class):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
    	self.setupUi(self)
    	self.startButton.clicked.connect(self.start) 
        self.resetPushButton.clicked.connect(self.clickedResetPushButton) 
        self.startButton.setStyleSheet("background-color: green;")

        self.totalTestsRunCount = 0
        self.totalTestsPassedCount = 0
        self.totalTestsFailedCount = 0

        if MANUFACTURER_NAME != "GT":
            self.label.hide()
            self.label_4.hide()
            self.label_6.hide()
            self.resetPushButton.hide()
            self.totalTestsFailedLabel.hide()
            self.totalTestsPassedLabel.hide()
            self.totalTestsRunLabel.hide()

        title = "ATE Station %s-%s" % (STATION_ID, STATION_INDEX) 
    	self.setWindowTitle(title)	

    	self.input1CheckBox.hide()
    	self.input2CheckBox.hide()
        self.input2LineEdit.hide()
        self.input2Label.hide()
    	#self.scannedLineEdit.setFocus()
        self.input1LineEdit.setFocus()

    	internalRegEx = QtCore.QRegExp(SERIAL_NUM_PREFIX + MATCHSTR_INTERNAL_REGEX)
        internalValidator = QtGui.QRegExpValidator(internalRegEx)	
    	packagingRegEx = QtCore.QRegExp(SERIAL_NUM_PREFIX + MATCHSTR_REGEX)
    	packagingValidator = QtGui.QRegExpValidator(packagingRegEx)

        if STATION_ID == 1 or STATION_ID == 1.5 or (STATION_ID == 2 and DEVICE_TYPE == 'SAM'):
    	    self.input1Label.setText("Internal Serial Number (PCB)")

            if MANUFACTURER_NAME != "VS":
                self.input2Label.show()
                self.input2Label.setText("SMT Serial Number")
                self.input2LineEdit.show()
            else:
                self.input1Label.setText("Serial Number")

    	    self.input1LineEdit.setValidator(internalValidator)
            self.input2LineEdit.setMaxLength(11)
        elif STATION_ID == 2:
            if GET_IEEE_FROM_SERIAL_INTERNAL and DEVICE_TYPE != "BMW":
                self.input1Label.setText("Internal Serial Number (PCB)")
    	    else:
                self.input1Label.hide()
                self.input1LineEdit.hide()

            if MANUFACTURER_NAME != "VS":
                self.input2Label.show()
                self.input2LineEdit.show()
                self.input1LineEdit.setValidator(internalValidator) 
                self.input2Label.setText("Packaging Serial Number")
                self.input2LineEdit.setValidator(packagingValidator)
            else:
                self.input1Label.setText("Serial Number")
                self.input2Label.hide()
                self.input2LineEdit.hide()
                self.input1LineEdit.setValidator(internalValidator)

        elif STATION_ID == 3:

            if MANUFACTURER_NAME == 'VS' or DEVICE_TYPE == 'SAM':
                # Setup the Internal serial number label and line edit input
                self.input1Label.setText("Internal Serial Number (PCB)")
                self.input1LineEdit.show()
                self.input1LineEdit.setValidator(internalValidator)

                # Setup the packaging serial number length and line edit input
                self.input1LineEdit.setMaxLength(SERIAL_NUMBER_LENGTH)
                self.input2LineEdit.setMaxLength(SERIAL_NUMBER_LENGTH)
                self.input2Label.setText("Packaging Serial Number")
                self.input2Label.show()
                self.input2LineEdit.show()
                self.input2LineEdit.setValidator(packagingValidator)
            else:
                self.input1Label.setText("Serial Number (PCB or Packaging)")
                self.input2Label.hide()
                self.input2LineEdit.hide() 

        #self.scannedLineEdit.textChanged.connect(self.textHasChanged)
        gpio_ns_config(POGOPIN_TEST_PIN, "out")

    def updateGui(self):
        QtGui.QApplication.processEvents()
        self.totalTestsRunLabel.setText(str(self.totalTestsRunCount))
        self.totalTestsPassedLabel.setText(str(self.totalTestsPassedCount))
        self.totalTestsFailedLabel.setText(str(self.totalTestsFailedCount))

    def keyPressEvent(self, event):
    	"""
     	This function detects if the Enter or Return key is pressed and calls the 
    	start() function.	
    	"""	
    	if event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return:
    	    self.start()

    def clickedResetPushButton(self):
        self.totalTestsRunCount = 0
        self.totalTestsPassedCount = 0
        self.totalTestsFailedCount = 0
        self.updateGui()

    def textHasChanged(self):
        inputString = str(self.sender().text())	
        internalRegEx = re.compile(SERIAL_NUM_PREFIX + MATCHSTR_INTERNAL_REGEX)
        packagingRegEx = re.compile(SERIAL_NUM_PREFIX + MATCHSTR_REGEX) 

       	if internalRegEx.match(inputString):
       	    self.input1LineEdit.setText(inputString)
            self.scannedLineEdit.setText("")
            self.scannedLineEdit.setFocus()	    
        elif packagingRegEx.match(inputString) and (STATION_ID != 1):
            if STATION_ID == 3:
                self.input1LineEdit.setText(inputString)
            elif STATION_ID == 2:
                self.input2LineEdit.setText(inputString)
    	    self.scannedLineEdit.setText("")
    	    self.scannedLineEdit.setFocus()
        	
    	elif len(inputString) > 9:
    	    self.statusTextBrowser.setText(inputString + " is an invalid serial number!")
    	    self.scannedLineEdit.setText(inputString[1:])
    	    self.scannedLineEdit.setFocus()
		
    def start(self):
    	testsFailed = None
    	self.__setStatusLabel(4)
        self.updateGui()

        if STATION_ID == 1 or STATION_ID == 1.5 or (STATION_ID == 2 and DEVICE_TYPE == 'SAM'):
            self.serial_num_internal = self.input1LineEdit.text()
            serial_num_internal = str(self.input1LineEdit.text())

            # Add in special setup for CES testing
            if STATION_INDEX == -2:
                self.serial_num_smt.set(None)
                serial_num_smt = None
                self.serial_num.set(self.entry_2.get())
                serial_num = self.entry_2.get()
            else:
                self.serial_num_smt = self.input2LineEdit.text()
                serial_num_smt = str(self.input2LineEdit.text())
                self.serial_num = None
                serial_num = None

        elif STATION_ID == 2:
            if GET_IEEE_FROM_SERIAL_INTERNAL:
                self.serial_num_internal = self.input1LineEdit.text()
                serial_num_internal = str(self.input1LineEdit.text())
            else:
                self.serial_num_internal = None
                serial_num_internal = None

            if MANUFACTURER_NAME != "VS":
                self.serial_num = self.input2LineEdit.text()
                serial_num = str(self.input2LineEdit.text())
            else:
                self.serial_num = self.input1LineEdit.text()
                serial_num = str(self.input1LineEdit.text())
            self.serial_num_smt = None 
            serial_num_smt = None
        elif STATION_ID == 3:
            self.serial_num_internal = self.input1LineEdit.text()
            serial_num_internal = str(self.input1LineEdit.text())
            self.serial_num = self.input2LineEdit.text() 
            serial_num = str(self.input2LineEdit.text())
            self.serial_num_smt = None
            serial_num_smt = None

        dut_parameters = None   # Legacy -- can get rid of this variable eventually



        (validSerialNumber, serial_num, serial_num_internal, serial_num_smt) = serialNumberCheck(serial_num, serial_num_internal, serial_num_smt)

        if validSerialNumber:

            # Check whether operating current directory exists
            if (STATION_ID == 2 or STATION_ID == 3) and (SAVE_OP_CURRENT_CSV or SAVE_OP_CURRENT_PNG):
                subprocess.call("/home/pi/misfit/ShineProduction/src/scripts/checkOpCurrDirectory.sh")

            if CLI_MODE:
                if serial_num is None:
                    serial_num = "None"
                if serial_num_internal is None:
                    serial_num_internal = "None"
                if serial_num_smt is None or serial_num_smt == "":
                    serial_num_smt = "None"
                print "\nserial_num: %s" % serial_num
                print "serial_num_internal: %s" % serial_num_internal
                print "serial_num_smt: %s\n" % serial_num_smt
                subprocess.call(["/home/pi/misfit/ShineProduction/src/scripts/runStationTests.sh", serial_num, serial_num_internal, serial_num_smt],stderr=subprocess.STDOUT)
                # Read status from file
                sf = open(STATUS_FILE,'r')
                status = int(sf.readline())
                sf.close()
                # print "\n....\n....\n....\nCLI status returned: %s\n....\n....\n....\n" % status
            else:
                # Set current local time
                os.environ['TZ'] = TIMEZONE
                time.tzset()
                curr_time = datetime.datetime.now()
                print "\nCurrent local time is %s\n" % datetime.datetime.strftime(curr_time,"%Y-%m-%d %H:%M:%S")

                # Initialize the Agilent 34461
                instr = A34461(AGILENT_BASE_ADDRESS, AGILENT_SUB_ADDRESS)
                if instr.instr is not None:
                    try:
                        instr.setModeToCurrent()
                    except:
                        print "Warning: can't set mode to current -- please check Agilent connection"
                        instr.instr = None

                # Initialize the DUT
                initDUT()

		
                input_type = 'normal'
                (status, testsFailed) = executeTestSequence(serial_num, serial_num_internal, serial_num_smt, instr, input_type)
        else:
            status = 3
        print 'Status: {}'.format(status)
        # dut_parameters.logStatus(status)
        self.__setStatusLabel(status, testsFailed)

        #self.serial_num_smt.set("")
        #self.serial_num.set("")
        #self.serial_num_internal.set("")
        #self.start_button.config(state=ACTIVE, background='green')
        #self.start_button.update()
        self.input1LineEdit.setText("")
        self.input2LineEdit.setText("")
        self.scannedLineEdit.setText("")
        self.input1LineEdit.setFocus()	

    def __setStatusLabel(self, success, testsFailed=None):
        if success == 0:
            self.statusTextBrowser.setText("SUCCESS")
            self.statusTextBrowser.setStyleSheet("background-color: green;")
            self.totalTestsPassedCount += 1
            self.totalTestsRunCount += 1
            print ""
            print "Success!"
            print ""
        elif success == 2:
            self.statusTextBrowser.setText('Tests succeeded, Raspberry Pi not connected to internet')
            self.statusTextBrowser.setStyleSheet("background-color: yellow;") 
            print ""
            print "Tests succeeded, Raspberry Pi not connected to internet."
            print ""
        elif success == 3:
            self.statusTextBrowser.setText("Invalid serial number! Try rescanning the barcode.")
            self.statusTextBrowser.setStyleSheet("background-color: blue;") 
            print ""
            print "Check errors"
            print ""
        elif success == 4:
            self.statusTextBrowser.setText("Tests running...")
            self.statusTextBrowser.setStyleSheet("background-color: gray;")
        elif success == 5:
            self.statusTextBrowser.setText(testsFailed)

            self.statusTextBrowser.setStyleSheet("background-color: yellow;") 
            self.updateGui()
            time.sleep(1)
            self.statusTextBrowser.setStyleSheet("background-color: gray;")
            self.updateGui()
            time.sleep(1)
            self.statusTextBrowser.setStyleSheet("background-color: yellow;") 
        else:
            errorMessage = "Tests Failed:\n"
            self.totalTestsFailedCount += 1
            self.totalTestsRunCount += 1
            for test in testsFailed:
                errorMessage += test.name + " " + str(vars(test)) + "\n"
            self.statusTextBrowser.setText(errorMessage)
            self.statusTextBrowser.setStyleSheet("background-color: red;") 
	    print ""
            print "Tests failed"
            print ""
        print "\n==============================================================\n"
        self.updateGui()
       
