#!/usr/bin/env python
'''
Created on 2014-07-17

@author: Rachel Kalmar
'''

from helper.utils import shortenPath
from multiprocessing import Array, Process
from multiprocessing.queues import SimpleQueue
from Tkinter import Button, Checkbutton, Entry, Frame, Label, LabelFrame
from Tkinter import IntVar, StringVar
from Tkinter import N, S, E, W, ACTIVE, CENTER, DISABLED, RIDGE, BOTH, Tk
from ttk import Style
from PIL import Image, ImageTk

import os
import time
import tkFileDialog
import tkMessageBox
import Tkinter

DELAY_BEFORE_WINDOW_CLOSE = 0 # Number of seconds before GUI window closes after selecting choice

class GuiBatteryWindow(Frame):

    def __init__(self, master_batt):
        Frame.__init__(self, master_batt)
        self.master_batt = master_batt
        self.__initUi()

    #===========================================================================
    # Initialize and reset GUI
    #===========================================================================
    def __initUi(self):
        self.master_batt.title('Battery Plot')
        self.pack(fill=BOTH, expand=1)

        style = Style().configure("TFrame", background="#333")

        battPlot = ImageTk.PhotoImage(file="view/images/batteryPlot.png")
        label1 = Label(self, image=battPlot)
        label1.image = battPlot
        label1.place(x=0, y=0, width=1500, height=900)

        # Pass and Fail Buttons
        self.fail_button = Button(self, text="Fail", command=self.failed, height=4, width=20, background='red')        
        self.fail_button.place(x=1080, y=850, width=100, height=30)
        self.pass_button = Button(self, text="Pass", command=self.passed, height=4, width=20, background='green')        
        self.pass_button.place(x=1240, y=850, width=100, height=30)        


    def failed(self):

        self.fail_button.config(state=DISABLED)
        self.fail_button.update()

        plot_passed = False

        time.sleep(DELAY_BEFORE_WINDOW_CLOSE)
        self.master_batt.plot_passed = plot_passed
        self.master_batt.quit()
        return

    def passed(self):

        self.pass_button.config(state=DISABLED)
        self.pass_button.update()

        plot_passed = True

        time.sleep(DELAY_BEFORE_WINDOW_CLOSE)
        self.master_batt.plot_passed = plot_passed        
        self.master_batt.quit()
        return 
