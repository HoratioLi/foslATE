

from model.device import *
from helper.gpio_no_sudo import *
from constants import *

import numpy

def readCurrent(instr, num_readings, params):
    readings = instr.getMultipleReadings(num_readings)
    meanReading = numpy.mean(readings)
    if INVERT_AGILENT_READINGS:
        for reading in readings:
            reading = reading * -1
        meanReading = meanReading * -1
    if params['debug_mode']:
        print "\n%d readings: %s" % (num_readings, readings)    
        print "Mean of %d readings: %s" % (num_readings, meanReading)
    testResult = MultipleCurrentTest(currents=readings, 
                                 average=meanReading)
    return testResult

def readSingleCurrent(instr, params):
    reading = instr.getReading()
    if INVERT_AGILENT_READINGS:
        reading = reading * -1    
    if params['debug_mode']:
        print "\nReading: %s" % reading
    testResult = SingleCurrentTest(current=reading)
    return testResult    

def readSingleVoltage(instr, params):
    pinState = gpio_ns_write(VOLTAGE_TEST_PIN, GPIO_LO) 
    read_pin_state = gpio_ns_read(VOLTAGE_TEST_PIN)  
    print "read_pin_state: %s, intended pin_state: %s" % (read_pin_state, GPIO_LO)               
    reading = instr.getReading()
    if INVERT_AGILENT_READINGS:
        reading = reading * -1        
    #choice = raw_input("Hit 'Enter' to continue: ")        
    pinState = gpio_ns_write(VOLTAGE_TEST_PIN, GPIO_HI) 
    read_pin_state = gpio_ns_read(VOLTAGE_TEST_PIN)  
    print "read_pin_state: %s, intended pin_state: %s" % (read_pin_state, GPIO_HI)      
    if params['debug_mode']:
        print "\nReading: %s" % reading
    testResult = SingleVoltageTest(voltage=reading)
    return testResult   

def setResults(testResult, name, isPassed, params):
    testResult.name = name
    testResult.is_passed = isPassed
    if params['verbose_mode']:
        pprint (vars(testResult))
        print ""
    return testResult    

def setTimeoutResults(name, timeout, params):
    print "Warning: timeout in %s. Exiting." % name
    testResult = TimeoutTest()
    testResult.timeout = timeout
    testResult.is_passed = False
    testResult.name = name
    if params['verbose_mode']:
        pprint (vars(testResult))
        print ""
    return testResult  