#!/usr/bin/env python
'''
Created on 2015-07-07

@author: James Quen
'''

import sys
import datetime
from gpio_no_sudo import *
import wiringpi2
from subprocess import call
from PyQt4 import QtCore, QtGui, uic

form_class = uic.loadUiType("/home/pi/misfit/ShineProduction/src/helper/mainwindowgpio.ui")[0]

class GpioWindowClass(QtGui.QMainWindow, form_class):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setupUi(self)

        # Initialize the configuration buttons
        self.inputButton.clicked.connect(self.clickedInputButton)
        self.outputButton.clicked.connect(self.clickedOutputButton)
        self.releaseAllPinsPushButton.clicked.connect(self.clickedReleaseAllPinsButton)

        # Initialize set buttons
        self.highButton.clicked.connect(self.clickedHighButton)
        self.lowButton.clicked.connect(self.clickedLowButton)
        self.toggleButton.clicked.connect(self.clickedToggleButton)

        # Initialize pull buttons
        self.upButton.clicked.connect(self.clickedUpButton)
        self.downButton.clicked.connect(self.clickedDownButton)
        self.triButton.clicked.connect(self.clickedTriButton)

        self.isOutput = False

        # Release all GPIOs
        call(["gpio", "unexportall"])

##########################################################################################
# Pin mode configuration
##########################################################################################
    def clickedInputButton(self):
        """
        This function initializes the desired pin as an input.
        """
        self.updateStatus("Clicked input button")
        call(["gpio", "export", str(self.pinLineEdit.text()), "in"])
        self.readPin()

        self.resetAllButtonBackgrounds()

        self.outputButton.setStyleSheet("background-color: white;")
        self.inputButton.setStyleSheet("background-color: gray;")

        self.highButton.setStyleSheet("background-color: white;")
        self.lowButton.setStyleSheet("background-color: white;")
        self.isOutput = False

    def clickedOutputButton(self):
        """
        This function initializes the desired pin as an output.
        """
        self.updateStatus("Clicked output button")
        call(["gpio", "export", str(self.pinLineEdit.text()), "out"])
        self.readPin()

        self.resetAllButtonBackgrounds()

        self.outputButton.setStyleSheet("background-color: gray;")
        self.inputButton.setStyleSheet("background-color: white;")

        self.upButton.setStyleSheet("background-color: white;")
        self.downButton.setStyleSheet("background-color: white;")
        self.triButton.setStyleSheet("background-color: white;")
        self.isOutput = True

    def clickedReleaseAllPinsButton(self):
        """
        This function releases all the GPIO pins and sets all the pins 
        background color to white.
        """
        self.resetAllButtonBackgrounds()
        call(["gpio", "unexportall"])

##########################################################################################
# Setting pins
##########################################################################################
    def clickedToggleButton(self):
        """
        This function toggles the selected pin and updates the 
        pin value label.
        """
        if self.isOutput:
            if not self.isValidPin():
                return

            if int(self.readPin()):
                self.setLow()
            else:
                self.setHigh()

            self.readPin()
        else:
            self.updateStatus("Pin is not an output.  Configure as an output to toggle")


    def setLow(self):
        """
        This function sets the desired pin low.
        """
        gpio_ns_write(int(self.pinLineEdit.text()), "0")

        self.highButton.setStyleSheet("background-color: white;")
        self.lowButton.setStyleSheet("background-color: gray;")

    def setHigh(self):
        """
        This function sets the desired pin high.
        """
        gpio_ns_write(int(self.pinLineEdit.text()), "1")
        self.highButton.setStyleSheet("background-color: gray;")
        self.lowButton.setStyleSheet("background-color: white;")

    def clickedHighButton(self):
        """
        This function sets the desired pin low when clicked
        and updates the pin value label.
        """
        self.updateStatus("Clicked high button")

        if not self.isValidPin():
            return

        self.setHigh()
        self.readPin()

    def clickedLowButton(self):
        """
        This function sets the desired pin low when clicked
        and updates the pin value label.
        """
        self.updateStatus("Clicked low button")

        if not self.isValidPin():
            return

        self.setLow()
        self.readPin()

##########################################################################################
# Setting pull state
##########################################################################################

    def clickedUpButton(self):
        """
        This function sets the pull up on the desired pin and
        updates the pin value label.  Also updates the GUI to reflect
        the selected pin.
        """

        if not self.isOutput:
            self.updateStatus("Clicked up button")
            call(["gpio", "-g", "mode", str(self.pinLineEdit.text()), "up"])
            self.readPin()

            self.upButton.setStyleSheet("background-color: gray;")
            self.downButton.setStyleSheet("background-color: white;")
            self.triButton.setStyleSheet("background-color: white;")
        else:
            self.updateStatus("Pin is not configured as an input.")

    def clickedDownButton(self):
        """
        This function sets the pull down on the desired pin and
        updates the pin value label.  Also updates the GUI to reflect
        the selected pin.
        """
        if not self.isOutput:
            self.updateStatus("Clicked down button")
            call(["gpio", "-g", "mode", str(self.pinLineEdit.text()), "down"])
            self.readPin()

            self.upButton.setStyleSheet("background-color: white;")
            self.downButton.setStyleSheet("background-color: gray;")
            self.triButton.setStyleSheet("background-color: white;")
        else:
            self.updateStatus("Pin is not configured as an input.")

    def clickedTriButton(self):
        """
        This function tri-states the desired pin and
        updates the pin value label.  Also updates the GUI to reflect
        the selected pin.
        """
        self.updateStatus("Clicked tri button")
        call(["gpio", "-g", "mode", str(self.pinLineEdit.text()), "tri"])
        self.readPin()

        self.upButton.setStyleSheet("background-color: white;")
        self.downButton.setStyleSheet("background-color: white;")
        self.triButton.setStyleSheet("background-color: gray;")

##########################################################################################
# Status updates
##########################################################################################
    def isValidPin(self):
        """
        This function checks if the pin is valid.
        Returns True if it is and False if it isn't.
        """
        pin = str(self.pinLineEdit.text())

        if pin == "":
            self.updateStatus("No pin selected")
            return False
        elif int(pin) < 2 or int(pin) > 27:
            self.pdateStatus("Invalid Pin")
            return False

        return True

    def readPin(self):
        """
        This function reads the desired pin value and
        updates the pin value label.
        Returns the pin value.
        """
        pinValue = str(gpio_ns_read(int(self.pinLineEdit.text())))
        self.readLabel.setText(pinValue)
        return pinValue

    def updateStatus(self, status):
        """
        This function updates the status text browser, prepending it with a timestamp.
        """
        self.statusTextBrowser.append(str(datetime.datetime.now()) + ": " + status)

##########################################################################################
# GUI updates
##########################################################################################
    def resetAllButtonBackgrounds(self):
        self.outputButton.setStyleSheet("background-color: white;")
        self.inputButton.setStyleSheet("background-color: white;")

        self.highButton.setStyleSheet("background-color: white;")
        self.lowButton.setStyleSheet("background-color: white;")

        self.upButton.setStyleSheet("background-color: white;")
        self.downButton.setStyleSheet("background-color: white;")
        self.triButton.setStyleSheet("background-color: white;")


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myWindow = GpioWindowClass(None)
    myWindow.show()
    app.exec_()





