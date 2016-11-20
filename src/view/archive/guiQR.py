'''
Created on 19-06-2013

@author: Trung Huynh
'''


from constants import *
from helper.log_utils import writeLog
from helper.utils import shortenPath
from model.dut_parameters import DutParameters
from Tkinter import Button, Checkbutton, Entry, Frame, Label, LabelFrame
from Tkinter import IntVar, StringVar
from Tkinter import N, S, E, W, ACTIVE, CENTER, DISABLED, RIDGE, BOTH
from controller.qrserial import *
from ttk import Frame, Style

import os
import time
import tkFileDialog
import tkMessageBox


#log_queue = SimpleQueue()


class QRMainWindow(Frame):
	def __init__(self, master):
		Frame.__init__(self, master)
		self.serial_num = StringVar()
		self.master = master
		self.__initUi()

	#===========================================================================
	# Initialize and reset GUI
	#===========================================================================
	def __initUi(self):
		self.master.title('Shine Production')
		self.pack(fill=BOTH, expand=1)

		Style().configure("TFrame", background="#333")

		#Status frame
		self.status_frame = LabelFrame(self, text='Status', relief=RIDGE, width=800, height=500)
		self.status_frame.place(x=20, y=20)
		 
		#QRFrame
		self.path_frame = LabelFrame(self, text='QR Serial Code', relief=RIDGE, height=60, width=225)
		self.path_frame.place(x=400, y=550)
		entry = Entry(self.path_frame, bd=5, textvariable=self.serial_num)
		entry.place(x=50, y=5)

		#START
		self.start_button = Button(self, text="Start", command=self.start, height=4, width=20)
		self.start_button.place(x=100, y=550)

	def start(self):
		self.start_button.config(state=DISABLED)
		self.start_button.update()
		self.__setStatusLabel(2)
		 
		success = executeQRSerialSequence(self.serial_num.get())
		self.serial_num.set("")
		self.__setStatusLabel(success)
		 
		self.start_button.config(state=ACTIVE)
		self.start_button.update()

	def __setStatusLabel(self, success):
		if success == 1:
			self.status_frame.config(text='SUCCESS', bg=STATUS_OK_COLOR)
		elif success > 1:
			self.status_frame.config(text='Status', bg='yellow')
		elif success == -1:
			self.status_frame.config(text='ERROR CONNECTING TO SOURCE METER. TRY AGAIN.', bg='blue')
		elif success == -2:
			self.status_frame.config(text='PC IS NOT CONNECTED TO INTERNET!!!!.', bg='blue')
		else:
			self.status_frame.config(text='FAIL', bg=STATUS_ERROR_COLOR)
		self.update()
