#!/usr/bin/env python
'''
Created on 2015-10-12

@author: James Quen
'''

import time
import re
import sys
import pexpect
import subprocess
import datetime
from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtCore import QThread, SIGNAL
from constants import *

# Add the path to the utilities module.
sys.path.append("/home/pi/misfit/ShineProduction/src/utilities")

from utilities.gitCommands import *

# Load the .ui file.
form_class = uic.loadUiType("/home/pi/misfit/ShineProduction/src/segger/updater.ui")[0]

class performUpdate(QThread):
    """
    This class handles the update in a separate thread in order to not block the main thread
    from updating the GUI.
    """

    def __init__(self):
        """
        This function initializes the thread.
        """

        QThread.__init__(self)

    def __del__(self):
        """
        This function tells the thread to wait.
        """

        self.wait()

    def _updateGUI(self, message, color, progress):
        """
        This function emits to the SIGNAL when the GUI needs to be updated.
        """
        self.emit(SIGNAL('updateStatus(QString)'), message)
        self.emit(SIGNAL('updateStatusColor(QString)'), color)
        self.emit(SIGNAL('updateProgressBar(int)'), progress)

    def run(self):
        """
        The updateFlasher function performs the upgrade of the SEGGER flasher.  
        It checks for connection to the flasher and if the programming was successful.
        It also updates the GUI as it progresses.
        """

        # Error code of 0 indicates successful programming.
        errorCode = 0

        # The message to return to the GUI.
        message = ""

        # The response of the git command.
        response = 0

        # git hard reset to be able to pull and fetch.  If there is an uncommitted file, a git pull is not permitted.
        self._updateGUI("Resetting commit", "white", 1)
        gitHardReset()

        # Delete all tags because we will fetch the latest tags later.
        self._updateGUI("Deleting tags", "white", 2)
        gitDeleteAllTags()

        # git pull to get latest branch update
        self._updateGUI("Getting updates", "white", 3)
        (response, message) = gitPull(gitGetCurrentBranchName())

        if response == 0:

            self._updateGUI("Getting latest tags", "white", 4)
            #git fetch to get latest tags
            (response, message) = gitFetch()

            if response == 0:

                COMMAND_PROMPT = "J-Link\>"
                EXECUTABLE = "/home/pi/misfit/ShineProduction/src/segger/./JLinkExe"
                DATA_FILE = "/home/pi/misfit/ShineProduction/src/segger/FLASHER_" + DEVICE_TYPE + ".DAT"
                CONFIG_FILE = "/home/pi/misfit/ShineProduction/src/segger/FLASHER_" + MCU + ".CFG"

                # Perform lsusb | grep SEGGER to see if SEGGER is connected.  If it's not connected, return an error code of -1.
                # TODO: Write a function that handles command line with pipe(s)
                lsusb = subprocess.Popen("lsusb", stdout=subprocess.PIPE)
                grep = subprocess.Popen("grep SEGGER".split(), stdin=lsusb.stdout, stdout=subprocess.PIPE)
                lsusb.stdout.close()
                output = grep.communicate()[0]
                lsusb.wait()

                # Check the output
                output = " ".join(output.split()[-3:])

                # If SEGGER is connected and station is ATE 1
                # Allow to program the SEGGER is connected.
                if output == "SEGGER J-Link ARM" and (STATION_ID == 1 or (STATION_ID == 2 and DEVICE_TYPE == 'SAM')):
                    self._updateGUI("Found flasher", "white", 5)

                    # Run the JLink executable
                    child = pexpect.spawn(EXECUTABLE)

                    # Expect the command prompt
                    child.expect(COMMAND_PROMPT)

                    # Write file <file name on flasher to write> <local file name to write>
                    child.sendline("fwr FLASHER.DAT " + DATA_FILE)

                    # Expect the command prompt
                    child.expect(COMMAND_PROMPT)

                    # Write file <file name on flasher to write> <local file name to write>
                    child.sendline("fwr FLASHER.CFG " + CONFIG_FILE)

                    # Expect the command prompt
                    child.expect(COMMAND_PROMPT)

                    # Get the programming status
                    programmingStatus = " ".join(child.before.split()[-2:])

                    # Check the status of programming.  If it fails to program, print out the error and return error code of -2.
                    if programmingStatus == "written successfully.":

                        # Get the tags for this commit.
                        message = gitGetTagsOnThisCommit()

                        # Search for the tag that ends in '.ship_mode'
                        for tag in message:
                            if re.search("\.ship_mode", tag) or re.search("\.prod", tag):
                                message = "Programming is successful with " + tag + "."
                                break
                            else:
                                message = "Programming is successful without firmware version name.  Contact Rebel for confirmation of update."
                                message += " The commit hash is " + gitGetCommitHash()

                        self._updateGUI(message, "white", 5)
                        
                        # Search for the tag that starts with 'ATE.'
                        for tag in gitGetTagsOnThisCommit():
                            if re.search("ATE\.", tag):
                                message = "ATE version is now " + tag + "."
                                break
                            else:
                                message = "ATE software updated with out version name.  Contact Rebel for confirmation of update."
                                message += " The commit hash is " + gitGetCommitHash()

                        self._updateGUI(message, "green", 6)
                    else:
                        # Print out the error message.
                        message = child.before.split('\r\n')[-2]
                        self._updateGUI(message, "red", 6)

                    # Quit JLink exe.
                    child.sendline("q")
                # If it's ATE 2, end the upgrade.
                elif STATION_ID == 1.5 or STATION_ID == 2 or STATION_ID == 3:
                    # Get the tags for this commit.
                    message = gitGetTagsOnThisCommit()
                    # Search for the tag that starts with "ATE."
                    for tag in message:
                        if re.search("ATE\.", tag):
                            message = "ATE version is now " + tag + "."
                            break
                        else:
                            message = "ATE software updated with out version name.  Contact Rebel for confirmation of update."
                            message += " The commit hash is " + gitGetCommitHash()

                    self._updateGUI(message, "green", 6)
                else:
                    message = "SEGGER is not connected.  Please connect SEGGER directly to ATE."
                    self._updateGUI(message, "red", 6)
            else:
                # git fetch failed.
                self._updateGUI(message + "\nCheck network settings or connection.", "red", 6)
        else:
            # git pull failed.
            self._updateGUI(message + "\nCheck network settings or connection.", "red", 6)



class MainWindowClass(QtGui.QMainWindow, form_class):
    """
    This class is the controller of the application that programs the flasher.
    The firmware version is updated through git.  The SEGGER flasher needs to be connected to ATE
    directly for the update.
    """

    def __init__(self, parent=None):
        """
        This function initializes the GUI and connects buttons to functions.
        """

        QtGui.QMainWindow.__init__(self, parent)
        self.setupUi(self)

        # Connect buttons to functions
        self.programButton.clicked.connect(self.programButtonClicked)
        self.doneButton.clicked.connect(self.doneButtonClicked)

        # Initialize status text box.
        self.statusTextBrowser.setText("")
        self.statusTextBrowser.setStyleSheet("background-color: white;")

        self.progressBar.hide()


    def programButtonClicked(self):
        """
        This function initializes text box, progress bar, and thread and SIGNAL connections.
        Then it calls the upgrade function.
        """

        # Clear text in status box.
        self.statusTextBrowser.setText("")

        # Show the progress bar.
        self.progressBar.show()

        # Set the maximum value of progress bar, can be any int and it will
        # be automatically converted to x/100% values
        self.progressBar.setMaximum(6)

        # Setting the value on every run to 0
        self.progressBar.setValue(0)

        self.getThread = performUpdate()

        # Connect thread to SIGNALs.
        self.connect(self.getThread, SIGNAL("updateStatus(QString)"), self.updateStatus)
        self.connect(self.getThread, SIGNAL("updateProgressBar(int)"), self.updateProgressBar)
        self.connect(self.getThread, SIGNAL("updateStatusColor(QString)"), self.updateStatusColor)

        # We have all the events we need connected we can start the thread
        self.getThread.start()

    def doneButtonClicked(self):
        """
        This function closes the application.
        """

        QtCore.QCoreApplication.instance().quit()

    def updateStatus(self, status, color="white", progress=0):
        """
        This function updates the status text box with the date, time, and status.
        """

        self.statusTextBrowser.append(str(datetime.datetime.now()) + ": " + status)

    def updateProgressBar(self, progress):
        """
        This function updates the progress bar.
        """

        # If max_value = 3, current_value = 1, the progress bar will show 33%
        self.progressBar.setValue(progress)

    def updateStatusColor(self, color):
        """
        This function updates the color status.
        """

        # Update the color of the status text box.
        self.statusTextBrowser.setStyleSheet("background-color: %s;" % color)







