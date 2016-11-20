#!/usr/bin/env python
'''
Created on 2014-07-17

@author: Rachel Kalmar
'''

from helper.gpio_no_sudo import *
from constants import *

# Initialize the Device Under Test
def initDUT():
    # Initialize GPIO
    gpio_ns_init()

    resetDUT()
    return True

# Reset the Device Under Test
def resetDUT():

    configureSuccess = configureGPIOs("reset")

    # turn off UART RX PIN
    if DEVICE_TYPE == 'Aquila' or DEVICE_TYPE == 'SaturnMKII' or DEVICE_TYPE == 'Pluto' or DEVICE_TYPE == 'BMW' or DEVICE_TYPE == 'Silvretta' or DEVICE_TYPE == 'SAM':
        if DEBUG_MODE:
            print "\nTurning off UART relay...\n"

        if LUNCHBOX:
            gpio_ns_write(IN_MFG_INFO_CTL, GPIO_LO)
        else:
            gpio_ns_write(IN_MFG_INFO_CTL, GPIO_HI)

    # Turn off power to DUT
    print "\n...\nPowering off DUT\n...\n"
    gpio_ns_write(POWER_PIN, GPIO_HI)

    return configureSuccess

# Reset the Device Under Test
def turnOnDUT():

    # Turn on power to DUT
    print "\n...\nPowering on DUT\n...\n"
    gpio_ns_write(POWER_PIN, GPIO_LO)

    # turn off UART RX PIN
    if DEVICE_TYPE == 'Aquila' or DEVICE_TYPE == 'SaturnMKII' or DEVICE_TYPE == 'Pluto' or DEVICE_TYPE == 'BMW' or DEVICE_TYPE == 'Silvretta' or DEVICE_TYPE == 'SAM':
        if DEBUG_MODE:
            print "\nTurning on UART relay...\n"
        if LUNCHBOX:
            gpio_ns_write(IN_MFG_INFO_CTL, GPIO_HI)
        else:
            gpio_ns_write(IN_MFG_INFO_CTL, GPIO_LO)

    return True

def connectUART():
    gpio_ns_write(IN_MFG_INFO_CTL, GPIO_HI)

def disconnectUART():
    gpio_ns_write(IN_MFG_INFO_CTL, GPIO_LO)

# Power cycle the Device Under Test
def powerCycleDUT(state):

    configureSuccessReset = resetDUT()

    # Pause between tests in debug mode
    if DEBUG_MODE:
        choice = raw_input("Hit 'Enter' to continue: ")
        print ""

    # Sleep for one second
    time.sleep(0.25)

    # Turn on power to DUT
    turnOnDUT()

    configureSuccessStart = configureGPIOs(state)

    # Return False if can't power on Pi or configure GPIOs
    return (configureSuccessStart and configureSuccessReset)
    # return (configureSuccessStart or configureSuccessReset)    

# Configure the GPIO pins based on whether resetting or configuring DUT
def configureGPIOs(state):

    configureSuccess = True

    if state == "reset":
        pin_state = GPIO_LO
        voltage_pin_state = GPIO_HI
        mfg_pin_state = GPIO_LO  
        #pull_state = "tri"
        pull_state = "down"     
    elif state == "configure":
        pin_state = GPIO_HI
        voltage_pin_state = GPIO_HI
        mfg_pin_state = GPIO_HI     
        pull_state = "up"  
    elif state == "customer":
        pin_state = GPIO_LO
        voltage_pin_state = GPIO_HI
        mfg_pin_state = GPIO_LO
        pull_state = "down"
    else:
        print "Configure state %s unknown. Aborting..." % state
        configureSuccess = False
        return configureSuccess

    # Set GPIOs to appropriate state
    if DEBUG_MODE:
        print "\nConfiguring GPIOs into %s mode" % state

    # Set VOLTAGE_TEST_PIN to output logic level pin_state    
    gpio_ns_write(VOLTAGE_TEST_PIN, voltage_pin_state) 
    read_pin_state = gpio_ns_read(VOLTAGE_TEST_PIN)  
    if voltage_pin_state != str(read_pin_state):
        print "Error: VOLTAGE_TEST_PIN state not successfully set"
        print "read_pin_state: %s, intended pin_state: %s" % (read_pin_state, voltage_pin_state)        
        configureSuccess = False
    if DEBUG_MODE:
        print "VOLTAGE_TEST_PIN start state: %s" % read_pin_state   

    """
    #leave this block in for now, could be removed later.  Just used for debugging
    gpio_ns_config(MFG_TRIG_PIN, "out")
    gpio_ns_config(MFG_TOGGLE_PIN, "out")
    gpio_ns_config(MFG_INFO_PIN, "out")
    """

    # Drive the MFG_INFO_PIN low to enter Hardware test mode.
    # Firmware has another level of checking that requires ATE to drive this pin low
    # in order to prevent users from entering hardware test mode.
    if state == "configure":
        gpio_ns_config(MFG_INFO_PIN, "out")
        gpio_ns_write(MFG_INFO_PIN, GPIO_LO)
  
    gpio_ns_write(MFG_TRIG_PIN, mfg_pin_state) 
    read_pin_state = gpio_ns_read(MFG_TRIG_PIN)  
    if mfg_pin_state != str(read_pin_state):
        print "Error: MFG_TRIG_PIN state not successfully set"
        print "read_pin_state: %s, intended pin_state: %s" % (read_pin_state, mfg_pin_state)        
        configureSuccess = False
    if DEBUG_MODE:
        print "MFG_TRIG_PIN start state: %s" % read_pin_state   
    
    # Set button to output logic level pin_state
    gpio_ns_write(MFG_TRIG_PIN, pin_state)  
    read_pin_state = gpio_ns_read(MFG_TRIG_PIN)
    if pin_state != str(read_pin_state):
        print "Error: MFG_TRIG_PIN state not successfully set"
        print "read_pin_state: %s, intended pin_state: %s" % (read_pin_state, pin_state)            
        configureSuccess = False
    if DEBUG_MODE:        
        print "Button start state: %s" % read_pin_state       

    if STATION_ID == 1:
        if not LIMITED_PIN_SET:
            # Set MFG_INFO_PIN to input with pull_state
            gpio_ns_pull(MFG_INFO_PIN, pull_state)  
            # Wait for 300ms, then read pull_state to make sure it's down
            # time.sleep(0.3)
            time.sleep(1) 
            read_pin_state = gpio_ns_read(MFG_INFO_PIN)
            if str(read_pin_state) == '0':
                read_pin_str = 'low'
            elif str(read_pin_state) == '1':
                read_pin_str = 'high'    
            if DEBUG_MODE:
                print "read_pin_str: %s" % read_pin_str
            if read_pin_str != 'low':
                print "Error: MFG_INFO_PIN state should be logic low"
                configureSuccess = False
            if DEBUG_MODE:
                print "MFG_INFO_PIN start state: %s" % read_pin_str  

        # Set MFG_TOGGLE_PIN to input with pull_state
        gpio_ns_pull(MFG_TOGGLE_PIN, pull_state) 
        """
        if state == "configure":
            gpio_ns_write(MFG_INFO_PIN, GPIO_HI)
            gpio_ns_write(MFG_TOGGLE_PIN, GPIO_HI)
            time.sleep(2.5)  
            # for ate_sync on MCU.  MCU is waiting for rising edge of MFG_TRIG_PIN
            # when in hardware test mode.
            gpio_ns_write(MFG_TRIG_PIN,GPIO_LO)
            gpio_ns_write(MFG_TRIG_PIN,GPIO_HI)
        """


        # Wait for 300ms, then read pull_state to make sure it's down
        time.sleep(0.5)
        """
        if state == "configure":
            time.sleep(1)    
            read_pin_state = gpio_ns_read(MFG_TOGGLE_PIN)
            if str(read_pin_state) == '0':
                read_pin_str = 'low'
            elif str(read_pin_state) == '1':
                read_pin_str = 'high'
            if DEBUG_MODE:
                print "read_pin_str: %s" % read_pin_str
            if read_pin_str != 'low':
                print "Error: MFG_TOGGLE_PIN state should be logic low"
                if PROGRAM_DEVICE:
                    print "(Board may not be programmed!)"
                configureSuccess = False
            if DEBUG_MODE:
                print "MFG_TOGGLE_PIN start state: %s" % read_pin_str
        """
    # Return False if any of these things didn't work. 
    return configureSuccess

# Toggle the MFG_TRIG_PIN on the Raspberry Pi
def toggleButton(current_state, new_state):
    # Toggle button pin
    if DEBUG_MODE:
        print "Toggling MFG_TRIG_PIN"
    gpio_ns_pull(MFG_TRIG_PIN, "out")    
    gpio_ns_write(MFG_TRIG_PIN,GPIO_LO)
    if DEBUG_MODE:
        read_pin_state = gpio_ns_read(MFG_TRIG_PIN)
        print "read_pin_state: %s, intended pin_state: %s" % (read_pin_state, GPIO_LO) 
    time.sleep(BUTTON_TOGGLE_TIME)
    gpio_ns_write(MFG_TRIG_PIN,GPIO_HI)
    if DEBUG_MODE:
        read_pin_state = gpio_ns_read(MFG_TRIG_PIN)
        print "read_pin_state: %s, intended pin_state: %s" % (read_pin_state, GPIO_HI)         
    if DEBUG_MODE:
        print "Current state: %s" % current_state
        print "New state: %s" % new_state

    if DEBUG_MODE:
        print "Set MFG_TRIG_PIN low."
    gpio_ns_write(MFG_TRIG_PIN,GPIO_LO)
    if DEBUG_MODE:
        print "Setting MFG_TRIG_PIN as an input."
    gpio_ns_pull(MFG_TRIG_PIN, "in")


# Set the pins to test mode
def setPinsToTestMode():
    time.sleep(0.001) 
    if DEBUG_MODE:
        print "Turning off weak pullup on MFG_TOGGLE_PIN\n\n"
    if MCU == "Ambiq":
        #gpio_ns_write(MFG_TRIG_PIN, GPIO_LO)
        gpio_ns_pull(MFG_TRIG_PIN, "in")
    #gpio_ns_pull(MFG_TOGGLE_PIN, "tri")
    if not LIMITED_PIN_SET:
        gpio_ns_write(MFG_TRIG_PIN, GPIO_LO) # Set MFG_TRIG_PIN to output logic level low
    

def unlockToProgram():
    print "Unlocking device to program..."
    #open UART comms
    gpio_ns_write(IN_MFG_INFO_CTL, GPIO_HI)

    resetDUT()

    print "Setting pins to unlock"
    #configure pins as outputs
    gpio_ns_config(MFG_TRIG_PIN, "out")
    print "MFG_TRIG_PIN: %d" % gpio_ns_read(MFG_TRIG_PIN)
    gpio_ns_config(MFG_TOGGLE_PIN, "out")
    print "MFG_TOGGLE_PIN: %d" % gpio_ns_read(MFG_TOGGLE_PIN)
    gpio_ns_config(MFG_INFO_PIN, "out")
    print "MFG_INFO_PIN: %d" % gpio_ns_read(MFG_INFO_PIN)


    #assert info and toggle pins low
    gpio_ns_write(MFG_INFO_PIN, GPIO_LO)
    print "MFG_INFO_PIN: %d" % gpio_ns_read(MFG_INFO_PIN)
    gpio_ns_write(MFG_TOGGLE_PIN, GPIO_LO)
    print "MFG_TOGGLE_PIN: %d" % gpio_ns_read(MFG_TOGGLE_PIN)

    print "Powering on device"
    #power on device
    powerCycleDUT("configure")
    #assert trigger pin high
    gpio_ns_write(MFG_TRIG_PIN, GPIO_HI)
    print "MFG_TRIG_PIN: %d" % gpio_ns_read(MFG_TRIG_PIN)
    print "MFG_INFO_PIN: %d" % gpio_ns_read(MFG_INFO_PIN)
    print "MFG_TOGGLE_PIN: %d" % gpio_ns_read(MFG_TOGGLE_PIN)

    time.sleep(3)
    
    gpio_ns_pull(MFG_INFO_PIN, "alt0")
    gpio_ns_pull(MFG_TOGGLE_PIN, "in")

    print "Powering off device"
    gpio_ns_write(MFG_TRIG_PIN, GPIO_LO) # Set MFG_TRIP_PIN low to not back power device.
    gpio_ns_write(POWER_PIN, GPIO_HI)
    time.sleep(0.25)
    print "Powering on device"
    gpio_ns_write(POWER_PIN, GPIO_LO)


# Run the programming sequence via the flasher pins
def runProgrammingSequence():
    programming_success = False

    print "\nRunning programming sequence...\n"

    if DEBUG_MODE:
        print "Starting Programming Test"
        print "Start state of pins:"
        print "OK_PIN: %d" % gpio_ns_read(FLASHER_OK_PIN)
        print "BUSY_PIN: %d" % gpio_ns_read(FLASHER_BUSY_PIN)

    # Assert Start pin
    gpio_ns_write(FLASHER_START_PIN, "1")
    time.sleep(0.25)

    if DEBUG_MODE:
        print "Assert state of pins:"
        print "OK_PIN: %d" % gpio_ns_read(FLASHER_OK_PIN)
        print "BUSY_PIN: %d" % gpio_ns_read(FLASHER_BUSY_PIN)

    # Lower the Start 
    gpio_ns_write(FLASHER_START_PIN, "0")
    time.sleep(0.25)
    busy_pin_state = gpio_ns_read(FLASHER_BUSY_PIN)

    if DEBUG_MODE:
        print "Busy Pin: %d" % busy_pin_state

    while (busy_pin_state):
        if DEBUG_MODE:
            print "Busy state of pins:"
            print "OK_PIN: %d" % gpio_ns_read(FLASHER_OK_PIN)
            print "BUSY_PIN: %d" % gpio_ns_read(FLASHER_BUSY_PIN)
        busy_pin_state = gpio_ns_read(FLASHER_BUSY_PIN)
        time.sleep(0.1)

    time.sleep(0.25)

    # TODO: check if this is correct
    flasher_ok_state = gpio_ns_read(FLASHER_OK_PIN)
    if flasher_ok_state == "0":
        if DEBUG_MODE:
            print "flasher_ok_state (str): %s" % flasher_ok_state
        programming_success = True        
    elif flasher_ok_state == 0:
        if DEBUG_MODE:
            print "flasher_ok_state (str): %s" % flasher_ok_state        
        programming_success = True

    if DEBUG_MODE:
        print "Programming Complete"
        print "Complete state of pins:"
        print "OK_PIN: %d" % flasher_ok_state
        print "BUSY_PIN: %d" % gpio_ns_read(FLASHER_BUSY_PIN)

    return programming_success


def setGpioPin(bcm_pin):
    gpio_ns_write(bcm_pin, "1")

def clearGpioPin(bcm_pin):
    gpio_ns_write(bcm_pin, "0")

def configureGpioPin(bcm_pin, configType):
    gpio_ns_pull(bcm_pin, configType)

def enterTestModeSequence():

    print "Configuring GPIO pins for entering test mode sequence..."
    gpio_ns_config(MFG_TRIG_PIN, "out")
    print "MFG_TRIG_PIN: %d" % gpio_ns_read(MFG_TRIG_PIN)
    gpio_ns_config(MFG_TOGGLE_PIN, "in")  # This is not used, so it can be left as an output.
    print "MFG_TOGGLE_PIN: %d" % gpio_ns_read(MFG_TOGGLE_PIN)
    gpio_ns_config(MFG_INFO_PIN, "out")
    print "MFG_INFO_PIN: %d" % gpio_ns_read(MFG_INFO_PIN)


    # reset device
    # configure pins for entering test mode 
    # TRIG = 0
    # TOGGLE =     configureSuccessReset = resetDUT()

    resetDUT()
    # Pause between tests in debug mode
    if DEBUG_MODE:
        choice = raw_input("Hit 'Enter' to continue: ")
        print ""

    # Sleep for 0.25 seconds.
    time.sleep(0.25)

    #Set info pin low
    print "Set INFO pin low"
    gpio_ns_write(MFG_INFO_PIN, GPIO_LO)
    print "MFG_INFO_PIN: %d" % gpio_ns_read(MFG_INFO_PIN)

    # Turn on power to DUT
    turnOnDUT()

    #Set TRIG pin hi
    print "Set TRIG pin high"
    gpio_ns_write(MFG_TRIG_PIN, GPIO_HI)
    print "MFG_TRIG_PIN: %d" % gpio_ns_read(MFG_TRIG_PIN)

    # Sleep for 0.5 seconds to let device sleep and wait for next TRIG high edge.
    time.sleep(0.5)

    # Wake up the device by setting TRIG high before the watchdog times out.
    toggleButton("", "")

    # Reconfigure the INFO pin as a UART RX to receive UART data from the device.
    gpio_ns_pull(MFG_INFO_PIN, "alt0")


def rotatingPlateIsInCorrectPosition(internalSerialNumber=""):
    """
    For SAM project's module ATE, check the position of the rotating plate position.
    The third character of the serial number determines the position of encoder.
    If the position doesn't match the serial number, do not run tests and prompt
    the operator to set the plate to the correct orientation.
    """

    isCorrectPosition = False
    # Configure GPIO pins to inputs and read the value.
    # Compare if equal 
    a0 = gpio_ns_read(ENCODER_A0)
    a1 = gpio_ns_read(ENCODER_A1)
    a2 = gpio_ns_read(ENCODER_A2)

    encoderOutput = str(a2) + str(a1) + str(a0)
    encoderOutput = str(int(encoderOutput, 2))

    print "Encoder output is " + encoderOutput

    if encoderOutput == subeyeLocations[internalSerialNumber[4]]:
        print "Rotating plate is in correct orientation"
        isCorrectPosition = True
    else:
        print "Rotating plate is not in correct orientation"
        print "Set the plate to position " + internalSerialNumber[4]

    return isCorrectPosition

def activatePusherPistions():
    gpio_ns_write(PUSH1_ACTUATOR, GPIO_HI)
    gpio_ns_write(PUSH2_ACTUATOR, GPIO_HI)
    gpio_ns_write(PUSH3_ACTUATOR, GPIO_HI)

def deactivatePusherPistons():
    gpio_ns_write(PUSH1_ACTUATOR, GPIO_LO)
    gpio_ns_write(PUSH2_ACTUATOR, GPIO_LO)
    gpio_ns_write(PUSH3_ACTUATOR, GPIO_LO)
