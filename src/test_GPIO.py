#!/usr/bin/env python
'''
Created on 2015-04-21

@author: James Quen
'''


from constants import *
from Tkinter import Tk
from view.testGPIO import GuiMainWindow

import sys
import tkMessageBox


def startGui():
    def callback():
        if tkMessageBox.askokcancel('Confirmation', 'Are you sure you want to quit?'):
            master.destroy()
    master = Tk()
    master.geometry=("800x800")
    master.minsize(300, 350)
    master.protocol('WM_DELETE_WINDOW', callback)
    app = GuiMainWindow(master)
    app.master.title("GPIO Tester")
    app.mainloop()

def usage():
    '''
    TODO
    '''
    pass

def main(options):
    if len(options) == 0:
        usage()

    # Start GUI
    startGui()

if __name__ == "__main__":
    main(sys.argv[1:])
