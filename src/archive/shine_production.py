'''
Created on 20-05-2013

@author: Trung Huynh
'''


from constants import *
from model.environment import Environment
from Tkinter import Tk
from view.gui import GuiMainWindow

import sys
import tkMessageBox


def startGui(environment):
    def callback():
        if tkMessageBox.askokcancel('Confirmation', 'Are you sure you want to quit?'):
            master.destroy()
    master = Tk()
    master.protocol('WM_DELETE_WINDOW', callback)
    app = GuiMainWindow(master, environment)
    app.master.title("Shine Firmware Updater")
    app.mainloop()

def usage():
    '''
    TODO
    '''
    pass

def main(options):
    if len(options) == 0:
        usage()

    # Setup environment
    environment = Environment()
    environment.load()

    # Start GUI
    startGui(environment)

if __name__ == "__main__":
    main(sys.argv[1:])
