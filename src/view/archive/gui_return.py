'''
Created on 19-06-2013

@author: Michael Akilian
'''


from constants import *
from helper.log_utils import writeLog
from helper.utils import shortenPath
from model.dut_parameters import DutParameters
from Tkinter import Button, Checkbutton, Entry, Frame, Label, LabelFrame
from Tkinter import IntVar, StringVar
from Tkinter import N, S, E, W, ACTIVE, CENTER, DISABLED, RIDGE, BOTH
from controler.return_analysis import *
from ttk import Frame, Style

import os
import time
import tkFileDialog
import tkMessageBox


class QRReturnMainWindow(Frame):

    def __init__(self, master):
        Frame.__init__(self, master)
        self.serial_num = StringVar()
        self.master = master
        self.results = StringVar()
        self.__initUi()

    #===========================================================================
    # Initialize and reset GUI
    #===========================================================================
    def __initUi(self):
        self.master.title('Shine Production')
        self.pack(fill=BOTH, expand=1)

        Style().configure("TFrame", background="#333")

        #Status of Test frame
        self.status_frame = LabelFrame(self, text='Status', relief=RIDGE, width=800, height=500)
        self.status_frame.place(x=20, y=20)
        
        #QR SERIAL # Frame
        self.path_frame = LabelFrame(self, text='QR Serial Code', relief=RIDGE, height=60, width=225)
        self.path_frame.place(x=400, y=550)
        entry = Entry(self.path_frame, bd=5, textvariable=self.serial_num)
        entry.place(x=50, y=5)


        #TEST RESULTS LABEL
        w = Label(self.status_frame, textvariable=self.results)
        w.place(x=50, y=50)

        #START Button
        self.start_button = Button(self, text="Start", command=self.start, height=4, width=20)
        self.start_button.place(x=100, y=550)

    def start(self):
        self.start_button.config(state=DISABLED)
        self.start_button.update()
        self.results.set("")
        self.__setStatusLabel(2)
        uiText = ""
        self.results.set(uiText)

        results = executeQRSerialSequence(self.serial_num.get())
        self.parseResults(results)
        
        self.serial_num.set("")
        self.start_button.config(state=ACTIVE)
        self.start_button.update()

    def parseResults(self, results):
        uiText = ''
        success = 1
        print results
        if results == -1:
            success = 3
            uiText += "Something wrong with connection to source meter."
        else:
            if results[SCAN_FAIL] == 1:
                success = 0
                uiText += "Couldn't find Shine \n"

            if results[CHECK_FW_FAIL] == 1:
                success = 0
                uiText += "Invalid firmware version. \n"
                
            if results[ACCEL_STREAM_FAIL] == 1:
                success = 0
                uiText += "Acceleromete data not correct. \n"

            if results[SN_DEFAULT_FAIL] == 1:
                success = 0
                uiText += "This serial # is 9876543210.\n"

            if results[SN_MISMATCH_FAIL] == 1:
                success = 0
                uiText += "Serial # scanned does not match internal (bt) serial #. \n"

            if results[TIMEOUT_FAIL] == 1:
                success = 0
                uiText += "Bluetooth connection timeout. \n"

            if results[AVG_CURRENT_FAIL] == 1:
                success = 0
                uiText += "Average operating current falls outside accepted range for this firmware. \n"

            if results[SN_DUPLICATE_FAIL] == 1:
                success = 0
                uiText += "This Shine is a duplicate serial number. \n"

            if results[RECENTLY_SYNCED_FAIL] == 1:
                success = 0
                uiText += "A Shine with this SN was synced in the past month. \n"

            if results[BATTERY_PLOT_FAIL] == 1:
                success = 0
                uiText += "Human determined battery plots failed."

            if success:
                uiText = "This Shine is in good condition!\n"

        self.results.set(uiText)
        self.__setStatusLabel(success)

    def __setStatusLabel(self, success):
        if success == 1:
            self.status_frame.config(text='SUCCESS', bg=STATUS_OK_COLOR)
        elif success == 2:
            self.status_frame.config(text='Status', bg='yellow')
        elif success == 3:
            self.status_frame.config(text='Something Wrong', bg='blue')
        else:
            self.status_frame.config(text='FAIL', bg=STATUS_ERROR_COLOR)
        self.update()
            

   
