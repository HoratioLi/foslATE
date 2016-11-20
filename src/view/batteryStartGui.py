

import os, sys
import matplotlib.pylab as plt
import matplotlib.legend
from matplotlib.widgets import Button
from view.guiBattery import GuiBatteryWindow
from Tkinter import Tk, Toplevel
import tkMessageBox
from constants import *

from PIL import Image, ImageTk
from helper.posgresDB_extractor import *

# IMAGE_FILE_PATH = '/home/pi/misfit/ShineProduction/src/view/images/batteryPlot.png'
DELAY_BEFORE_WINDOW_CLOSE = 1 # Number of seconds before GUI window closes after selecting choice
# isRunningOnPi = os.path.isdir("/home/pi")

params = {}
params['img_file_path'] = IMAGE_FILE_PATH
params['isRunningOnPi'] = IS_RUNNING_ON_PI
print "isRunningOnPi: %s" % IS_RUNNING_ON_PI

def startGui():

    def callback():
        if tkMessageBox.askokcancel('Confirmation', 'Are you sure you want to quit?'):
            master_batt.destroy()
            return master_batt.plot_passed
    if CLI_MODE:
        master_batt = Tk()
    else:
        master_batt = Toplevel()   
    master_batt.geometry=("1500x900")
    master_batt.minsize(1500,900)
    master_batt.protocol('WM_DELETE_WINDOW', callback)
    master_batt.plot_passed = None
    app = GuiBatteryWindow(master_batt)
    app.master_batt.title("Battery Plot")
    app.mainloop()
    master_batt.destroy()

    print "PLOT PASSED: %s" % master_batt.plot_passed
    return master_batt.plot_passed
