#!/usr/bin/env python
'''
Created on 2015-04-21

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
from Tkinter import Button, Checkbutton, Entry, Frame, Label, LabelFrame
from Tkinter import IntVar, StringVar, BooleanVar
from Tkinter import N, S, E, W, ACTIVE, CENTER, DISABLED, RIDGE, BOTH
from ttk import Frame, Style

import os
import time
import tkFileDialog
import tkMessageBox
import re
import subprocess

log_queue = SimpleQueue()

class GuiMainWindow(Frame):

    def __init__(self, master):
        Frame.__init__(self, master)
        self.serial_num = StringVar()
        self.gpioPin = StringVar()
        self.serial_num_smt = StringVar()
        self.master = master
        self.results = StringVar()
        self.debug_mode = BooleanVar()
        self.__initUi()

    #===========================================================================
    # Initialize and reset GUI
    #===========================================================================
    def __initUi(self):
        self.master.title('GPIO Test')
        self.pack(fill=BOTH, expand=1)

        Style().configure("TFrame", background="#333")

        # Status of Test frame
        self.status_frame = LabelFrame(self, text='Status', relief=RIDGE, width=235, height=100)
        self.status_frame.place(x=20, y=20)

        self.path_frame_1 = LabelFrame(self, text='GPIO Pin (between 0 and 27)', relief=RIDGE, height=60, width=235)
        self.path_frame_1.place(x=20, y=150)
        self.entry_1 = Entry(self.path_frame_1, bd=5, textvariable=self.gpioPin)
        self.entry_1.place(x=20, y=5)
        self.entry_1.focus_set()

        # TEST RESULTS LABEL
        w = Label(self.status_frame, textvariable=self.results)
        w.place(x=50, y=50)

        # Toggle Button
        self.toggleButton = Button(self, text="Toggle", command=self.toggle, height=4, width=20, background='green')
        self.toggleButton.place(x=20, y=250)
        self.toggleButton.bind('<Return>', lambda e:self.hi())

        self.isHi = False
        gpio_ns_init()

    def toggle(self):

        pin = self.entry_1.get()
        if pin == "":
            self.status_frame.config(text="Invalid pin!", bg=STATUS_ERROR_COLOR)
            return

        validPin = re.match('^[0-9]{1,2}$', pin)

        if not validPin or (int(pin) < 4 or int(pin) > 27):
            self.status_frame.config(text="Invalid pin!", bg=STATUS_ERROR_COLOR)
            return

        if self.isHi:
            self.status_frame.config(text='Pin is low', bg=STATUS_OK_COLOR)
            self.isHi = False
            self.toggleButton['text'] = "Set Hi"
            gpio_ns_write(int(pin), GPIO_LO)
        else:
            self.isHi = True
            self.status_frame.config(text='Pin is hi', bg=STATUS_OK_COLOR)
            self.toggleButton['text'] = "Set Low"
            gpio_ns_write(int(pin), GPIO_HI)

