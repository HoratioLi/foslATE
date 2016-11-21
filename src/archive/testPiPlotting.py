

import os, sys
# import helper.posgresDB_extractor as pgdb
import matplotlib.pylab as plt
import matplotlib.legend
from matplotlib.widgets import Button
from view.guiBattery import GuiMainWindow
from Tkinter import Tk
import tkMessageBox

from PIL import Image, ImageTk
from helper.posgresDB_extractor import *
from view.batteryStartGui import startGui

IMAGE_FILE_PATH = '/home/pi/misfit/Production/src/view/images/batteryPlot.png'
DELAY_BEFORE_WINDOW_CLOSE = 1 # Number of seconds before GUI window closes after selecting choice
isRunningOnPi = os.path.isdir("/home/pi")

params = {}
params['img_file_path'] = IMAGE_FILE_PATH
# params['delayBeforeWindowClose'] = DELAY_BEFORE_WINDOW_CLOSE
params['isRunningOnPi'] = True
# params['isRunningOnPi'] = isRunningOnPi
print "isRunningOnPi: %s" % isRunningOnPi

def BatteryPlotCheck():

    #BATTERY PLOT CHECK
    #pull up plot and pass/fail button.
    print "Battery Plot Test Running" 
    BATTERY_PLOT_FAIL = 0
    startDateStr = '2013-09-01'
    endDateStr = '2013-09-17'
    serialFromShine = 'sf00000026'
    # endDate = datetime.date.today() - datetime.timedelta(days=30)
    # endDateStr = endDate.strftime('%Y-%m-%d')
    print "Getting battery data..."
    (bat, reset) = getBatteryWithResetData('shine_prod','serial_number', str(serialFromShine), startDateStr, endDateStr)    
    print "Plotting battery data..."
    passed = plotActivityBatterryReset(bat, reset, input, startDateStr, endDateStr, params)
    print "Returned passed = %s, from battery GUI" % passed
    if not passed:
        BATTERY_PLOT_FAIL = 1
    return

# def startGui():

#     def callback():
#         if tkMessageBox.askokcancel('Confirmation', 'Are you sure you want to quit?'):
#             master.destroy()
#             return master.plot_passed
#     master = Tk()
#     master.geometry=("1500x900")
#     master.minsize(1500,900)
#     master.protocol('WM_DELETE_WINDOW', callback)
#     master.plot_passed = None
#     app = GuiMainWindow(master)
#     app.master.title("Battery Plot")
#     app.mainloop()

#     print "PLOT PASSED: %s" % master.plot_passed
#     return master.plot_passed

def main():

    BatteryPlotCheck()

    # plot_passed = startGui()

    # print "PLOT PASSED (main): %s" % plot_passed

    return plot_passed

if __name__ == "__main__":
    main()
