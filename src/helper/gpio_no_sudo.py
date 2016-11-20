#!/usr/bin/env python

import sys
sys.path.append("/home/pi/misfit/ShineProduction/src/")
import wiringpi2
import time
from multiprocessing import Process
from subprocess import call
from constants import *
from pprint import pprint


# used to check if requested pin is out of range
def _check_pin_error(bcm_pin):
	if (bcm_pin < 2 or bcm_pin > 27):		
		print "\nError: pin %s is out of range\n" % bcm_pin
		# raise InputError('Pin out of range')

# used to read the value of a pin
def gpio_ns_read(bcm_pin):
	_check_pin_error(bcm_pin)
	return wiringpi2.digitalRead(bcm_pin)
	time.sleep(GP_DELAY_TIME);

# only use this function in its own thread
# should only be called from write_gpio()
def __process_write_gpio(bcm_pin, value):
	if value == "1":
		wiringpi2.digitalWrite(bcm_pin, 1)
	else:
		wiringpi2.digitalWrite(bcm_pin, 0)
	time.sleep(GP_DELAY_TIME);

# this function is used to setup the thread for gpio writes
# use this one from python code
def gpio_ns_write(bcm_pin, value):
	_check_pin_error(bcm_pin)
	p = Process(target=__process_write_gpio, args=(bcm_pin, value))
	p.start()
	p.join()

# this is the initailization function
# configures 4 wire comm between shine and raspi
# configures power pin
def gpio_ns_init():
	call(["gpio", "drive", str(PADS_0_TO_27), str(GPIO_DRIVE_STRENGTH_PADS_0_TO_27)]) #configure the output drive strength of the gpio - this is needed for the level translator
	call(["gpio", "export", str(VOLTAGE_TEST_PIN), "out"])		#configure bcm pin 4 as an output - Voltage Test
	call(["gpio", "export", str(MFG_TRIG_PIN), "out"])				#configure bcm pin 17 as an output - MFG Test
	call(["gpio", "export", str(MFG_TOGGLE_PIN), "in"])		#configure bcm pin 22 as an input  - Toggle/Continue
	call(["gpio", "export", str(POWER_PIN), "out"])				#configure bcm pin 24 as an output.
	call(["gpio", "export", str(FIXTURE_CLOSED_PIN), "in"])				#configure bcm pin 2 as an input - Fixture Closed

	call(["gpio", "export", str(FLASHER_OK_PIN), "in"])			#configure bcm pin 7 as an input - Flasher Programmer OK
	call(["gpio", "export", str(FLASHER_BUSY_PIN), "in"])		#configure bcm pin 8 as an input - Flasher Programmer Busy
	call(["gpio", "export", str(FLASHER_START_PIN), "out"])		#configure bcm pin 25 as an output - Flasher Programmer Start
	call(["gpio", "export", str(IN_JTAG_VCC_CTL), "out"])		#configure bcm pin 11 as an output - Flasher Programmer Start
	call(["gpio", "export", str(IN_MFG_INFO_CTL), "out"])		#configure bcm pin 10 as an output - UART RX 
	call(["gpio", "export", str(POGOPIN_TEST_PIN), "out"])		#configure bcm pin 5 as an output - Pogo Pin Test Pin
	call(["gpio", "export", str(POGOPIN_RELAY_PIN), "out"])		#configure bcm pin 6 as an output - Pogo Pin Test Pin

	time.sleep(GP_DELAY_TIME);
	call(["gpio", "-g", "mode", str(MFG_TOGGLE_PIN), "up"])	#configure bcm pin 22 to have a pull up resistor
	call(["gpio", "-g", "mode", str(FLASHER_OK_PIN), "up"])		#configure bcm pin 7 to have a pull up resistor
	call(["gpio", "-g", "mode", str(FLASHER_BUSY_PIN), "up"])	#configure bcm pin 8 to have a pull up resistor
	call(["gpio", "-g", "mode", str(MFG_INFO_PIN), "alt0"])	#configure bcm pin 15 to be a UART Rx

	call(["gpio", "export", str(ENCODER_A0), "in"])			#configure bcm pin 16 as an input - Encoder A0
	call(["gpio", "export", str(ENCODER_A1), "in"])			#configure bcm pin 20 as an input - Encoder A1
	call(["gpio", "export", str(ENCODER_A2), "in"])			#configure bcm pin 21 as an input - Encoder A2
	call(["gpio", "export", str(PUSH1_ACTUATOR), "out"])		#configure bcm pin 13 as an output - Actuate piston for PUSH1
	call(["gpio", "export", str(PUSH2_ACTUATOR), "out"])		#configure bcm pin 19 as an output - Actuate piston for PUSH2
	call(["gpio", "export", str(PUSH3_ACTUATOR), "out"])		#configure bcm pin 26 as an output - Actuate piston for PUSH3

	
	call(["gpio", "export", str(CRYSTAL_CAL_PIN), "out"])		#configure bcm pin 26 as an output - Actuate piston for PUSH3

	# set the actuator pins to low.
	gpio_ns_write(PUSH1_ACTUATOR, 0)
	gpio_ns_write(PUSH2_ACTUATOR, 0)
	gpio_ns_write(PUSH3_ACTUATOR, 0)

	gpio_ns_write(POWER_PIN, 1) #initialize pin to 1 since the power is active low.
	time.sleep(GP_DELAY_TIME);
	wiringpi2.wiringPiSetupSys()			#setup gpio to work with no sudo. must be called after 'gpio export' and 'gpio mode' calls
	time.sleep(GP_DELAY_TIME);
	time.sleep(GP_DELAY_TIME);
	time.sleep(GP_DELAY_TIME);

# setup pull resistor
# mode = "up", for pullup
# mode = "down", for pulldown
# mode = "tri", for pulls disabled
def gpio_ns_pull(bcm_pin, mode):
	_check_pin_error(bcm_pin)
	call(["gpio", "-g", "mode", str(bcm_pin), mode])
	time.sleep(GP_DELAY_TIME);

# release all gpio
def gpio_ns_release():
	call(["gpio", "unexportall"])		#return gpio to raspi
	time.sleep(GP_DELAY_TIME)


def gpio_ns_config(bcm_pin, ioType):
	if ioType == "in" or ioType == "out":
		call(["gpio", "export", str(bcm_pin), ioType])
		time.sleep(GP_DELAY_TIME)
	else:
		print "Invalid GPIO configuration"



		
