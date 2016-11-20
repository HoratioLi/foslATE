'''
Created on 22-06-2013

@author: Michael AKilian
'''


from constants import *

import os.path
import sys
import array
import time
import socket


# Special characters to be escaped
LF   = 0x0A
CR   = 0x0D
ESC  = 0x1B
PLUS = 0x2B


def initialize():
    # Open TCP connect to port 1234 of GPIB-ETHERNET
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    sock.settimeout(3)
    print IP

    try:
        sock.connect((IP, PORT))
    except socket.timeout, e:
        print 'socket connection timed out'
        return False
    except Exception, e:
        print 'something\'s wrong with %s:%d. Exception type is %s' % (IP, PORT, `e`)
        return False

    try:
        # Turn on read-after-write
        sock.send('++auto 0\n')

        # Set mode as CONTROLLER
        sock.send('++mode 1\n')

        # Set address
        sock.send("++addr 24\n")

        # Do not append carriage return (CR) of line feed (LF) to GPIB data
        sock.send('++eos 3\n') 

        # Assert eoi to indicate last byte of data
        sock.send('++eoi 1\n')

        #reset
        sock.send('*RST\n')

        #only measure references on initialization
        sock.send(':syst:azer:stat once\n')
        sock.send(':syst:azer:stat off\n')

        sock.close()
        return True
    except socket.error, e:
        print e
        return False

def armSystem():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    sock.settimeout(3)
    sock.connect((IP, PORT))

    try:
        # Turn output on
        sock.send('OUTP 1\n')
        sock.close()

    except socket.error, e:
        print e

def outputOff():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    sock.settimeout(3)
    sock.connect((IP, PORT))

    try:
        # Power cycle
        sock.send(':sour:volt:lev 0\n')
        sock.send(':outp off\n')
        sock.close()

    except socket.error, e:
        print e

def setComplianceCurrent(amps):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    sock.settimeout(3)
    sock.connect((IP, PORT))

    try:
        sock.send(':sens:func "curr"\n')
        sock.send(':sens:curr:prot %s\n' % amps)
        sock.send(':sens:curr:rang %s\n' % amps)
        sock.send(':outp on\n') # Turn on power

        sock.close()
    except socket.error, e:
        print e

def setupVoltageAndBatchCurrent1():
    # Open TCP connect to port 1234 of GPIB-ETHERNET
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    sock.settimeout(3)
    sock.connect((IP, PORT))

    try:
        sock.send(':sour:volt 3\n')  # Set output voltage to 3.00V
        sock.send(':sens:func "curr"\n') # Sense current draw
        sock.send(':sens:curr:prot 100e-3\n') # Set compliance to 100 mA
        sock.send(':sens:curr:rang 100e-3\n') # Set range to 100 mA
        sock.send(':sens:curr:nplc .6\n') # set measurement speed to 100ms
        sock.send(':sens:aver:tcon rep\n')
        sock.send(':sens:aver:coun 10\n') #average every 10 measurements
        sock.send(':sens:aver on\n')
        sock.send(':trac:feed sens\n')
        sock.send(':trac:poin 10\n') #10 100 ms measuremetnes = 1 second
        sock.send(':trig:coun 10\n')
        sock.send(':trac:feed:cont nev\n')
        sock.send(':outp on\n') # Turn on power
        sock.close()
    except socket.error, e:
        print e

def setupVoltageAndBatchCurrent2():
    # Open TCP connect to port 1234 of GPIB-ETHERNET
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    sock.settimeout(3)
    sock.connect((IP, PORT))

    try:
        sock.send(':sens:curr:nplc 4\n') # set measurement speed to 66.6ms
        sock.send(':sens:aver:tcon rep\n')
        sock.send(':sens:aver:coun 59\n') #average every 59 measurements (~ 4 seconds per average)
        sock.send(':sens:aver on\n')
        sock.send(':trac:feed sens\n')
        sock.send(':trac:poin 5\n') #5 4 seconds averages = 20 seconds
        sock.send(':trig:coun 5\n')
        sock.send(':trac:feed:cont nev\n')
        sock.close()
    except socket.error, e:
        print e

def measureBatchCurrent2():
    # Open TCP connect to port 1234 of GPIB-ETHERNET
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    sock.settimeout(1)
    sock.connect((IP, PORT))

    current = ''
    try:
        # clear buffer
        sock.send('trac:cle\n')

        # enable buffer
        sock.send(':trac:feed:cont next\n')

        # start measurement
        sock.send(':init\n')
        time.sleep(22) #take 1000 measurements quickly

        #c ollect readings
        sock.send(':trac:data?\n')
        sock.send('++auto 1\n')
        while True:
                current += sock.recv(4096)
        print "done"
        
        #clean up
        sock.send('++auto 0\n')
        sock.send(':trac:feed:cont nev\n')
        sock.send(':trac:cle\n')
        sock.close()
    except socket.error, e:
        print "done"
        #clean up
        sock.send('++auto 0\n')
        sock.send(':trac:feed:cont nev\n')
        sock.send(':trac:cle\n')
        sock.close()

    return current

def measureBatchCurrent1():
    # Open TCP connect to port 1234 of GPIB-ETHERNET
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    sock.settimeout(1)
    sock.connect((IP, PORT))

    current = ''
    try:
        # clear buffer
        sock.send('trac:cle\n')

        # enable buffer
        sock.send(':trac:feed:cont next\n')

        # start measurement
        sock.send(':init\n')
        time.sleep(1.3) #take 1000 measurements quickly

        #c ollect readings
        sock.send(':trac:data?\n')
        sock.send('++auto 1\n')
        while True:
                current += sock.recv(4096)
        print "done"
        
        #clean up
        sock.send('++auto 0\n')
        sock.send(':trac:feed:cont nev\n')
        sock.send(':trac:cle\n')
        sock.close()
    except socket.error, e:
        print "done"
        #clean up
        sock.send('++auto 0\n')
        sock.send(':trac:feed:cont nev\n')
        sock.send(':trac:cle\n')
        sock.close()

    return current

def setOutputVoltageTo3v():
    # Open TCP connect to port 1234 of GPIB-ETHERNET
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    sock.settimeout(3)
    sock.connect((IP, PORT))

    try:
        #reset
        sock.send('*RST\n')

        #only measure references on initialization
        sock.send(':syst:azer:stat once\n')
        sock.send(':syst:azer:stat off\n')
        
        sock.send(':sour:func volt\n') # Set output to source voltage
        sock.send(':sour:volt:mode fix\n') # Fixed voltage
        sock.send(':sour:volt:rang 20\n') # Set voltage range to 20V
        sock.send(':sour:volt:lev 3\n')  # Set output voltage to 3.00V
        sock.send(':sens:func "curr"\n') # Sense current draw
        sock.send(':sens:curr:prot 100e-3\n') # Set compliance to 100 mA
        sock.send(':sens:curr:rang 100e-3\n') # Set range to 100 mA
        sock.send(':outp on\n') # Turn on power
        sock.close()
    except socket.error, e:
        print e

def senseAdvertCurrent():
    # Open TCP connect to port 1234 of GPIB-ETHERNET
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    sock.settimeout(3)
    sock.connect((IP, PORT))
    current = -1
    try:
        # Measure current above threshold (expected advertising current) timeout
        # after 4 seconds since we advertise every second.
        sock.send('\n')
        current = sock.recv(100)
        sock.close()
    except socket.error, e:
        print e

    return current

def senseCurrent():
    # Open TCP connect to port 1234 of GPIB-ETHERNET
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    sock.settimeout(3)
    sock.connect((IP, PORT))

    current = -1

    try:
        # Measure current 
        sock.send(':read?\n')
        sock.send('++auto 1\n')
        current = sock.recv(100)
        sock.send('++auto 0\n')
        sock.close()
    except socket.error, e:
        print e

    return current
