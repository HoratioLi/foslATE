'''
Created on 3-07-2013

@author: Michael Akilian
'''


from constants import *
from Tkinter import Tk
from view.guiQR import QRMainWindow

import sys
import tkMessageBox


def startGui():
    def callback():
        if tkMessageBox.askokcancel('Confirmation', 'Are you sure you want to quit?'):
            master.destroy()
    master = Tk()
    master.geometry=("800x800")
    master.minsize(850, 750)
    master.protocol('WM_DELETE_WINDOW', callback)
    app = QRMainWindow(master)
    app.master.title("Shine Production Serial")
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
