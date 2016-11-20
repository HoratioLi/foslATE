'''
Created on 19-06-2013

@author: Michael Akilian
'''


from constants import *
from controller.commands import *
from helper.utils import shortenPath
from model.dut_parameters import DutParameters
from multiprocessing import Array, Process
from multiprocessing.queues import SimpleQueue
from Tkinter import Button, Checkbutton, Entry, Frame, Label, LabelFrame
from Tkinter import IntVar, StringVar
from Tkinter import N, S, E, W, ACTIVE, CENTER, DISABLED, RIDGE
from helper import ni_usb_6800 as NI
from helper import source_meter as SM

import os
import time
import tkFileDialog
import tkMessageBox


log_queue = SimpleQueue()


class GuiMainWindow(Frame):

    def __init__(self, master, environment):

        Frame.__init__(self, master)

        self.environment = environment
        self.number_of_devices = self.environment.number_of_devices

        self.cc2541_checked = IntVar()
        self.efm32_checked = IntVar()
        self.bluetooth_checked = IntVar()
        self.ni_usb_checked = IntVar()
        self.gpib_checked = IntVar()

        self.srfpc_return_code_list = []
        self.eac_return_code_list = []

        self.eb_id_list = [StringVar() for _ in range(self.number_of_devices)]
        self.jlink_sn_list = [StringVar() for _ in range(self.number_of_devices)]
        self.__loadEbIdFromEnvironment()
        self.__loadJlinkSnFromEnvironment()

        self.master = master
        self.__initUi()

    def __notImplementedYet(self):
        tkMessageBox.showinfo('Information', 'NOT IMPLEMENTED YET!!!')

    #===========================================================================
    # Initialize and reset GUI
    #===========================================================================
    def __initUi(self):
        self.grid()
        self.master.title('Shine Production')
        for i in range(3):
            self.rowconfigure(i, pad=5)
        self.columnconfigure(0, pad=5, weight=1)
        self.columnconfigure(1, pad=5, weight=1)
        self.columnconfigure(2, pad=5, weight=2)
        self.columnconfigure(3, pad=5, weight=1)

        # Status frame
        self.status_frame = LabelFrame(self, text='Status', relief=RIDGE)
        self.status_frame.grid = self.status_frame.grid(row=0, column=0, columnspan=FRAME_COLUMN_SPAN, padx=5, pady=5)
        for i in range(8):
            self.status_frame.rowconfigure(i, pad=3)
        for i in range(self.number_of_devices + 1):
            self.status_frame.columnconfigure(i, pad=3)

        Label(self.status_frame, text='EB ID').grid(row=0, column=0, sticky=W)
        Label(self.status_frame, text='J-Link Serial Number').grid(row=1, column=0, sticky=W)
        Label(self.status_frame, text='Status').grid(row=2, column=0, sticky=W)
        Label(self.status_frame, text='DUT').grid(row=3, column=0, sticky=W)

        self.eb_id_entry = []
        self.jlink_sn_entry = []
        self.dut_status_label = []

        for i in range (self.number_of_devices):
            self.eb_id_entry.append(Entry(self.status_frame, textvariable=self.eb_id_list[i], justify=CENTER, width=10))
            self.eb_id_entry[i].grid(row=0, column=i + 1)
            self.jlink_sn_entry.append(Entry(self.status_frame, textvariable=self.jlink_sn_list[i], justify=CENTER, width=10))
            self.jlink_sn_entry[i].grid(row=1, column=i + 1)
            self.dut_status_label.append(Label(self.status_frame, text='status', bg=INITIATED_COLOR))
            self.dut_status_label[i].grid(row=2, column=i + 1)
            Label(self.status_frame, text='#{}'.format(i + 1)).grid(row=3, column=i + 1)

        # Path frame
        self.path_frame = LabelFrame(self, text='Paths')
        self.path_frame.grid = self.path_frame.grid(row=1, column=0, columnspan=FRAME_COLUMN_SPAN, padx=5, pady=5)
        for i in range(5):
            self.path_frame.rowconfigure(i, pad=3)
        for i in range(3):
            self.path_frame.columnconfigure(i, pad=3)
 
        Label(self.path_frame, text='SmartRFProgConsole Path').grid(row=0, column=0, sticky=W)
        self.srfpc_path_label = Label(self.path_frame, text=shortenPath(self.environment.srfpc_path))
        self.srfpc_path_label.grid(row=0, column=1, columnspan=FRAME_COLUMN_SPAN - 2, sticky=W)
        Button(self.path_frame, text='  ...  ', command=self.setSrfpcPath).grid(row=0, column=FRAME_COLUMN_SPAN - 1, sticky=N + S + E + W)
 
        Label(self.path_frame, text='EACommander Path').grid(row=1, column=0, sticky=W)
        self.eac_path_label = Label(self.path_frame, text=shortenPath(self.environment.eac_path))
        self.eac_path_label.grid(row=1, column=1, columnspan=FRAME_COLUMN_SPAN - 2, sticky=W)
        Button(self.path_frame, text='  ...  ', command=self.setEacPath).grid(row=1, column=FRAME_COLUMN_SPAN - 1, sticky=N + S + E + W)
 
        Label(self.path_frame, text='CC2541 Firmware Path').grid(row=2, column=0, sticky=W)
        self.cc2541_firmware_path_label = Label(self.path_frame, text=shortenPath(self.environment.cc2541_firmware_path))
        self.cc2541_firmware_path_label.grid(row=2, column=1, columnspan=FRAME_COLUMN_SPAN - 2, sticky=W)
        Button(self.path_frame, text='  ...  ', command=self.setCc2541FirmwarePath).grid(row=2, column=FRAME_COLUMN_SPAN - 1, sticky=N + S + E + W)
 
        Label(self.path_frame, text='EFM32 Firmware Path').grid(row=3, column=0, sticky=W)
        self.efm32_firmware_path_label = Label(self.path_frame, text=shortenPath(self.environment.efm32_firmware_path))
        self.efm32_firmware_path_label.grid(row=3, column=1, columnspan=FRAME_COLUMN_SPAN - 2, sticky=W)
        Button(self.path_frame, text='  ...  ', command=self.setEfm32FirmwarePath).grid(row=3, column=FRAME_COLUMN_SPAN - 1, sticky=N + S + E + W)

        Label(self.path_frame, text='EFM32 Final Firmware Path').grid(row=4, column=0, sticky=W)
        self.efm32_final_firmware_path_label = Label(self.path_frame, text=shortenPath(self.environment.efm32_firmware_path_final))
        self.efm32_final_firmware_path_label.grid(row=4, column=1, columnspan=FRAME_COLUMN_SPAN - 2, sticky=W)
        Button(self.path_frame, text='  ...  ', command=self.setEfm32FinalFirmwarePath).grid(row=4, column=FRAME_COLUMN_SPAN - 1, sticky=N + S + E + W)
        
        # Initiate Verify, Start and Close buttons
        self.save_environment_button = Button(self, text='Save Environment', command=self.saveEnvironment)
        self.save_environment_button.grid(row=2, column=0, sticky=N+S+E+W)
        
        self.start_button = Button(self, text="Start", command=self.start2)
        self.start_button.grid(row=2, column=2, sticky=N+S+E+W)
 
        self.close_button = Button(self, text="Close", command=self.close)
        self.close_button.grid(row=2, column=3, sticky=N+S+E+W)

    def __resetStatusLabels(self):
        for i in range (self.number_of_devices):
            self.dut_status_label[i].config(text='status', bg=INITIATED_COLOR)

    #===========================================================================
    # Load, save EB and J-Link devices IDs from to environment to display them
    # on the GUI 
    #===========================================================================
    def __loadEbIdFromEnvironment(self):
        for i in range(self.number_of_devices):
            self.eb_id_list[i].set(self.environment.eb_id_list[i])

    def __loadJlinkSnFromEnvironment(self):
        for i in range(self.number_of_devices):
            self.jlink_sn_list[i].set(self.environment.jlink_sn_list[i])

    def __saveEbIdToEnvironment(self):
        for i in range(self.number_of_devices):
            self.environment.eb_id_list[i] = self.eb_id_list[i].get()

    def __saveJlinkSnToEnvironment(self):
        for i in range(self.number_of_devices):
            self.environment.jlink_sn_list[i] = self.jlink_sn_list[i].get()

    #===========================================================================
    # Update status labels on the GUI
    #===========================================================================
    def __setStatusLabel(self, index, status):
#        self.srfpc_return_code_list[index] = status
        if status == SUCCESS_CODE:
            self.dut_status_label[index].config(text='Pass [{}]'.format(str(status)), bg=STATUS_OK_COLOR)
        elif status == IN_PROGRESS_CODE:
            self.dut_status_label[index].config(text='In Progress... [{}]'.format(str(status)), bg=STATUS_IN_PROGRESS_COLOR)
        elif status == -2:
            self.dut_status_label[index].config(text='FIX INTERNET', bg='blue')
        elif status == -3:
            self.dut_status_label[index].config(text='CANT CONNECT TO KEITHLEY', bg='blue')
        else:
            self.dut_status_label[index].config(text='Fail [{}]'.format(str(status)), bg=STATUS_ERROR_COLOR)
        self.update()

    def __drawStatusLabel(self, status_list):
        if type(status_list) != list or len(status_list) != self.number_of_devices:
            return
        for i in range(self.number_of_devices):
            self.__setStatusLabel(i, status_list[i])

    #===========================================================================
    # Update executable paths
    #===========================================================================
    def setSrfpcPath(self):
        f = tkFileDialog.askopenfile(parent=self.master,
                                     mode='rb',
                                     title='Pick SmartRFProgConsole.exe file',
                                     filetype=(('EXE file', '*.exe'),))
        if f:
            self.environment.srfpc_path = os.path.abspath(f.name)
            f.close()
            self.environment.save()
            self.srfpc_path_label.config(text=shortenPath(self.environment.srfpc_path))
            self.srfpc_path_label.update()

    def setEacPath(self):
        f = tkFileDialog.askopenfile(parent=self.master,
                                     mode='rb',
                                     title='Pick eACommander.exe file',
                                     filetype=(('EXE file', '*.exe'),))
        if f != None:
            self.environment.eac_path = os.path.abspath(f.name)
            f.close()
            self.environment.save()
            self.eac_path_label.config(text=shortenPath(self.environment.eac_path))
            self.eac_path_label.update()

    def setCc2541FirmwarePath(self):
        f = tkFileDialog.askopenfile(parent=self.master,
                                     mode='rb',
                                     title='Pick CC2541 Firmware HEX file',
                                     filetype=(('HEX file', '*.hex'),))
        if f != None:
            self.environment.cc2541_firmware_path = os.path.abspath(f.name)
            f.close()
            self.environment.save()
            self.cc2541_firmware_path_label.config(text=shortenPath(self.environment.cc2541_firmware_path))
            self.cc2541_firmware_path_label.update()

    def setEfm32FirmwarePath(self):
        f = tkFileDialog.askopenfile(parent=self.master,
                                     mode='rb',
                                     title='Pick EFM32 Firmware BIN file',
                                     filetype=(('BIN file', '*.bin'),))
        if f != None:
            self.environment.efm32_firmware_path = os.path.abspath(f.name)
            f.close()
            self.environment.save()
            self.efm32_firmware_path_label.config(text=shortenPath(self.environment.efm32_firmware_path))
            self.efm32_firmware_path_label.update()
    
    def setEfm32FinalFirmwarePath(self):
        f = tkFileDialog.askopenfile(parent=self.master,
                                     mode='rb',
                                     title='Pick EFM32 Final Firmware BIN file',
                                     filetype=(('BIN file', '*.bin'),))
        if f != None:
            self.environment.efm32_firmware_path_final = os.path.abspath(f.name)
            f.close()
            self.environment.save()
            self.efm32_final_firmware_path_label.config(text=shortenPath(self.environment.efm32_firmware_path_final))
            self.efm32_final_firmware_path_label.update()

    def saveEnvironment(self):
        self.__saveEbIdToEnvironment()
        self.__saveJlinkSnToEnvironment()
        self.environment.save()
        tkMessageBox.showinfo('Information', 'Environment has been saved successfully!')

    def close(self):
        """
        TODO: Save current parameters, state.
        """
        if tkMessageBox.askokcancel('Confirmation', 'Are you sure you want to quit?'):
            self.quit()

    def __waitForContinueMessage(self):
        #P0.6 = ETM_TD0
        test = -1
        while test != 0:  # THIS VALUE IS ALWAYS  SOMETHING IS WRONG
            test = NI.captureDigitalInput('Dev1/port0/line6', 1)[0]

    def __sendContinueMessage(self):
        #P0.7 = ETM_TD1
        NI.setDigitalOutput('Dev1/port0/line7', 128)
        NI.setDigitalOutput('Dev1/port0/line7', 0)

    def start2(self):
        self.__resetStatusLabels()
        self.start_button.config(state=DISABLED)
        self.start_button.update()
        self.__setStatusLabel(0, IN_PROGRESS_CODE)

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #~~~CC2541 and EFM32 FIRMWARE FLASH (PRODUCTION TEST FIRMWARE)~~~
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        dut_parameters = DutParameters(ATE_ID,
                self.environment.device_code_name,
                self.environment.device_type,
                self.environment.eb_id_list[0],
                self.environment.jlink_sn_list[0],
                self.environment)

        status = executeTestSequence(dut_parameters, log_queue)
        print 'Status: {}'.format(status)
        dut_parameters.logStatus(status)
        self.__setStatusLabel(0, status)

        self.start_button.config(state=ACTIVE)
        self.start_button.update()
