#!/usr/bin/env python
'''
Created on 2015-07-07

@author: James Quen
'''

import sys
import datetime
from agilent_34461 import A34461
from PyQt4 import QtCore, QtGui, uic

form_class = uic.loadUiType("/home/pi/misfit/ShineProduction/src/helper/mainwindowdmm.ui")[0]

class DmmWindowClass(QtGui.QMainWindow, form_class):
    def __init__(self, parent=None):
		QtGui.QMainWindow.__init__(self, parent)
		self.setupUi(self)

		self.dcVoltageButton.clicked.connect(self.clickedVoltageButton)
		self.dcCurrentButton.clicked.connect(self.clickedCurrentButton)
		self.twoWireResistanceButton.clicked.connect(self.clickedResistanceButton)
		self.singleReadButton.clicked.connect(self.clickedReadButton)
		self.dmm = A34461(2391, 6663)
		self.type = ""

    def clickedVoltageButton(self):
		self.updateStatus("Configured to measure DC voltage")
		self.dmm.setModeToVoltage()
		self.typeLabel.setText("DC Voltage:")
		self.type = "voltage"

    def clickedCurrentButton(self):
		self.updateStatus("Configured to measure DC current")
		self.dmm.setModeToCurrent()
		self.typeLabel.setText("DC Current:")
		self.type = "current"

    def clickedResistanceButton(self):
		self.updateStatus("Configured to measure 2 wire resistance")
		self.dmm.setModeToResistance()
		self.typeLabel.setText("Resistance:")
		self.type = "resistance"

    def clickedReadButton(self):
		value = str(self.dmm.getReading())

		if self.type == "voltage":
		    value += " V"
		elif self.type == "current":
		    value += " A"
		elif self.type == "resistance":
		    value += " Ohms"        		

		self.valueLabel.setText(value)
		self.updateStatus("Reading " + value)

    def updateStatus(self, status):
		self.statusTextBrowser.append(str(datetime.datetime.now()) + ": " + status)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = DmmWindowClass(None)
    window.show()
    app.exec_()


